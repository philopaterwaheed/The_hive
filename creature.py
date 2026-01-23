from hex import Content, COLORS
import random


class Creature:
    def __init__(self, grid, col_index, row_key, taken_colors=None):
        self.grid = grid
        self.col_index = col_index
        self.row_key = row_key
        
        # Generate a unique color not in taken_colors
        if taken_colors is None:
            taken_colors = set()
        
        max_attempts = 1000
        for _ in range(max_attempts):
            color = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
            if color not in taken_colors and color not in COLORS:
                self.color = color
                break
        else:
            self.color = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))

    def get_current_hex(self):
        if self.row_key in self.grid.hexs:
            row = self.grid.hexs[self.row_key]
            if 0 <= self.col_index < len(row):
                return row[self.col_index]
        return None

    def can_move_to(self, col_index, row_key):
        if row_key not in self.grid.hexs:
            return False

        row = self.grid.hexs[row_key]
        if col_index < 0 or col_index >= len(row):
            return False

        if row[col_index].content != Content.EMPTY:
            return False
        return True

    def think(self):
        self.move(random.choice([0, 1, -1]), random.choice([0, 1, -1]))

    def move(self, col_delta=0, row_delta=0):
        current_hex = self.get_current_hex()
        if current_hex:
            current_hex.content = Content.EMPTY
            current_hex.creature = None
        new_col = self.col_index + col_delta
        if row_delta != 0:
            rows = list(self.grid.hexs.keys())
            try:
                current_row_index = rows.index(self.row_key)
                new_row_index = current_row_index + row_delta

                if 0 <= new_row_index < len(rows):
                    new_row_key = rows[new_row_index]
                else:
                    new_row_key = self.row_key
            except (ValueError, IndexError):
                new_row_key = self.row_key
        else:
            new_row_key = self.row_key

        if self.can_move_to(new_col, new_row_key):
            self.col_index = new_col
            self.row_key = new_row_key

        new_hex = self.get_current_hex()
        if new_hex:
            new_hex.content = Content.CREATURE
            new_hex.creature = self
