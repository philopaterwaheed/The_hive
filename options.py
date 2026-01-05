import pygame

def options(shared, options_event):
    while shared["running"]:
        if not options_event.wait(timeout=0.1):
            continue

        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("options")
        clock = pygame.time.Clock()

        while options_event.is_set() and shared["running"]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options_event.clear()

            screen.fill((200, 80, 80))
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
