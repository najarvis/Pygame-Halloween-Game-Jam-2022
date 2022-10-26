import pygame

from state_manager import State

class CreatureStateWaiting(State):

    def __init__(self, creature_sprite: pygame.sprite.Sprite, player_sprite: pygame.sprite.Sprite):
        State.__init__(self, "waiting")
        self.create_sprite = creature_sprite
        self.player_sprite_target = player_sprite
        self.goal_distance = 250 # px

    def entry_actions(self) -> None:
        self.create_sprite.target = None
        self.create_sprite.velocity.update(0, 0)

    def exit_actions(self) -> None:
        pass

    def do_actions(self) -> None:
        pass

    def check_conditions(self) -> str | None:
        offset = self.player_sprite_target.position - self.create_sprite.position
        if offset.length() < self.goal_distance:
            return "seeking"

        return None

class CreatureStateSeeking(State):

    def __init__(self, creature_sprite: pygame.sprite.Sprite, player_sprite: pygame.sprite.Sprite):
        State.__init__(self, "seeking")
        self.create_sprite = creature_sprite
        self.player_sprite_target = player_sprite
        self.goal_distance = 250 # px

    def entry_actions(self) -> None:
        self.create_sprite.target = self.player_sprite_target.position

    def exit_actions(self) -> None:
        pass

    def do_actions(self) -> None:
        pass

    def check_conditions(self) -> str | None:
        offset = self.player_sprite_target.position - self.create_sprite.position
        if offset.length() > self.goal_distance:
            return "waiting"

        return None

class CreatureStateAttacking(State):

    NotImplemented