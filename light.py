import math
import pygame

import helpers

import entity

class Light(entity.Entity):

    def __init__(self, position, angle_offset=0):
        self.arc = 20.0 * helpers.DEG_TO_RAD # degrees
        size = 500
        center = size / 2
        self.radius = size / 2
        self.timer = 0
        light_image = pygame.Surface((size, size), pygame.SRCALPHA)
        light_image.fill((0, 0, 0, 0)) # Alpha

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

        entity.Entity.__init__(self, position, light_image)

    def in_light(self, check_pos: pygame.Vector2):
        """Test whether a position is within the light cone"""
        orientation_vec = pygame.Vector2(math.cos(self.orientation * helpers.DEG_TO_RAD), -math.sin(self.orientation * helpers.DEG_TO_RAD))
        offset_vec = check_pos - self.position

        if offset_vec.length() > self.radius:
            return False

        # for two normalized vectors, a and b, the angle between them is acos(dot(a, b))
        return math.acos(offset_vec.normalize().dot(orientation_vec)) < self.arc / 2

    def update(self, delta):
        self.timer += delta
        alpha = 200 + 55 * (1.0 + math.sin(self.timer * 4)) / 2.0
        self.image.set_alpha(alpha)
