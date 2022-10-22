import pygame
import math

import entity
import ImageLoader

class Player(entity.Entity):

    def __init__(self, position: pygame.Vector2):
        player_img = ImageLoader.ImageLoader.GetImage("assets/imgs/bike.png", alpha=True)
        
        entity.Entity.__init__(self, position, player_img)

        self.on_bike = True
    
    def update(self, acceleration, rotation, delta):
        if self.on_bike and acceleration.y == 0.0:
            # Slows the player down if they aren't actively "pedaling"
            direction = -1 if self.velocity.y > 0 else 0 if self.velocity.y == 0 else 1
            acceleration.y = ((10 / delta) + self.velocity.y * self.velocity.y / 2.0) * delta * direction
        self.velocity += acceleration * delta

        if self.on_bike:
            self.velocity.y = max(-50, self.velocity.y)
            move_velocity = pygame.Vector2()
            orientation_rad = (self.orientation * math.pi) / 180.0
            move_velocity.x = math.cos(orientation_rad) * self.velocity.y
            move_velocity.y = -math.sin(orientation_rad) * self.velocity.y
            self.position += move_velocity * delta
            self.orientation += rotation * delta

        self.rect.center = self.position
        self.update_children()
        self.update_rect()