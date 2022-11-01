from ast import literal_eval
from lzma import is_check_supported
import math
import glob
import random

import pygame

import player
import entity
import light
import creature

import camera
import helpers

from gametools import ImageLoader

class World:

    def __init__(self):
        self.camera = camera.Camera(pygame.Vector2())

        self.player_sprite = player.Player(pygame.Vector2(250, 250), self)
        self.player_group = pygame.sprite.GroupSingle(self.player_sprite)

        self.player_headlight = light.Light(pygame.Vector2(helpers.WIDTH / 2, helpers.HEIGHT / 2), self)
        self.light_group = pygame.sprite.Group(self.player_headlight)
        self.player_sprite.add_child(self.player_headlight)

        self.world_background = ImageLoader.ImageLoader.GetImage("assets/imgs/TheMap.png")
        self.world_mask_img = ImageLoader.ImageLoader.GetImage("assets/imgs/TheMapMask.png")
        self.world_mask = pygame.mask.from_threshold(self.world_mask_img, (0, 0, 0, 255), threshold=(10, 10, 10, 255))

        self.other_entity_group = pygame.sprite.Group()
        # Later the monsters will be placed intentionally, random locations for now to test
        with open("mapdata.txt") as f:
            for line in f:
                prop_type, prop_coord = literal_eval(line)
                if prop_type == 'Creature':
                    coord = pygame.Vector2(prop_coord)
                    creature_sprite = creature.Creature(coord, self)
                    self.other_entity_group.add(creature_sprite)

        self.scenery_entities = pygame.sprite.Group()
        self.player_scenery_sprite = None
        self.bike_scenery_sprite = None
        self.player_in_animation = False

        self.fog_timer = 0
        self.sound_timer = 0

        self.grandma_position = pygame.Vector2(6755, 3268)
        self.grandma_image = ImageLoader.ImageLoader.GetImage("assets/imgs/Props/Grandma.png")
        self.grandma_entity = entity.SceneryEntity(self.grandma_position, self.grandma_image, self)
        self.scenery_entities.add(self.grandma_entity)

        # self.player_sprite.position.update(self.grandma_position)

        self.init_sounds()

        self.won = False

    def init_sounds(self) -> None:
        """Load sounds from the disc and create our library of sounds"""
        pygame.mixer.init()
        self.sound_library: dict[str, pygame.mixer.Sound] = {}

        path_start = "assets/sound/"
        for fname in glob.iglob(path_start + "*.ogg"):
            sound_name = fname[len(path_start):-4]
            self.sound_library[sound_name] = pygame.mixer.Sound(fname)

        # Create some lists of the keys ahead of time if we want to play from a random subset of sounds
        self.hurt_noises = [key for key in self.sound_library if "player_hurt" in key]
        self.ambient_noises = [key for key in self.sound_library if "voice" in key]

    def create_fog_images(self) -> None:
        """Create images that will be used to mask the screen and obscure the players' vision"""

        # self.fog_image will act as a mask, and we will subtract from it what the player CAN see
        self.fog_image = pygame.Surface(helpers.SCREEN_SIZE, pygame.SRCALPHA)
        self.fog_image.fill((0, 0, 0))

        # Draw the shrinking ambient light
        view_image = pygame.Surface(helpers.SCREEN_SIZE, pygame.SRCALPHA)
        pygame.draw.circle(view_image, (255, 255, 255, 5), helpers.CENTER, 400 - self.fog_timer)
        pygame.draw.circle(view_image, (255, 255, 255, 127), helpers.CENTER, 200 - self.fog_timer)
        pygame.draw.circle(view_image, (255, 255, 255, 255), helpers.CENTER, 175 - self.fog_timer)

        # Add player light to view image
        light_rect = self.player_headlight.rect.copy()
        light_rect.center = helpers.CENTER
        view_image.blit(self.player_headlight.image, light_rect)

        # Wanted to get just the eyes to show, TODO: Fix glow
        # for sprite in self.other_entity_group:
        #     new_rect = sprite.rect.copy()
        #     new_rect.center = self.camera.world_to_screen(pygame.Vector2(new_rect.center))
        #     view_image.blit(sprite.image, new_rect)

        self.fog_image.blit(view_image, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    def handle_input(self) -> None:
        """Handle input of the player holding down keys or buttons"""
        self.player_acceleration = pygame.Vector2()
        self.player_rotation = 0

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_a]:
            # Rotate clockwise one rad/s
            self.player_rotation += helpers.RAD_TO_DEG
        if pressed_keys[pygame.K_d]:
            self.player_rotation -= helpers.RAD_TO_DEG 
        if pressed_keys[pygame.K_w]:
            self.player_acceleration.y += 100
        if pressed_keys[pygame.K_s]:
            self.player_acceleration.y -= 100

        # If the player was knocked off their bike, they can run over to it and get back on with SPACE
        if pressed_keys[pygame.K_SPACE]:
            if self.bike_scenery_sprite is not None:
                distance = (self.bike_scenery_sprite.position - self.player_sprite.position).magnitude_squared()
                if distance < 32 * 32:
                    self.player_sprite.on_bike = True
                    self.bike_scenery_sprite.kill()
                    self.bike_scenery_sprite = None
                    self.player_sprite.set_animation('biking')

    def update(self, delta: float) -> None:
        """Update the position and states of all entities in the game"""

        # Player objects, if the player is in an animation don't update their normal class
        self.scenery_entities.update(delta)
        if self.player_scenery_sprite is not None:
            self.player_in_animation = True
            self.player_sprite.position = self.player_scenery_sprite.position.copy()
            self.player_headlight.position = self.bike_scenery_sprite.position.copy()
            if self.player_scenery_sprite.done_status:
                self.player_scenery_sprite.kill()
                self.player_scenery_sprite = None
        else:
            # First start with the player and their light sources
            self.player_group.update(acceleration=self.player_acceleration, rotation=self.player_rotation, delta=delta)
            self.player_in_animation = False

            # The player wins if they get close enough to grandma
            if (self.grandma_position - self.player_sprite.position).length_squared() < 80 * 80:
                self.other_entity_group.empty()
                self.won = True
            # self.lock_to_mask(self.world_mask_img)

        # Light
        self.light_group.update(delta)

        player_collision_radius = 16
        enemy_collision_radius = 16

        # Update every monster or other entity.
        for other_entity in self.other_entity_group:
            player_offset: pygame.Vector2 = self.player_sprite.position - other_entity.position
            player_offset_normalize = player_offset.normalize()

            other_entity.update(delta)
            visible = self.player_headlight.in_light(other_entity.position)
            other_entity.visible = visible

            if not self.player_in_animation and player_offset.magnitude_squared() < (player_collision_radius + enemy_collision_radius) ** 2:
                if not self.player_sprite.on_bike:
                    # Player loses if they are hit by a monster while knocked off their bike
                    self.player_sprite.kill()
                    return
                    
                sound_choice = random.choice(self.hurt_noises)
                self.sound_library[sound_choice].play()

                self.player_sprite.on_bike = False
                other_entity.kill()

                self.player_scenery_sprite = entity.SceneryEntity(self.player_sprite.position.copy(), None, self)
                dist = 100
                player_target = self.player_sprite.position + player_offset_normalize * dist
                while not self.is_coord_in_mask(player_target):
                    dist /= 2
                    player_target = self.player_sprite.position + player_offset_normalize * dist
                self.player_scenery_sprite.add_keyframe(player_target, 2.0)
                self.player_scenery_sprite.add_animation('falling', self.player_sprite.animations['falling'])
                self.player_scenery_sprite.set_animation('falling')
                self.scenery_entities.add(self.player_scenery_sprite)
                
                bike_img = ImageLoader.ImageLoader.GetImage("assets/imgs/bike.png")
                self.bike_scenery_sprite = entity.SceneryEntity(self.player_sprite.position.copy(), bike_img, self)
                dist = 100
                bike_target = self.player_sprite.position - player_offset_normalize * dist
                while not self.is_coord_in_mask(bike_target):
                    dist /= 2
                    bike_target = self.player_sprite.position - player_offset_normalize * dist
                self.bike_scenery_sprite.add_keyframe(bike_target, 1.5)

                self.scenery_entities.add(self.bike_scenery_sprite)

                self.player_in_animation = True
                self.player_sprite.set_animation('walking')

        self.camera.position = self.player_sprite.position
        self.fog_timer += delta

        # Play ambient sounds from time to time to keep the player on edge
        # TODO: Make the sounds get louder the closer to an enemy you are?
        self.sound_timer -= delta
        if self.sound_timer < 0:
            sound_choice = random.choice(self.ambient_noises)
            self.sound_library[sound_choice].play()
            self.sound_timer += 15

    def lock_to_mask(self, sprite: pygame.sprite.Sprite, movement_vector: pygame.Vector2) -> pygame.Vector2:
        pos = sprite.position
        goal_pos = pos + movement_vector
        if self.is_coord_in_mask(goal_pos):
            return movement_vector
        
        else:
            return pygame.Vector2()
    
    def is_coord_in_mask(self, world_coord: pygame.Vector2):
        try:
            return self.world_mask.get_at(world_coord)
        except IndexError:
            # if the world_coord is off the map
            return False

    def draw_group_offset(self, group: pygame.sprite.Group, surface: pygame.Surface) -> None:
        """Draw the entities in a group relative to the camera"""
        for entity in group:
            new_pos = self.camera.world_to_screen(entity.position)
            new_rect = entity.rect.copy()
            new_rect.center = new_pos
            surface.blit(entity.image, new_rect)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the game world, the entities, and then constrain what the player can see"""
        self.create_fog_images()
        surface.blit(self.world_background, self.camera.world_to_screen(pygame.Vector2()))
        self.draw_group_offset(self.other_entity_group, surface)
        if not self.player_in_animation:
            self.draw_group_offset(self.player_group, surface)
        self.draw_group_offset(self.scenery_entities, surface)
        self.draw_group_offset(self.light_group, surface)

        surface.blit(self.fog_image, (0, 0))