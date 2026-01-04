import pygame
import math

pygame.init()

W, H = 1600, 800
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def hex_points(x, y, size):
    pts = []
    for i in range(6):
        ang = math.radians(60 * i + 30)
        pts.append((x + size * math.cos(ang), y + size * math.sin(ang)))
    return pts


running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 10))

    toggle = False
    for y in range(45, H-45, 26):
        for x in range(45, W-45, 27):
            pygame.draw.polygon(screen, (0, 140, 255),
                                hex_points(x-(15*(toggle)), y, 15), 1)
        toggle = not toggle

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
