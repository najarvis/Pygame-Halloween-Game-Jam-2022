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

        self.player_sprite = player.Player(pygame.Vector2(helpers.WIDTH / 2, helpers.HEIGHT / 2))
        self.player_group = pygame.sprite.GroupSingle(self.player_sprite)

        self.player_headlight = light.Light(pygame.Vector2(helpers.WIDTH / 2, helpers.HEIGHT / 2))
        self.light_group = pygame.sprite.Group(self.player_headlight)
        self.player_sprite.add_child(self.player_headlight)

        im1 = ImageLoader.ImageLoader.GetImage("assets/imgs/Humanoid1.png", alpha=True)
        im2 = ImageLoader.ImageLoader.GetImage("assets/imgs/Humanoid2.png", alpha=True)
        self.other_entity_group = pygame.sprite.Group()
        for _ in range(50):
            humanoid = entity.TwoFaced(pygame.Vector2(random.randint(16, 1264), random.randint(16, 704)), im1, im2)
            self.other_entity_group.add(humanoid)

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
            visible = self.player_headlight.in_light(other_entity.position)
            other_entity.visible = visible

        self.camera.position = self.player_sprite.position

    def draw_group_offset(self, group, surface):
        """Draw the entities in a group relative to the camera"""
        for entity in group:
            new_pos = self.camera.world_to_screen(entity.position)
            new_rect = entity.rect.copy()
            new_rect.center = new_pos
            surface.blit(entity.image, new_rect)

    def draw(self, surface):
        self.draw_group_offset(self.other_entity_group, surface)
        self.draw_group_offset(self.player_group, surface)
        self.draw_group_offset(self.light_group, surface)