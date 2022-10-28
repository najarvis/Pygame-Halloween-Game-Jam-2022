import pygame

import helpers
import world
import os
from enum import Enum

class GameState(Enum):
    MENU = 1
    GAMING = 2
    WIN = 3

def run():
    state = GameState.MENU
    menuWidth = 300
    menuHeight = 150
    screen = pygame.display.set_mode(helpers.SCREEN_SIZE)
    pygame.display.set_caption("Spooky game for game jam!")

    clock = pygame.time.Clock()
    done = False

    game_world = None
    win_timer = 5

    while not done:
        delta = clock.tick(144) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

        if state == GameState.MENU:
            screen.fill((0, 0, 0))
            pos = pygame.mouse.get_pos()
            menu_area = pygame.Rect(helpers.WIDTH/2 - menuWidth/2, helpers.HEIGHT/2 - menuHeight/2, menuWidth, menuHeight)
            hovering = menu_area.collidepoint(*pos)
            pygame.draw.rect(screen, (255,255,255), menu_area, 5 if hovering else 3)

            menu_text = "GET TO GRANDMA"
            menu_text_rendered = helpers.CREEPY_FONT.render(menu_text, True, (255, 255, 255))
            menu_text_rendered_rect = menu_text_rendered.get_rect()
            menu_text_rendered_rect.center = menu_area.center
            screen.blit(menu_text_rendered, menu_text_rendered_rect)

            credits_text = "By Nick Jarvis, John Hata, and Bennett Goertemiller"
            credits_text_rendered = helpers.REGULAR_FONT.render(credits_text, True, (255, 255, 255))
            credits_text_rendered_rect = credits_text_rendered.get_rect()
            credits_text_rendered_rect.center = (helpers.CENTER_X, helpers.HEIGHT - 25)
            screen.blit(credits_text_rendered, credits_text_rendered_rect)

            leftClick = pygame.mouse.get_pressed() == (1,0,0)
            if hovering and leftClick:
                state = GameState.GAMING
                game_world = world.World()

        elif state == GameState.GAMING:
            game_world.handle_input()
            game_world.update(delta)

            if not game_world.player_sprite.alive():
                state = GameState.MENU

            if game_world.won:
                state = GameState.WIN
                win_timer = 5

            pos = pygame.mouse.get_pos()
            try:
                world_pos = game_world.camera.screen_to_world(pos)
                pygame.display.set_caption(f"coord: {world_pos}, in mask: {game_world.world_mask.get_at(world_pos)}")
            except IndexError:
                pygame.display.set_caption(f"OFF MAP")

            # Background
            screen.fill((50, 25, 15))

            game_world.draw(screen)

        elif state == GameState.WIN:
            win_timer -= delta
            screen.fill((0, 0, 0))
            pos = pygame.mouse.get_pos()

            menu_text = "YOU WIN"
            menu_text_rendered = helpers.CREEPY_FONT.render(menu_text, True, (255, 255, 255))
            menu_text_rendered_rect = menu_text_rendered.get_rect()
            menu_text_rendered_rect.center = menu_area.center
            screen.blit(menu_text_rendered, menu_text_rendered_rect)

            if win_timer <= 0:
                state = GameState.MENU


        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()