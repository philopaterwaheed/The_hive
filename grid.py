class Grid:
    hexs: dict[float, list] = {}

    def add_hex(self, hex):
        if not self.hexs.get(hex.center_y):
            self.hexs[hex.center_y] = []
        self.hexs.get(hex.center_y).append(hex)

    def draw(self):
        for raw in self.hexs.values():
            for hex in raw:
                hex.draw()
