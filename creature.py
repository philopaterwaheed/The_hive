from hex import Content, COLORS
from consts import MAX_HUNGER, REPRODUCTION_THRESHOLD, REPRODUCTION_COST, REPRODUCTION_PROBABILITY
from brain import NeuralNetwork, MotherBrain
import random


class Creature:
    hunger = 0
    dead = False
    captured = False
    is_mother = False

    def __init__(self, grid, col_index, row_key, taken_colors=None, parent_brain=None, mother=None):
        self.grid = grid
        self.col_index = col_index
        self.row_key = row_key
        self.mother = mother
        self.offspring = []
        self._shared_points = 0

        if parent_brain is not None:
            self.brain = parent_brain.copy()
            self.brain.mutate()
        else:
            self.brain = NeuralNetwork()

        # Mother brain for goal-setting
        if mother is None:
            self.mother_brain = MotherBrain()
            self.is_mother = True
        else:
            self.mother_brain = None
            self.is_mother = False

        # Generate a unique color not in taken_colors
        if taken_colors is None:
            taken_colors = set()

        max_attempts = 1000
        for _ in range(max_attempts):
            red = random.randint(30, 255)
            green = random.randint(30, 255)
            blue = random.randint(30, 255)
            color = (red, green, blue)

            # Check that the color isn't too dark (brightness check)
            brightness = (red * 0.299 + green * 0.587 + blue * 0.114)
            if brightness > 100 and color not in taken_colors and color not in COLORS:
                self.color = color
                taken_colors.add(self.color)
                break
        else:
            # Fallback color
            self.color = (50, random.randint(120, 255),
                          random.randint(120, 255))

    @property
    def point(self):
        if self.mother is not None and not self.mother.dead:
            return self.mother._shared_points
        return self._shared_points

    @point.setter
    def point(self, value):
        if self.mother is not None and not self.mother.dead:
            self.mother._shared_points = value
        else:
            self._shared_points = value

    def get_mother_goals(self):
        if self.mother is not None and not self.mother.dead and self.mother.mother_brain is not None:
            avg_hunger = sum(o.hunger for o in self.mother.offspring if not o.dead) / \
                max(1, len([o for o in self.mother.offspring if not o.dead]))
            return self.mother.mother_brain.get_goals(
                self.mother.hunger,
                self.mother.point,
                len([o for o in self.mother.offspring if not o.dead]),
                avg_hunger
            )
        return None

    def capture_food(self, dead=False, fats=50):
        if dead:
            self.hunger = max(0, self.hunger - fats)
        else:
            self.hunger = max(0, self.hunger - 20)

        # 30% goes to mother
        if self.mother is not None and not self.mother.dead:
            mother_share = int(fats * 0.3)
            self.mother.hunger = max(0, self.mother.hunger - mother_share)
            fats = fats - mother_share
        self.point += fats

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
        if self.mother is not None and self.mother.dead:
            self.dead = True
            return

        if not self.dead:
            inputs = self._get_sensory_inputs()

            goals = self.get_mother_goals()
            if goals is not None:
                inputs.extend(goals.tolist())
            else:
                inputs.extend([0.0, 0.0, 0.0])

            preferred_dir = self.brain.decide(inputs)
            valid_moves = self._get_valid_moves()

            if not valid_moves:
                # No valid moves, stay in place
                self.move(0, 0)
                return

            # Direction 6 means stay
            # punish for trying to stay too often
            if preferred_dir == 6:
                self.point = max(0, self.point - 5)
                self.hunger = min(MAX_HUNGER, self.hunger + 5)
                self.move(0, 0)
                return

            # Apply mother's goal influence for food priority
            food_bonus = 0
            if goals is not None:
                food_priority = (goals[0] + 1) / 2  # Normalize to 0-1
                food_bonus = int(food_priority * 5)

            # Try to find the preferred direction in valid moves
            for dir_idx, col_d, row_d, has_food in valid_moves:
                if dir_idx == preferred_dir:
                    # Reward for moving towards food
                    self.point += (2 + food_bonus) if has_food else 0
                    self.move(col_d, row_d)
                    return

            # Preferred direction is blocked- punish
            self.point = max(0, self.point - 5)
            self.hunger = min(MAX_HUNGER, self.hunger + 5)
            self.move(0, 0)  # Stay in place (also causes hunger)

    def _get_valid_moves(self):
        valid_moves = []
        rows = list(self.grid.hexs.keys())

        try:
            current_row_idx = rows.index(self.row_key)
        except ValueError:
            return valid_moves

        is_even_row = current_row_idx % 2 == 0

        # Define all 6 hex directions: (direction_index, col_delta, row_delta)
        # Horizontal directions
        directions = [
            (0, -1, 0),   # Left
            (1, 1, 0),    # Right
        ]

        # Add diagonal directions based on row parity
        if current_row_idx > 0:
            if is_even_row:
                directions.append((2, -1, -1))  # Up-left
                directions.append((3, 0, -1))   # Up-right
            else:
                directions.append((2, 0, -1))   # Up-left
                directions.append((3, 1, -1))   # Up-right

        if current_row_idx < len(rows) - 1:
            if is_even_row:
                directions.append((4, -1, 1))   # Down-left
                directions.append((5, 0, 1))    # Down-right
            else:
                directions.append((4, 0, 1))    # Down-left
                directions.append((5, 1, 1))    # Down-right

        for dir_idx, col_d, row_d in directions:
            new_col = self.col_index + col_d
            new_row_key = self.row_key

            if row_d != 0:
                new_row_index = current_row_idx + row_d
                if 0 <= new_row_index < len(rows):
                    new_row_key = rows[new_row_index]
                else:
                    continue

            if self.can_move_to(new_col, new_row_key):
                content, creature = self._get_hex_content(new_col, new_row_key)
                has_food = (content == Content.FOOD or
                            (content == Content.CREATURE and creature and creature.dead and not creature.captured))
                valid_moves.append((dir_idx, col_d, row_d, has_food))

        return valid_moves

    def _get_sensory_inputs(self):
        inputs = []
        neighbors = self._get_neighbor_contents()

        for content, creature in neighbors:
            # Encode content type: 0=empty, 0.5=food/dead, 1=wall/living creature
            if content == Content.EMPTY:
                content_val = 0.0
            elif content == Content.FOOD:
                content_val = 0.5
            elif content == Content.WALL:
                content_val = 1.0
            elif content == Content.CREATURE:
                if creature and creature.dead:
                    content_val = 0.5  # Dead creature is like food
                else:
                    content_val = 1.0  # Living creature is obstacle
            else:
                content_val = 0.0

            is_edible = 1.0 if (content == Content.FOOD or
                                (content == Content.CREATURE and creature and creature.dead and not creature.captured)) else 0.0

            inputs.extend([content_val, is_edible])

        inputs.append(self.hunger / MAX_HUNGER)
        inputs.append(min(self.point / 100.0, 1.0))

        return inputs

    def _get_neighbor_contents(self):
        neighbors = []
        rows = list(self.grid.hexs.keys())

        try:
            current_row_idx = rows.index(self.row_key)
        except ValueError:
            return [(Content.WALL, None)] * 6

        is_even_row = current_row_idx % 2 == 0

        # Left
        neighbors.append(self._get_hex_content(
            self.col_index - 1, self.row_key))

        # Right
        neighbors.append(self._get_hex_content(
            self.col_index + 1, self.row_key))

        # Previous row (up-left, up-right)
        if current_row_idx > 0:
            prev_y = rows[current_row_idx - 1]
            if is_even_row:
                neighbors.append(self._get_hex_content(
                    self.col_index - 1, prev_y))
                neighbors.append(self._get_hex_content(self.col_index, prev_y))
            else:
                neighbors.append(self._get_hex_content(self.col_index, prev_y))
                neighbors.append(self._get_hex_content(
                    self.col_index + 1, prev_y))
        else:
            neighbors.extend([(Content.WALL, None), (Content.WALL, None)])

        # Next row (down-left, down-right)
        if current_row_idx < len(rows) - 1:
            next_y = rows[current_row_idx + 1]
            if is_even_row:
                neighbors.append(self._get_hex_content(
                    self.col_index - 1, next_y))
                neighbors.append(self._get_hex_content(self.col_index, next_y))
            else:
                neighbors.append(self._get_hex_content(self.col_index, next_y))
                neighbors.append(self._get_hex_content(
                    self.col_index + 1, next_y))
        else:
            neighbors.extend([(Content.WALL, None), (Content.WALL, None)])

        return neighbors

    def _get_hex_content(self, col_index, row_key):
        if row_key not in self.grid.hexs:
            return (Content.WALL, None)

        row = self.grid.hexs[row_key]
        if col_index < 0 or col_index >= len(row):
            return (Content.WALL, None)

        hex = row[col_index]
        return (hex.content, hex.creature)

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
        self.point = max(0, self.point - 1)
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
