import math
from consts import HEX_SIZE, Y_DIFF, H


class Creature:
    x, y = HEX_SIZE, HEX_SIZE

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, axes, val: int):
        if axes == "y":
            if self.y + int(HEX_SIZE * Y_DIFF) <= H - math.sqrt(3) * HEX_SIZE:
                self.y = self.y + int(HEX_SIZE * Y_DIFF)
        if axes == "x":
            self.x = self.x + val
