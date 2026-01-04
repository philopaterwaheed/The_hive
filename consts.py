import pygame
from grid import Grid

W, H = 1600, 800
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

hex_size = 10

grid = Grid()
