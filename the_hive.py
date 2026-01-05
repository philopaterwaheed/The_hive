from consts import H, W
from grid import Grid
import pygame


def the_hive(shared, options_event):
    pygame.init()
    pygame.display.set_caption("the_hive")
    grid = Grid()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    while shared["running"]:
        for e in pygame.event.get():
            left, _, right = pygame.mouse.get_pressed()
            if e.type == pygame.QUIT:
                shared["running"] = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_o:
                    if not options_event.is_set():
                        options_event.set()
                    else:
                        options_event.clear()
            elif e.type == pygame.MOUSEBUTTONDOWN or (e.type == pygame.MOUSEMOTION and left or right):
                x, y = pygame.mouse.get_pos()
                if left:
                    grid.add_creature(x, y)
                elif right:
                    grid.toggle_fill(x, y, False)

        screen.fill((10, 10, 10))
        grid.draw(screen)
        grid.move_creatures()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
