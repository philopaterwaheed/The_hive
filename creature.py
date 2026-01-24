from hex import Content, COLORS
from consts import MAX_HUNGER, REPRODUCTION_THRESHOLD, REPRODUCTION_COST, REPRODUCTION_PROBABILITY
import random


class Creature:
    point = 0
    hunger = 0
    dead = False
    captured = False

    def __init__(self, grid, col_index, row_key, taken_colors=None):
        self.grid = grid
        self.col_index = col_index
        self.row_key = row_key

        # Generate a unique color not in taken_colors
        if taken_colors is None:
            taken_colors = set()

        max_attempts = 1000
        for _ in range(max_attempts):
            color = (random.randint(10, 255), random.randint(
                10, 255), random.randint(10, 255))
            if color not in taken_colors and color not in COLORS:
                self.color = color
                break
        else:
            self.color = (random.randint(50, 255), random.randint(
                50, 255), random.randint(50, 255))

    def capture_food(self, dead=False, fats=50):
        if dead:
            self.HUNGER = max(0, self.hunger - fats)
        else:
            self.hunger = max(0, self.hunger - 20)
        self.point += 1

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

        hex = row[col_index]
        if hex.content != Content.EMPTY and hex.content != Content.FOOD and not (hex.content == Content.CREATURE and hex.creature.dead and not hex.creature.captured):
            return False
        return True

    def think(self):
        if not self.dead:
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
            dead = (new_hex.content ==
                    Content.CREATURE and new_hex.creature and new_hex.creature.dead and not new_hex.creature.captured)
            if new_hex.content == Content.FOOD or dead:
                # how faty was the dead creature
                fats = 0
                if dead:
                    fats = new_hex.creature.point // 10
                    new_hex.creature.captured = True if dead else False
                self.capture_food(dead, fats)
            new_hex.content = Content.CREATURE
            new_hex.creature = self
        self.hunger = min(MAX_HUNGER, self.hunger + 1)
        if self.hunger >= MAX_HUNGER:
            self.dead = True

    def can_reproduce(self):
        if not self.dead:
            prop = random.uniform(0, 1)
            if prop > REPRODUCTION_PROBABILITY:
                return False
            return self.hunger <= REPRODUCTION_THRESHOLD

    def reproduce(self):
        if self.can_reproduce():
            self.hunger += REPRODUCTION_COST
            return True
        return False
