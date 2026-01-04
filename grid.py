import math
from consts import hex_size, W, H , X_DIFF , Y_DIFF , X_OFFSET
from hex import Hex


class Grid:

    hexs: dict[float, list] = {}

    def __init__(self):
        toggle = False
        for y in range(hex_size, H-hex_size, int(hex_size * Y_DIFF)):
            for x in range(hex_size, W-hex_size, int(hex_size * X_DIFF)):
                if x <= (W - (2 * hex_size)) and y <= H - math.sqrt(3) * hex_size:
                    new_hex = Hex(x+(int(hex_size*X_OFFSET*(toggle))),
                                  y, hex_size, False)
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

    def toggle_fill(self, x, y, fill):
        hex_y = math.floor(hex_size + int(hex_size * Y_DIFF) *
                           math.floor(y/int(hex_size * Y_DIFF)))

        raw = self.hexs.get(hex_y)
        if raw:
            raw_len = len(raw)
            if raw_len >= 1:
                hex_i = int(
                    (x - raw[0].center_x + hex_size / 2)/int(hex_size * X_DIFF))
                if hex_i < raw_len:
                    raw[hex_i].fill = fill
