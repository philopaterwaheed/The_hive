from consts import H, W
from grid import Grid
import pygame


def the_hive(shared, options_event):
    pygame.init()
    pygame.display.set_caption("the_hive")
    grid = Grid()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    bg_color = (10, 10, 10)

    pg_event_get = pygame.event.get
    pg_mouse_get_pressed = pygame.mouse.get_pressed
    pg_mouse_get_pos = pygame.mouse.get_pos
    pg_display_flip = pygame.display.flip

    grid_draw = grid.draw
    grid_move = grid.move_creatures
    grid_remove_dead = grid.remove_dead_creatures
    grid_reproduction = grid.handle_reproduction
    grid_evolution = grid.handle_evolution_spawn
    grid_add_creature = grid.add_creature
    grid_spawn_toxins = grid.spawn_toxins

    running_key = "running"

    while shared[running_key]:
        for e in pg_event_get():
            if e.type == pygame.QUIT:
                shared[running_key] = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    grid.save_best()
                    shared[running_key] = False
                elif e.key == pygame.K_o:
                    if not options_event.is_set():
                        options_event.set()
                    else:
                        options_event.clear()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                left, _, right = pg_mouse_get_pressed()
                if left:
                    x, y = pg_mouse_get_pos()
                    grid_add_creature(x, y)

        screen.fill(bg_color)
        grid_draw(screen)
        grid_move()
        grid_remove_dead()
        grid_reproduction()
        grid_evolution()
        grid_spawn_toxins()
        pg_display_flip()
        clock.tick(5000)

    pygame.quit()
