import math
import glob
import random

import pygame

import player
import entity
import light

import camera
import helpers

import ImageLoader

class World:

    def __init__(self):
        self.camera = camera.Camera(pygame.Vector2())

        self.player_sprite = player.Player(pygame.Vector2(250, 250))
        self.player_group = pygame.sprite.GroupSingle(self.player_sprite)

        self.player_headlight = light.Light(pygame.Vector2(helpers.WIDTH / 2, helpers.HEIGHT / 2))
        self.light_group = pygame.sprite.Group(self.player_headlight)
        self.player_sprite.add_child(self.player_headlight)

        # Later the monsters will be placed intentionally, random locations for now to test
        im1 = ImageLoader.ImageLoader.GetImage("assets/imgs/Humanoid1.png", alpha=True)
        im2 = ImageLoader.ImageLoader.GetImage("assets/imgs/Humanoid2.png", alpha=True)
        self.other_entity_group = pygame.sprite.Group()
        for _ in range(50):
            humanoid = entity.TwoFaced(pygame.Vector2(random.randint(16, 1264), random.randint(16, 704)), im1, im2)
            self.other_entity_group.add(humanoid)

        self.world_background = ImageLoader.ImageLoader.GetImage("assets/imgs/test_game_world.png")

        self.fog_timer = 0
        self.sound_timer = 0

        # self.create_fog_images()
        self.init_sounds()

    def init_sounds(self) -> None:
        # TODO: Compress these to mp3 to save space
        pygame.mixer.init()
        self.sound_library = {}

        path_start = "assets/sound/"
        for fname in glob.iglob(path_start + "*.mp3"):
            sound_name = fname[len(path_start):-4]
            self.sound_library[sound_name] = pygame.mixer.Sound(fname)

    def create_fog_images(self):
        # Create images that will be used to mask the screen and obscure the players' vision
        self.fog_image = pygame.Surface(helpers.SCREEN_SIZE, pygame.SRCALPHA)
        self.fog_image.fill((0, 0, 0))
        view_image = pygame.Surface(helpers.SCREEN_SIZE, pygame.SRCALPHA)
        pygame.draw.circle(view_image, (255, 255, 255, 5), helpers.CENTER, 400 - self.fog_timer)
        pygame.draw.circle(view_image, (255, 255, 255, 127), helpers.CENTER, 200 - self.fog_timer)
        pygame.draw.circle(view_image, (255, 255, 255, 255), helpers.CENTER, 175 - self.fog_timer)
        light_rect = self.player_headlight.rect.copy()
        light_rect.center = helpers.CENTER
        view_image.blit(self.player_headlight.image, light_rect)
        self.fog_image.blit(view_image, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    def handle_input(self):
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

    def update(self, delta):
        self.player_group.update(acceleration=self.player_acceleration, rotation=self.player_rotation, delta=delta)
        self.light_group.update(delta)

        for other_entity in self.other_entity_group:
            other_entity.move_towards_point(self.player_sprite.position, delta)
            other_entity.update(pygame.Vector2(), 0, delta)
            visible = self.player_headlight.in_light(other_entity.position)
            other_entity.visible = visible
        
        test_sprite = pygame.sprite.Sprite()
        test_sprite.rect = pygame.Rect(0, 0, 32, 32)
        test_sprite.rect.center = self.player_sprite.rect.center
        if (collided_enemy := pygame.sprite.spritecollideany(test_sprite, self.other_entity_group)) is not None:
            hurt_noises = [key for key in self.sound_library if "player_hurt" in key]
            sound_choice = random.choice(hurt_noises)
            self.sound_library[sound_choice].play()

            self.player_sprite.velocity = pygame.Vector2()
            collided_enemy.kill()

        self.camera.position = self.player_sprite.position
        self.fog_timer += delta

        self.sound_timer -= delta
        if self.sound_timer < 0:
            ambient_noises = [key for key in self.sound_library if "voice" in key]
            sound_choice = random.choice(ambient_noises)
            self.sound_library[sound_choice].play()
            self.sound_timer += 5

    def draw_group_offset(self, group, surface):
        """Draw the entities in a group relative to the camera"""
        for entity in group:
            new_pos = self.camera.world_to_screen(entity.position)
            new_rect = entity.rect.copy()
            new_rect.center = new_pos
            surface.blit(entity.image, new_rect)

    def draw(self, surface):
        self.create_fog_images()
        surface.blit(self.world_background, self.camera.world_to_screen(pygame.Vector2()))
        self.draw_group_offset(self.other_entity_group, surface)
        self.draw_group_offset(self.player_group, surface)
        self.draw_group_offset(self.light_group, surface)

        surface.blit(self.fog_image, (0, 0))