import math
import pygame

import helpers

import entity

class Light(entity.Entity):
    """A light source that can reveal the true nature of others'"""

    def __init__(self, position, angle_offset=0):
        self.arc = 20.0 * helpers.DEG_TO_RAD # degrees
        size = 500
        center = size / 2
        self.radius = size / 2
        self.timer = 0

        # Since the light is also an entity, the light is drawn once on
        # creation to a Surface big enough to hold a circle with radius = self.radius.
        light_image = pygame.Surface((size, size), pygame.SRCALPHA)
        light_image.fill((0, 0, 0, 0)) # Completely transparent image

        # Draw points on the arc
        points = []
        resolution = 10
        start_angle = self.arc / 2 + angle_offset
        interval = self.arc / resolution
        for idx in range(resolution):
            point_angle = start_angle - interval * idx
            new_point = self.radius * pygame.Vector2(math.cos(point_angle),-math.sin(point_angle))
            new_point += pygame.Vector2(center, center)
            points.append(new_point)
        pygame.draw.polygon(light_image, (255, 255, 0, 127), ((center + 20, center), *points))

        # Finally do the entity constructor once we have the image
        entity.Entity.__init__(self, position, light_image)

    def in_light(self, check_pos: pygame.Vector2) -> bool:
        """Returns true if `check_pos` is within the light cone."""
        orientation_rad = self.orientation * helpers.DEG_TO_RAD
        orientation_vec = pygame.Vector2(math.cos(orientation_rad), -math.sin(orientation_rad))
        offset_vec = check_pos - self.position

        # if the distance is further than the radius, the point is outside the light.
        if offset_vec.length() > self.radius:
            return False

        # for two normalized vectors, a and b, the angle between them is acos(dot(a, b))
        return math.acos(offset_vec.normalize().dot(orientation_vec)) < self.arc / 2

    def update(self, delta: float) -> None:
        """Adds a flicker effect"""
        self.timer += delta
        alpha = 200 + 55 * (1.0 + math.sin(self.timer * 4)) / 2.0
        self.image.set_alpha(alpha)
