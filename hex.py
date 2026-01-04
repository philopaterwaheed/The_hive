import math
import pygame

from consts import screen


class Hex:
    @staticmethod
    def hex_points(x, y, size):
        pts = []
        for i in range(6):
            ang = math.radians(60 * i + 30)
            pts.append((x + size * math.cos(ang), y + size * math.sin(ang)))
        return pts

    def __init__(self, cx, cy, size, fill):
        self.center_x = cx
        self.center_y = cy
        self.size = size
        self.fill = fill
        self.points = self.hex_points(cx, cy, size)

    def draw(self):
        pygame.draw.polygon(screen, (0, 140, 255), self.points, 1)
