import pygame
from hex import Hex
from consts import screen, clock, H, W,  HEX_SIZE
from grid import Grid

pygame.init()
grid = Grid()


running = True
while running:
    for e in pygame.event.get():
        left, _, right = pygame.mouse.get_pressed()
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN or (e.type == pygame.MOUSEMOTION and left or right):
            x, y = pygame.mouse.get_pos()
            if left:
                grid.add_creature(x, y)
            elif right:
                grid.toggle_fill(x, y, False)

    screen.fill((10, 10, 10))
    grid.draw()
    grid.move_creatures()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
