import math
import pygame
import pygame.gfxdraw
from enum import IntEnum


class Content(IntEnum):
    CREATURE = 1
    WALL = 2
    FOOD = 3
    EMPTY = 4
    TOXIN = 5


_COLOR_WALL = (100, 100, 100)
_COLOR_FOOD = (200, 0, 0)
_COLOR_EMPTY = (0, 0, 0)
_COLOR_DEAD = (255, 0, 0)
_COLOR_TOXIN = (150, 0, 150)  # Purple for toxins
_COLOR_DEFAULT = (255, 255, 255)

COLORS = {
    Content.WALL: _COLOR_WALL,
    Content.FOOD: _COLOR_FOOD,
    Content.EMPTY: _COLOR_EMPTY,
    Content.TOXIN: _COLOR_TOXIN
}


_HEX_UNIT_OFFSETS = []
for i in range(6):
    ang = math.radians(60 * i + 30)
    _HEX_UNIT_OFFSETS.append((math.cos(ang), math.sin(ang)))


class Hex:
    __slots__ = ('center_x', 'center_y', 'size', 'content', 'creature', 'fill', 'points',
                 '_center_int')

    @staticmethod
    def hex_points(x, y, size):
        return [(x + size * ox, y + size * oy) for ox, oy in _HEX_UNIT_OFFSETS]

    def __init__(self, cx, cy, size, content=Content.EMPTY):
        self.center_x = cx
        self.center_y = cy
        self.size = size
        self.content = content  # what inhabits the hex
        self.creature = None  # reference to creature if one is here
        self.fill = self.content != Content.EMPTY
        self.points = self.hex_points(cx, cy, size)
        self._center_int = (int(cx), int(cy))

    def draw(self, screen):
        content = self.content
        creature = self.creature

        if content == Content.EMPTY:
            pygame.draw.polygon(screen, _COLOR_EMPTY, self.points, 1)
            return

        if content == Content.CREATURE and creature:
            color = creature.color
        elif content == Content.WALL:
            color = _COLOR_WALL
        elif content == Content.FOOD:
            color = _COLOR_FOOD
        elif content == Content.TOXIN:
            color = _COLOR_TOXIN
        else:
            color = _COLOR_DEFAULT

        pygame.draw.polygon(screen, color, self.points, 0)

        # Draw creature indicators
        if content == Content.CREATURE and creature:
            center = self._center_int
            size = self.size

            # Dead creature - just red circle
            if creature.dead:
                pygame.draw.circle(screen, _COLOR_DEAD,
                                   center, int(size * 0.7))
            else:
                # Living creature - draw dot
                r, g, b = creature.color
                dot_color = (255 - r, 255 - g, 255 - b)
                dot_radius = int(
                    size * 0.4) if creature.is_mother else int(size * 0.15)
                pygame.draw.circle(screen, dot_color, center, dot_radius)
