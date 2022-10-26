import pygame

from helpers import CENTER_X, CENTER_Y

class Camera:
    """Used to keep track of what should be on the screen. 
    Represents the virtual camera. Contains functions to convert
    to/from screen space from/to world space
    """

    SCREEN_CENTER = pygame.Vector2((CENTER_X, CENTER_Y))

    def __init__(self, pos: pygame.Vector2):
        self._scale = 1.0
        self._position = pos
        self.initial_position = pos

    def world_to_screen(self, coord: pygame.Vector2) -> pygame.Vector2:
        """Convert a coordinate from world space to screen space"""

        offset_from_camera_px = (coord - self._position) * self.scale
        return offset_from_camera_px + Camera.SCREEN_CENTER

    def screen_to_world(self, coord: pygame.Vector2) -> pygame.Vector2:
        """Convert a coordinate from screen space to world space"""

        offset_from_camera_world = coord - Camera.SCREEN_CENTER
        return (offset_from_camera_world / self.scale) + self._position

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, val) -> None:
        # clamp the values
        self._scale = max(0.1, min(val, 10))

    """The zoom level of the camera. As this increases object on the screen appear larger"""
    scale = property(get_scale, set_scale)

    def get_position(self) -> pygame.Vector2:
        return self._position

    def set_position(self, new_pos: pygame.Vector2) -> None:
        self._position = new_pos

    """The center of what the camera is looking at in world space"""
    position = property(get_position, set_position)