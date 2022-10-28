import math
import pygame

RAD_TO_DEG = 180 / math.pi
DEG_TO_RAD = math.pi / 180
SCREEN_SIZE = WIDTH, HEIGHT = (1280, 720)
CENTER_X, CENTER_Y = CENTER = (WIDTH / 2, HEIGHT / 2)
TILE_SIZE = (1, 1)

pygame.font.init()
CREEPY_FONT = pygame.font.Font("assets/fonts/October Crow.ttf", 40)
REGULAR_FONT = pygame.font.SysFont("Consolas", 18)