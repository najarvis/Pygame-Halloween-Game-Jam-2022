from __future__ import annotations

import pygame
from state_manager import StateManager
from creature_states import CreatureStateSeeking, CreatureStateWaiting
import world

class Entity(pygame.sprite.Sprite):
    """An entity is an object that is not part of the terrain, and can move and interact with other
    entities.
    """

    next_id = 0

    def __init__(self, position: pygame.Vector2(), base_image: pygame.Surface, world: world.World):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = base_image
        if base_image is None:
            self.base_image = pygame.Surface((32, 32))
        self.image = self.base_image.copy()

        self._position = position
        self.velocity = pygame.Vector2()

        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        self._orientation = 0

        self.speed = 100 # Max speed

        # Store a reference to the world to be able to easily access its data
        self.world = world

        # Whether or not the sprite's image should be re-drawn
        self.dirty = True

        # Children will be locked to their parents
        self.children = []

        # This will be unique to each entity
        self.id = Entity.next_id
        Entity.next_id = self.id + 1

        self.state_manager = StateManager()

        # Animation
        self.load_animations()
        self.time_between_animation_frames = 1/12 # 12 frames / second
        self.animation_timer = self.time_between_animation_frames
        self.animation_index = 0

    def load_animations(self) -> None:
        """Subclasses should overwrite this and load image sequences into 
        self.animations. <c.f. Creature.load_animations>
        """
        
        self.animations = {}
        self.current_animation = None

    def update(self, acceleration: pygame.Vector2, delta: float) -> None:
        """
        Update function called every frame. Updates the entity's position and orientation.

        Units of acceleration: px/s^2
        Units of rotation: degrees/s
        units of delta: s
        """
        self.velocity += acceleration * delta
        if self.velocity.length_squared() > self.speed * self.speed:
            self.velocity.scale_to_length(self.speed)

        self.position += self.velocity * delta

        self.rect.center = self.position

        # self.orientation += rotation * delta
        # Entities now face the direction in which they are moving.
        orientation_vel = pygame.Vector2(self.velocity.x, -self.velocity.y)
        self.orientation = (orientation_vel.as_polar()[1] - 90) % 360

        self.update_children()
        self.update_rect()

    def update_rect(self) -> None:
        """If the position or rotation has changed, this should be called."""
        self.update_image_rotation()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update_image_rotation(self) -> None:
        # Update the sprite's image to correspond with the updated rotation
        if self.dirty:
            self.image = pygame.transform.rotate(self.base_image, self.orientation)

    def update_animation(self, delta: float) -> None:
        if self.current_animation is None:
            return
    
        if self.animation_timer < 0:
            self.animation_timer += self.time_between_animation_frames
            self.animation_index += 1
            self.animation_index %= len(self.current_animation)

        self.base_image = self.current_animation[self.animation_index]
        self.animation_timer -= delta

    def add_animation(self, name: str, image_list: list[pygame.Surface]):
        self.animations[name] = image_list

    def set_animation(self, animation_name):
        if animation_name not in self.animations:
            raise KeyError(f"Animation `{animation_name}` not found in list")

        self.current_animation = self.animations[animation_name]
        self.animation_index = 0
        self.animation_timer = self.time_between_animation_frames
        self.dirty = True

    def add_child(self, other_entity: Entity) -> None:
        self.children.append(other_entity)

    def update_children(self) -> None:
        # TODO: Keep the offsets to the children consistent rather than copying the position and orientation
        for child in self.children:
            child.position = self.position
            child.orientation = self.orientation
            child.update_rect()

    def move_towards_point(self, point, delta) -> None:
        """Move an entity towards a point."""

        direction = point - self.position
        #self.position += direction.normalize() * self.speed * delta
        self.velocity += direction.normalize() * delta * self.speed # Add to the velocity instead of the position to mimic some acceleration
        self.update_rect()

    """Properties"""

    def get_orientation(self) -> float:
        return self._orientation

    def set_orientation(self, new_orientation: float) -> None:
        if new_orientation != self._orientation:
            self._orientation = new_orientation % 360
            self.dirty = True

    # This is in DEGREES
    orientation = property(get_orientation, set_orientation)

    def get_position(self):
        return self._position

    def set_position(self, new_position: pygame.Vector2) -> None:
        # NOTE: This does NOT get called if a component of position is changed (i.e. pos.x += 1)
        if new_position != self._position:
            self._position = new_position
            self.dirty = False

    position = property(get_position, set_position)

class TwoFaced(Entity):
    """Playing on the theme idea, TwoFaced is an entity with two forms, with
    the true form only being revealed in the light.
    """

    def __init__(self, position: pygame.Vector2, im1: pygame.Surface, im2: pygame.Surface):
        Entity.__init__(self, position, im1)
        self.image1 = im1
        self.image2 = im2
        self._visible = False
        self.base_speed = self.speed

    def get_visible(self):
        return self._visible

    def set_visible(self, visible: bool):
        self._visible = visible
        new_base_image = self.image2 if visible else self.image1
        if new_base_image != self.base_image:
            self.base_image = new_base_image
            self.dirty = True
            self.update_rect()

        self.speed = 0 if self._visible else self.base_speed

    visible = property(get_visible, set_visible)

class SceneryEntity(Entity):
    """An entity meant to not interact with other entities, but to
    follow keyframes (for animations). If an entity has been started
    and done_status is true, it has likely finished its animation
    (Unless you plan to add more keyframes).
    """

    def __init__(self, position: pygame.Vector, image: pygame.Surface, world: world.World):
        Entity.__init__(self, position, image, world)
        self.timer = 0
        self.keyframes = []
        self.done_status = True
        self.current_goal = None
        self.started = False

    def add_keyframe(self, location: pygame.Vector2, time: float) -> None:
        """Add a location the SE should move towards. time is how long it
        should take to get there
        """

        self.keyframes.append((location, time))

    def get_next_goal(self) -> bool:
        """Updates the entity with the information from the next keyframe.
        Returns False is there are no keyframes.
        """

        if len(self.keyframes) == 0:
            return False
        
        next_keyframe = self.keyframes.pop(0)
        self.current_goal = next_keyframe[0]
        self.timer = next_keyframe[1]
        self.started = True
        return True

    def update(self, delta: float) -> None:
        """Since these aren't acted upon by force, a scenery entity only
        needs the delta to update.
        """
        if self.current_goal is None:
            self.done_status = not self.get_next_goal()
            return

        self.timer -= delta
        if self.timer <= 0:
            self.position = self.current_goal
            self.current_goal = None
            self.timer = 0
        else:
            offset = self.current_goal - self.position
            speed = offset.length() / self.timer 
            if offset.length() > offset.epsilon:
                offset.scale_to_length(speed)
                self.position += offset * delta

        self.update_animation(delta)
        self.update_rect()
            