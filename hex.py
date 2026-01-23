import math
import pygame
from enum import Enum


class Content (Enum):
    CREATURE = 1
    WALL = 2
    FOOD = 3
    EMPTY = 4


COLORS = {
    Content.CREATURE: (0, 140, 255),   # cyan
    Content.WALL:     (100, 100, 100),  # gray
    Content.FOOD:     (200, 0, 0),   # red
    # Content.EMPTY:    (255, 255, 255)  # white
    Content.EMPTY:    (0, 0, 0)  # black
}


class Hex:
    @staticmethod
    def hex_points(x, y, size):
        pts = []
        for i in range(6):
            ang = math.radians(60 * i + 30)
            pts.append((x + size * math.cos(ang), y + size * math.sin(ang)))
        return pts

    color = (0, 0, 0)

    def __init__(self, cx, cy, size, content=Content.EMPTY):
        self.center_x = cx
        self.center_y = cy
        self.size = size
        self.content = content  # what inhabits the hex
        self.fill = self.content != Content.EMPTY
        self.points = self.hex_points(cx, cy, size)

    def draw(self, screen):
        color = COLORS[self.content]
        width = 0 if self.content != Content.EMPTY else 1
        pygame.draw.polygon(screen, color, self.points, width)
