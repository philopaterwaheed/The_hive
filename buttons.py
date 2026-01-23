import pygame


def draw_button(screen, font, text, rect, hover=False):
    color = (180, 180, 180) if hover else (140, 140, 140)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    txt = font.render(text, True, (0, 0, 0))
    screen.blit(
        txt,
        txt.get_rect(center=rect.center)
    )
