import pygame

from helpers import SCREEN_SIZE, TILE_SIZE

class Camera:
    """Used to keep track of what should be on the screen. 
    Represents the virtual camera. Contains functions to convert
    to/from screen space from/to world space
    """

    SCREEN_CENTER = pygame.Vector2(SCREEN_SIZE) / 2

    def __init__(self, pos: pygame.Vector2):
        self._scale = 1.0
        self._position = pos
        self.initial_position = pos

    @staticmethod
    def world_to_px_coords(coord: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(coord.x * TILE_SIZE[0], coord.y * TILE_SIZE[1])

    @staticmethod
    def px_to_world_coords(coord: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(coord.x / TILE_SIZE[0], coord.y / TILE_SIZE[1])

    def world_to_screen(self, coord: pygame.Vector2) -> pygame.Vector2:
        """Convert a coordinate from world (tile) space to screen space"""

        offset_from_camera_world = (coord - self._position) * self.scale
        offset_from_camera_px = Camera.world_to_px_coords(offset_from_camera_world)
        return offset_from_camera_px + Camera.SCREEN_CENTER

    def screen_to_world(self, coord: pygame.Vector2) -> pygame.Vector2:
        """Convert a coordinate from screen space to world (tile) space"""

        offset_from_camera_px = coord - Camera.SCREEN_CENTER
        offset_from_camera_world = Camera.px_to_world_coords(offset_from_camera_px)
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