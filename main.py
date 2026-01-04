import pygame
from hex import Hex
from consts import screen, clock, H, W, grid, hex_size


pygame.init()
screen.fill((10, 10, 10))

toggle = False
for y in range(hex_size, H-hex_size, int(hex_size * 1.51)):
    for x in range(hex_size, W-hex_size, int(hex_size * 1.75)):
        new_hex = Hex(x+(int(hex_size*0.87*(toggle))), y, hex_size, False)
        grid.add_hex(new_hex)

    toggle = not toggle


running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    grid.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
