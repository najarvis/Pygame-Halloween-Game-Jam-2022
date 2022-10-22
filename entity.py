import pygame
import random

class Entity(pygame.sprite.Sprite):

    next_id = 0

    def __init__(self, position: pygame.Vector2(), base_image: pygame.Surface):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = base_image
        self.image = self.base_image.copy()

        self._position = position
        self.velocity = pygame.Vector2()

        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        self._orientation = 0

        self.speed = random.uniform(9, 11)

        self.dirty = True
        self.children = []
        self.id = Entity.next_id
        Entity.next_id = self.id + 1

    def update(self, acceleration: pygame.Vector2(), rotation: float, delta: float):
        """Units of acceleration: units/s^2
        Units of rotation: rads/s
        units of delta: s
        """
        self.velocity += acceleration * delta
        self.position += self.velocity * delta

        self.rect.center = self.position

        self.orientation += rotation * delta

        self.update_children()
        self.update_rect()

    def update_rect(self):
        """If the position or rotation has changed, this should be called."""
        self.update_image_rotation()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update_image_rotation(self):
        if self.dirty:
            self.image = pygame.transform.rotate(self.base_image, self.orientation)

    def add_child(self, other_entity):
        self.children.append(other_entity)

    def update_children(self):
        for child in self.children:
            child.position = self.position
            child.orientation = self.orientation
            child.update_rect()

    def move_towards_point(self, point, delta):
        direction = point - self.position
        self.position += direction.normalize() * self.speed * delta
        self.update_rect()

    """Properties"""

    def get_orientation(self):
        return self._orientation

    def set_orientation(self, new_orientation):
        if new_orientation != self._orientation:
            self._orientation = new_orientation % 360
            self.dirty = True

    # This is in DEGREES
    orientation = property(get_orientation, set_orientation)

    def get_position(self):
        return self._position

    def set_position(self, new_position):
        if new_position != self._position:
            self._position = new_position
            self.dirty = False

    position = property(get_position, set_position)

class TwoFaced(Entity):

    def __init__(self, position, im1, im2):
        Entity.__init__(self, position, im1)
        self.image1 = im1
        self.image2 = im2
        self._visible = False
        self.base_speed = self.speed

    def get_visible(self):
        return self._visible

    def set_visible(self, visible):
        self._visible = visible
        new_base_image = self.image2 if visible else self.image1
        if new_base_image != self.base_image:
            self.base_image = new_base_image
            self.dirty = True
            self.update_rect()

        self.speed = 0 if self._visible else self.base_speed


    visible = property(get_visible, set_visible)