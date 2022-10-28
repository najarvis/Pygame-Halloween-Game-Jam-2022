from telnetlib import GA
from turtle import left, st
import pygame

import helpers
import world
import os
from enum import Enum

class GameState(Enum):
    MENU = 1
    GAMING = 2

def run():
    state = GameState.MENU
    menuWidth = 300
    menuHeight = 300
    screen = pygame.display.set_mode(helpers.SCREEN_SIZE)
    pygame.display.set_caption("Spooky game for game jam!")

    clock = pygame.time.Clock()
    done = False

    game_world = world.World()
    mouseCheck = False

    while not done:
        delta = clock.tick(144) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

        if state == GameState.MENU:
            pos = pygame.mouse.get_pos()
            menu_area = pygame.Rect(helpers.WIDTH/2 - menuWidth/2, helpers.HEIGHT/2 - menuHeight/2, menuWidth, menuHeight)
            pygame.draw.rect(screen, (255,0,0), menu_area)
            try:
                #menu_pos = game_world.camera.screen_to_world(pos)
                hovering = menu_area.collidepoint(pos[0], pos[1])
                leftClick = pygame.mouse.get_pressed() == (1,0,0)
                pygame.display.set_caption(f"coord: {pos}, in menu area: {hovering}, mouse pressed? {leftClick}")
                if hovering and leftClick:
                    mouseCheck = True
            except IndexError:
                pygame.display.set_caption(f"coord: {pos} not hovering the menu")

        elif state == GameState.GAMING:
            game_world.handle_input()
            game_world.update(delta)

            if not game_world.player_sprite.alive():
                done = True

            pos = pygame.mouse.get_pos()
            try:
                world_pos = game_world.camera.screen_to_world(pos)
                pygame.display.set_caption(f"coord: {world_pos}, in mask: {game_world.world_mask.get_at(world_pos)}")
            except IndexError:
                pygame.display.set_caption(f"OFF MAP")

            # Background
            screen.fill((50, 25, 15))

            game_world.draw(screen)

        if mouseCheck:
            mouseCheck = False
            state = GameState.GAMING
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()