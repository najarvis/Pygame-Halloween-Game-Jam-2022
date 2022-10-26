import pygame

import helpers
import world


def run():
    screen = pygame.display.set_mode(helpers.SCREEN_SIZE, pygame.FULLSCREEN)
    pygame.display.set_caption("Spooky game for game jam!")

    clock = pygame.time.Clock()
    done = False

    game_world = world.World()

    while not done:
        delta = clock.tick(144) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

        game_world.handle_input()
        game_world.update(delta)

        # Background
        screen.fill((50, 25, 15))

        game_world.draw(screen)

        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    run()