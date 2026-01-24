import math
import pygame
from enum import Enum


class Content (Enum):
    CREATURE = 1
    WALL = 2
    FOOD = 3
    EMPTY = 4


COLORS = {
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

    def __init__(self, cx, cy, size, content=Content.EMPTY):
        self.center_x = cx
        self.center_y = cy
        self.size = size
        self.content = content  # what inhabits the hex
        self.creature = None  # reference to creature if one is here
        self.fill = self.content != Content.EMPTY
        self.points = self.hex_points(cx, cy, size)

    def draw(self, screen):
        width = 0 if self.content != Content.EMPTY else 1
        
        # Use creature's color if a creature is on this hex
        if self.content == Content.CREATURE and self.creature:
            color = self.creature.color
        else:
            color = COLORS.get(self.content, (255, 255, 255))
        
        pygame.draw.polygon(screen, color, self.points, width)
        
        # A dot for mother creatures
        if self.content == Content.CREATURE and self.creature and self.creature.is_mother:
            r, g, b = self.creature.color
            dot_color = (255 - r, 255 - g, 255 - b)
            
            # Draw a circle at the center
            dot_radius = int(self.size * 0.2)
            pygame.draw.circle(screen, dot_color, (int(self.center_x), int(self.center_y)), dot_radius)
