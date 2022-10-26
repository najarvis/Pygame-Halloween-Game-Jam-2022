from __future__ import annotations

import glob

import pygame
from creature_states import CreatureStateSeeking, CreatureStateWaiting
import entity
import world

from gametools import ImageLoader


class Creature(entity.Entity):

    def __init__(self, position: pygame.Vector2, world: world.World):
        # Animation
        self.load_animations()
        self.time_between_animation_frames = 1/12 # 12 frames / second
        self.animation_timer = self.time_between_animation_frames
        self.animation_index = 0

        creature_image = self.current_animation[self.animation_index]
        entity.Entity.__init__(self, position, creature_image, world)
        self.target: pygame.Vector2 = None

        # States
        waiting_state = CreatureStateWaiting(self, self.world.player_sprite)
        seeking_state = CreatureStateSeeking(self, self.world.player_sprite)
        self.state_manager.add_state(waiting_state)
        self.state_manager.add_state(seeking_state)
        self.state_manager.set_state(waiting_state.name)

    def load_animations(self):
        self.animations = {}
        self.current_animation = None

        path_start = "assets/imgs/Creature/"
        for fname in glob.iglob(path_start + "*.png"):
            ImageLoader.ImageLoader.GetImage(fname, alpha=True) # Cache all the images

        self.animations['idle'] = ImageLoader.ImageLoader.return_image_set("creature_idle", None, True)
        self.animations['death'] = ImageLoader.ImageLoader.return_image_set("creature_death", None, True)
        self.current_animation = self.animations['idle']

    def update(self, delta: float) -> None:
        self.state_manager.do_state()

        if self.animation_timer < 0:
            self.animation_timer += self.time_between_animation_frames
            self.animation_index += 1
            self.animation_index %= len(self.current_animation)
            self.base_image = self.current_animation[self.animation_index]

        self.animation_timer -= delta
        
        acceleration = pygame.Vector2()
        if self.target is not None:
            target_offset = self.target - self.position
            acceleration = target_offset.normalize() * 100
        super().update(acceleration, 0, delta)