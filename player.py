import pygame
import math

from gametools import ImageLoader
import entity

class Player(entity.Entity):

    def __init__(self, position: pygame.Vector2):
        player_img = ImageLoader.ImageLoader.GetImage("assets/imgs/BikePlayer.png", alpha=True)
        
        entity.Entity.__init__(self, position, player_img)

        self.on_bike = True
    
    def update(self, acceleration: pygame.Vector2, rotation: float, delta: float):
        self.velocity += acceleration * delta
        if self.on_bike:
            self.movement_on_bike(acceleration, rotation, delta)

        else:
            self.movement_on_foot(acceleration, rotation, delta)
            
        move_velocity = pygame.Vector2()
        orientation_rad = (self.orientation * math.pi) / 180.0
        move_velocity.x = math.cos(orientation_rad) * self.velocity.y
        move_velocity.y = -math.sin(orientation_rad) * self.velocity.y
        self.position += move_velocity * delta

        self.rect.center = self.position
        self.update_children()
        self.update_rect()

    def movement_on_bike(self, acceleration: pygame.Vector2, rotation: float, delta: float) -> None:
        # On bike you have a higher max speed but have a slower turn speed
        if acceleration.y == 0.0:
            self.velocity *= 0.5 ** delta

        # If the player is on a bike they will move only in the direction they are facing, no strafing.
        self.velocity.y = max(-50, min(self.velocity.y, 200))
        self.orientation += rotation * delta
        
    def movement_on_foot(self, acceleration: pygame.Vector2, rotation: float, delta: float) -> None:
        # On foot you turn faster but have a lower max speed
        if acceleration.y == 0:
            self.velocity *= 0.05 ** delta

        self.velocity.y = max(-10, min(self.velocity.y, 50))
        self.orientation += rotation * 4 * delta