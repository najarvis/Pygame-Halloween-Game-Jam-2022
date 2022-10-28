import pygame

import helpers
import world
import os

def run():
    screen = pygame.display.set_mode(helpers.SCREEN_SIZE)
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

        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()