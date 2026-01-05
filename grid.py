import math
from consts import HEX_SIZE, W, H, X_DIFF, Y_DIFF, X_OFFSET
from hex import Hex
from creature import Creature


class Grid:

    hexs: dict[float, list] = {}
    creatures = []

    def __init__(self):
        toggle = False
        for y in range(HEX_SIZE, H-HEX_SIZE, int(HEX_SIZE * Y_DIFF)):
            for x in range(HEX_SIZE, W-HEX_SIZE, int(HEX_SIZE * X_DIFF)):
                if x <= (W - (2 * HEX_SIZE)) and y <= H - math.sqrt(3) * HEX_SIZE:
                    new_hex = Hex(x+(int(HEX_SIZE*X_OFFSET*(toggle))),
                                  y, HEX_SIZE, False)
                    self.add_hex(new_hex)
            toggle = not toggle

    def add_hex(self, hex: Hex):
        if not self.hexs.get(hex.center_y):
            self.hexs[hex.center_y] = []
        self.hexs.get(hex.center_y).append(hex)

    def draw(self):
        for raw in self.hexs.values():
            for hex in raw:
                hex.draw()

    def move_creatures(self):
        for creature in self.creatures:
            self.hexs[creature.y][creature.x].fill = False
            creature.move("x", 1)
            creature.move("y", 1)
            self.hexs[creature.y][creature.x].fill = True

    def toggle_fill(self, x, y, fill):
        i, y = self.get_hex_pos(x, y) or (-1, -1)
        if i > -1 and y > -1:
            self.hexs[y][i].fill = fill

    def add_creature(self, x, y):
        i, y = self.get_hex_pos(x, y) or (-1, -1)
        if i > -1 and y > -1:
            self.creatures.append(Creature(i, y))

    def get_hex_pos(self, x, y):
        hex_y = math.floor(HEX_SIZE + int(HEX_SIZE * Y_DIFF) *
                           math.floor(y/int(HEX_SIZE * Y_DIFF)))
        raw = self.hexs.get(hex_y)
        if raw:
            raw_len = len(raw)
            if raw_len >= 1:
                hex_i = int(
                    (x - raw[0].center_x + HEX_SIZE / 2)/int(HEX_SIZE * X_DIFF))
                if hex_i < raw_len:
                    return (hex_i, hex_y)
