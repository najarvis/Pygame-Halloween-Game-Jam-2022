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

        # Later the monsters will be placed intentionally, random locations for now to test
        # im1 = ImageLoader.ImageLoader.GetImage("assets/imgs/Humanoid1.png", alpha=True)
        # im2 = ImageLoader.ImageLoader.GetImage("assets/imgs/Humanoid2.png", alpha=True)
        creature_sprite = creature.Creature(pygame.Vector2(helpers.CENTER), self)
        self.other_entity_group = pygame.sprite.Group(creature_sprite)
        # for _ in range(1):
        #     humanoid = entity.TwoFaced(pygame.Vector2(helpers.CENTER), im1, im2)
        #     self.other_entity_group.add(humanoid)

        self.scenery_entities = pygame.sprite.Group()
        self.player_scenery_sprite = None
        self.bike_scenery_sprite = None
        self.player_in_animation = False

        self.world_background = ImageLoader.ImageLoader.GetImage("assets/imgs/test_game_world.png")

        self.fog_timer = 0
        self.sound_timer = 0

        # self.create_fog_images()
        self.init_sounds()

    def init_sounds(self) -> None:
        """Load sounds from the disc and create our library of sounds"""
        pygame.mixer.init()
        self.sound_library = {}

        path_start = "assets/sound/"
        for fname in glob.iglob(path_start + "*.mp3"):
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

    def update(self, delta: float) -> None:
        """Update the position and states of all entities in the game"""

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
        self.light_group.update(delta)

        player_collision_radius = 16
        enemy_collision_radius = 16

        # Update every monster or other entity.
        for other_entity in self.other_entity_group:
            #other_entity.move_towards_point(self.player_sprite.position, delta)
            player_offset = self.player_sprite.position - other_entity.position
            player_offset_normalize = player_offset.normalize()
            #enemy_acceleration = player_offset.normalize() * 100 # Accelerate towards the player at 100px/s^2
            other_entity.update(delta)
            visible = self.player_headlight.in_light(other_entity.position)
            other_entity.visible = visible

            if not self.player_in_animation and (player_offset).magnitude_squared() < (player_collision_radius + enemy_collision_radius) ** 2:
                sound_choice = random.choice(self.hurt_noises)
                self.sound_library[sound_choice].play()

                # TODO: When player gets hit, deactivate the player, spawn a dummy sprite object that represents
                # the player getting yeeted back, and once they land, reposition and reactivate the player. 
                # Avoids the messiness of the player moving while getting launched. 
                self.player_sprite.on_bike = False
                other_entity.kill()

                player_img = ImageLoader.ImageLoader.GetImage("assets/imgs/player.png", alpha=True)
                bike_img = ImageLoader.ImageLoader.GetImage("assets/imgs/bike.png")
                self.player_scenery_sprite = entity.SceneryEntity(self.player_sprite.position.copy(), player_img, self)
                self.player_scenery_sprite.add_keyframe(self.player_sprite.position + player_offset_normalize * 100, 2.0)
                self.scenery_entities.add(self.player_scenery_sprite)
                
                self.bike_scenery_sprite = entity.SceneryEntity(self.player_sprite.position.copy(), bike_img, self)
                self.bike_scenery_sprite.add_keyframe(self.player_sprite.position - player_offset_normalize * 100, 1.5)
                self.scenery_entities.add(self.bike_scenery_sprite)
                self.player_in_animation = True

        self.camera.position = self.player_sprite.position
        self.fog_timer += delta

        # Play ambient sounds from time to time to keep the player on edge
        # TODO: Make the sounds get louder the closer to an enemy you are?
        self.sound_timer -= delta
        if self.sound_timer < 0:
            sound_choice = random.choice(self.ambient_noises)
            self.sound_library[sound_choice].play()
            self.sound_timer += 15

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