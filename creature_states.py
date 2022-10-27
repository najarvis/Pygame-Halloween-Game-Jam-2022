import pygame

from state_manager import State

ENGAGE_DISTANCE = 50
SEEK_DISTANCE = 300
class CreatureStateWaiting(State):

    def __init__(self, creature_sprite: pygame.sprite.Sprite, player_sprite: pygame.sprite.Sprite):
        State.__init__(self, "waiting")
        self.creature_sprite = creature_sprite
        self.player_sprite_target = player_sprite

    def entry_actions(self) -> None:
        self.creature_sprite.set_animation('idle')
        self.creature_sprite.target = None
        self.creature_sprite.velocity.update(0, 0)

    def exit_actions(self) -> None:
        pass

    def do_actions(self) -> None:
        pass

    def check_conditions(self) -> str | None:
        offset = self.player_sprite_target.position - self.creature_sprite.position
        if offset.length() < SEEK_DISTANCE:
            return "seeking"

        return None

class CreatureStateSeeking(State):

    def __init__(self, creature_sprite: pygame.sprite.Sprite, target_sprite: pygame.sprite.Sprite):
        State.__init__(self, "seeking")
        self.creature_sprite = creature_sprite
        self.target_sprite = target_sprite

    def entry_actions(self) -> None:
        self.creature_sprite.set_animation('idle')
        self.creature_sprite.target = self.target_sprite.position.copy()

    def exit_actions(self) -> None:
        pass

    def do_actions(self) -> None:
        self.creature_sprite.target = self.target_sprite.position.copy()

    def check_conditions(self) -> str | None:
        offset = self.target_sprite.position - self.creature_sprite.position
        dist = offset.length()
        if dist > SEEK_DISTANCE:
            return "waiting"

        if dist < ENGAGE_DISTANCE:
            return "attacking"

        return None

class CreatureStateAttacking(State):

    def __init__(self, creature_sprite: pygame.sprite.Sprite, target_sprite: pygame.sprite.Sprite):
        State.__init__(self, "attacking")
        self.creature_sprite = creature_sprite
        self.target_sprite = target_sprite
    
    def entry_actions(self) -> None:
        self.creature_sprite.set_animation('bite')
        self.creature_sprite.target = self.target_sprite.position.copy()

    def exit_actions(self) -> None:
        pass

    def do_actions(self) -> None:
        self.creature_sprite.target = self.target_sprite.position.copy()

    def check_conditions(self) -> str | None:
        offset = self.target_sprite.position - self.creature_sprite.position
        dist = offset.length()
        if dist > ENGAGE_DISTANCE:
            return "waiting"

        return None