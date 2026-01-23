import pygame
from buttons import draw_button

WIDTH, HIGHT = 500, 800


def init_options():

    # Button positions
    options_btn = pygame.Rect((WIDTH - 300)/2,   100, 300, 50)
    back_btn = pygame.Rect((WIDTH - 140)/2,   220, 140, 40)
    return options_btn, back_btn


def options(shared, options_event):
    while shared["running"]:
        if not options_event.wait(timeout=0.1):
            continue

        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HIGHT))
        pygame.display.set_caption("options")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 36)
        state = "menu"
        options_btn, back_btn = init_options()

        # Title
        title = font.render("Options", True, (0, 0, 0))

        running_options = True
        while options_event.is_set() and shared["running"] and running_options:
            screen.fill((200, 80, 80))
            screen.blit(title, ((WIDTH - title.get_width())/2,  20))
            mouse_pos = pygame.mouse.get_pos()

            # Draw buttons
            if state == "menu":
                draw_button(screen, font, "Go to Options",
                            options_btn, options_btn.collidepoint(mouse_pos))
            if state == "options":
                draw_button(screen, font, "Back", back_btn,
                            back_btn.collidepoint(mouse_pos))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options_event.clear()
                    running_options = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if state == "menu" and options_btn.collidepoint(event.pos):
                        state = "options"
                    elif state == "options" and back_btn.collidepoint(event.pos):
                        state = "menu"

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
