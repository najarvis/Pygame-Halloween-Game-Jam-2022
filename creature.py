from __future__ import annotations

import glob

import pygame
from creature_states import CreatureStateAttacking, CreatureStateSeeking, CreatureStateWaiting
import entity
import world

from gametools import ImageLoader
import helpers


class Creature(entity.Entity):

    def __init__(self, position: pygame.Vector2, world: world.World):
        entity.Entity.__init__(self, position, None, world)
        self.target: pygame.Vector2 = None

        # States
        waiting_state = CreatureStateWaiting(self, self.world.player_sprite)
        seeking_state = CreatureStateSeeking(self, self.world.player_sprite)
        attacking_state = CreatureStateAttacking(self, self.world.player_sprite)
        self.state_manager.add_state(waiting_state)
        self.state_manager.add_state(seeking_state)
        self.state_manager.add_state(attacking_state)
        self.state_manager.set_state(waiting_state.name)
        self.speed = 1000

    def load_animations(self):
        self.animations = {}
        self.current_animation = None

        path_start = "assets/imgs/Creature/"
        for fname in glob.iglob(path_start + "*.png"):
            ImageLoader.ImageLoader.GetImage(fname, alpha=True) # Cache all the images

        self.animations['idle'] = ImageLoader.ImageLoader.return_image_set("creature_idle", None, True)
        self.animations['death'] = ImageLoader.ImageLoader.return_image_set("creature_death", None, True)
        self.animations['bite'] = ImageLoader.ImageLoader.return_image_set("creature_Bite", None, True)
        self.set_animation('idle')

    def update(self, delta: float) -> None:
        self.state_manager.do_state()

        self.update_animation(delta)
        
        acceleration = pygame.Vector2()
        if self.target is not None:
            target_offset = self.target - self.position
            if target_offset.length_squared() > self.speed * self.speed:
                target_offset.scale_to_length(self.speed)
            acceleration = target_offset - self.velocity
        super().update(acceleration, delta)