import pygame
from hex import Hex
from consts import screen, clock, H, W,  HEX_SIZE
from grid import Grid

pygame.init()
grid = Grid()




running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            left, _, right = pygame.mouse.get_pressed()
            if left:
                grid.toggle_fill(x, y, True)
            elif right:
                grid.toggle_fill(x, y, False)

    screen.fill((10, 10, 10))
    grid.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
