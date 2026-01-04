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
    size = 10
    for y in range(size, H-size, int(size * 1.51)):
        for x in range(size, W-size, int(size * 1.75)):
            pygame.draw.polygon(screen, (0, 140, 255),
                                hex_points(x+(int(size*0.87*(toggle))), y, size), 1)
        toggle = not toggle

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
