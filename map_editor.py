from email.mime import base
import pygame

import helpers
import camera

from gametools import ImageLoader

def create_prop_sprite(image_path, location) -> pygame.sprite.Sprite:
    prop_sprite = pygame.sprite.Sprite()
    prop_sprite.image = ImageLoader.ImageLoader.GetImage(image_path)
    prop_sprite.rect = prop_sprite.image.get_rect()
    prop_sprite.rect.center = location
    prop_sprite.path = image_path
    return prop_sprite

def run():

    screen = pygame.display.set_mode(helpers.SCREEN_SIZE)

    base_image = ImageLoader.ImageLoader.GetImage("assets/imgs/TheMap.png")
    world_image = base_image
    world_camera = camera.Camera(pygame.Vector2(0, 0))

    path_start = "assets/imgs/"
    prop_associations = {
        path_start + "Creature/creature_idle1.png": "Creature",
        path_start + "tree.png": "Tree",
        path_start + "Humanoid1.png": "Humanoid"
    }

    prop_strings = [key for key in prop_associations]
    current_prop_index = 0
    current_prop = prop_strings[current_prop_index]
    placed_props = pygame.sprite.Group()

    done = False
    while not done:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

                elif event.key == pygame.K_RIGHT:
                    current_prop_index += 1
                    current_prop_index %= len(prop_strings)
                    current_prop = prop_strings[current_prop_index]

                elif event.key == pygame.K_LEFT:
                    current_prop_index -= 1
                    current_prop_index %= len(prop_strings)
                    current_prop = prop_strings[current_prop_index]

                elif event.key == pygame.K_e:
                    with open("mapdata.txt", 'w') as f:
                        for prop in placed_props:
                            world_position = prop.rect.center
                            association = prop_associations[prop.path]
                            f.write(f"\"{association}\", {world_position}\n")

            elif event.type == pygame.MOUSEWHEEL:
                # zooming
                old_mouse_world = world_camera.screen_to_world(mouse_pos)
                
                world_camera.scale *= 1.0 + (event.y * 0.1)
                world_camera.scale = min(1, world_camera.scale)

                new_mouse_world = world_camera.screen_to_world(mouse_pos)

                world_camera.position += old_mouse_world - new_mouse_world

                world_image = pygame.transform.scale(base_image, pygame.Vector2(base_image.get_size()) * world_camera.scale)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    new_prop = create_prop_sprite(current_prop, world_camera.screen_to_world(mouse_pos))
                    placed_props.add(new_prop)

                elif event.button == 3:
                    for sprite in placed_props:
                        if sprite.rect.collidepoint(world_camera.screen_to_world(mouse_pos)):
                            sprite.kill()
                            break

        # panning
        if mouse_pos.x < helpers.SCREEN_SIZE[0] * 0.1:
            world_camera.position.x -= 1 / world_camera.scale
        if mouse_pos.x > helpers.SCREEN_SIZE[0] * 0.9:
            world_camera.position.x += 1 / world_camera.scale
        if mouse_pos.y < helpers.SCREEN_SIZE[1] * 0.1:
            world_camera.position.y -= 1 / world_camera.scale
        if mouse_pos.y > helpers.SCREEN_SIZE[1] * 0.9:
            world_camera.position.y += 1 / world_camera.scale

        screen.fill((255, 255, 255))

        # Map
        screen.blit(world_image, world_camera.world_to_screen(pygame.Vector2(0, 0)))

        # Props
        for prop in placed_props:
            new_rect = prop.rect.copy()
            new_rect.center = world_camera.world_to_screen(pygame.Vector2(prop.rect.center))
            screen.blit(prop.image, new_rect)

        # UI
        UI_rect = pygame.Rect((0, 0, 64, 64))
        UI_rect.center = (helpers.CENTER_X, 64)
        pygame.draw.rect(screen, (255, 0, 0), UI_rect, 3, 2)
        screen.blit(ImageLoader.ImageLoader.GetImage(current_prop, (64, 64), True), UI_rect)

        pygame.display.update()

if __name__ == "__main__":
    run()