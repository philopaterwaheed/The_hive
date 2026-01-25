from hex import Content, COLORS
from consts import MAX_HUNGER, REPRODUCTION_THRESHOLD, REPRODUCTION_COST, REPRODUCTION_PROBABILITY
from brain import NeuralNetwork, MotherBrain
import random

_HUNGER_THRESHOLD = MAX_HUNGER * 0.8
_INV_MAX_HUNGER = 1.0 / MAX_HUNGER


class Creature:
    __slots__ = ('grid', 'col_index', 'row_key', 'mother', 'offspring', '_shared_points',
                 'position_history', 'history_size', 'brain', 'mother_brain', 'color',
                 'hunger', 'dead', 'captured', 'is_mother')

    def __init__(self, grid, col_index, row_key, taken_colors=None, parent_brain=None, mother=None, parent_mother_brain=None):
        self.grid = grid
        self.col_index = col_index
        self.row_key = row_key
        self.mother = mother
        self.offspring = []
        self._shared_points = 0
        self.position_history = []  # Track recent positions to prevent cycling
        self.history_size = 6  # Track last 6 positions
        self.hunger = 0
        self.dead = False
        self.captured = False
        self.is_mother = False

        if parent_brain is not None:
            self.brain = parent_brain.copy()
            self.brain.mutate()
        else:
            self.brain = NeuralNetwork()

        # Mother brain for goal-setting
        if mother is None:
            if parent_mother_brain is not None:
                self.mother_brain = parent_mother_brain.copy()
            else:
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
        mother = self.mother
        if mother is not None and not mother.dead and mother.mother_brain is not None:
            offspring = mother.offspring
            total_hunger = 0
            alive_count = 0
            for o in offspring:
                if not o.dead:
                    total_hunger += o.hunger
                    alive_count += 1
            avg_hunger = total_hunger / max(1, alive_count)
            return mother.mother_brain.get_goals(
                mother.hunger,
                mother.point,
                alive_count,
                avg_hunger
            )
        return None

    def is_eatable_creature(self, other_creature):
        if other_creature is None or other_creature.dead:
            return False
        my_mother = self.mother if self.mother is not None else self
        other_mother = other_creature.mother if other_creature.mother is not None else other_creature
        if my_mother == other_mother:
            return False
        return other_creature.hunger >= _HUNGER_THRESHOLD

    def is_dangerous_creature(self, other_creature):
        """Check if another creature can capture/eat us."""
        if other_creature is None or other_creature.dead:
            return False
        my_mother = self.mother if self.mother is not None else self
        other_mother = other_creature.mother if other_creature.mother is not None else other_creature
        if my_mother == other_mother:
            return False
        # We're in danger if we're very hungry and from a different family
        return self.hunger >= _HUNGER_THRESHOLD

    def is_enemy_creature(self, other_creature):
        if other_creature is None or other_creature.dead:
            return False
        my_mother = self.mother if self.mother is not None else self
        other_mother = other_creature.mother if other_creature.mother is not None else other_creature
        return my_mother != other_mother

    def capture_food(self, dead=False, fats=50, eaten_creature=None):
        if dead:
            self.hunger = max(0, self.hunger - fats)
        else:
            self.hunger = max(0, self.hunger - 20)

        if eaten_creature is not None:
            eaten_creature.point = max(0, eaten_creature.point - fats)

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
        # Can move to: empty, food, dead creatures, or eatable living creatures
        if hex.content == Content.EMPTY or hex.content == Content.FOOD:
            return True
        if hex.content == Content.CREATURE and hex.creature:
            if hex.creature.dead and not hex.creature.captured:
                return True  # Can move to dead uncaptured creatures
            if self.is_eatable_creature(hex.creature):
                return True  # Can move to eatable living creatures
        return False

    def think(self):
        mother = self.mother
        if mother is not None and mother.dead:
            self.dead = True
            return

        if not self.dead:
            inputs = self._get_sensory_inputs()

            goals = self.get_mother_goals()
            if goals is not None:
                inputs.append(float(goals[0]))
                inputs.append(float(goals[1]))
                inputs.append(float(goals[2]))
            else:
                inputs.append(0.0)
                inputs.append(0.0)
                inputs.append(0.0)

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
            for dir_idx, col_d, row_d, has_food, has_enemy in valid_moves:
                if dir_idx == preferred_dir:
                    # Check if this move would revisit a recent position
                    new_col = self.col_index + col_d
                    new_row_key = self.row_key
                    if row_d != 0:
                        rows = self.grid.get_row_keys()
                        current_row_idx = self.grid.get_row_index(
                            self.row_key)  # O(1)
                        if current_row_idx >= 0:
                            new_row_idx = current_row_idx + row_d
                            if 0 <= new_row_idx < len(rows):
                                new_row_key = rows[new_row_idx]
                            pass
                    new_pos = (new_col, new_row_key)
                    if new_pos in self.position_history:
                        self.point = max(0, self.point - 10)
                        self.hunger = min(MAX_HUNGER, self.hunger + 3)
                        break

                    # Penalize for moving towards enemy creatures (different mother)
                    if has_enemy:
                        self.point = max(0, self.point - 8)
                        self.hunger = min(MAX_HUNGER, self.hunger + 2)

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
        rows = self.grid.get_row_keys()

        current_row_idx = self.grid.get_row_index(self.row_key)
        if current_row_idx < 0:
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
                            (content == Content.CREATURE and creature and creature.dead and not creature.captured) or
                            (content == Content.CREATURE and creature and self.is_eatable_creature(creature)))
                # Check if there's an enemy creature nearby in this direction
                has_enemy = (content == Content.CREATURE and creature and 
                             not creature.dead and self.is_enemy_creature(creature) and
                             not self.is_eatable_creature(creature))
                valid_moves.append((dir_idx, col_d, row_d, has_food, has_enemy))

        return valid_moves

    def _get_sensory_inputs(self):
        inputs = [0.0] * 24  # 6 neighbors * 4 values (content, edible, dangerous, enemy) = 24
        neighbors = self._get_neighbor_contents()

        Content_EMPTY = Content.EMPTY
        Content_FOOD = Content.FOOD
        Content_WALL = Content.WALL
        Content_CREATURE = Content.CREATURE
        is_eatable = self.is_eatable_creature
        is_dangerous_method = self.is_dangerous_creature
        is_enemy_method = self.is_enemy_creature

        idx = 0
        for content, creature in neighbors:
            # Encode content type: 0=empty, 0.5=food/dead, 1=wall/living creature
            if content == Content_EMPTY:
                content_val = 0.0
            elif content == Content_FOOD:
                content_val = 0.5
            elif content == Content_WALL:
                content_val = 1.0
            elif content == Content_CREATURE:
                content_val = 0.5 if (creature and creature.dead) else 1.0
            else:
                content_val = 0.0

            # Calculate is_edible
            is_edible = 0.0
            if content == Content_FOOD:
                is_edible = 1.0
            elif content == Content_CREATURE and creature:
                if creature.dead and not creature.captured:
                    is_edible = 1.0
                elif is_eatable(creature):
                    is_edible = 1.0

            # Calculate is_dangerous
            is_dangerous_val = 0.0
            if content == Content_CREATURE and creature and not creature.dead:
                if is_dangerous_method(creature):
                    is_dangerous_val = 1.0

            # Calculate is_enemy (creature from a different mother)
            is_enemy_val = 0.0
            if content == Content_CREATURE and creature and not creature.dead:
                if is_enemy_method(creature):
                    is_enemy_val = 1.0

            inputs[idx] = content_val
            inputs[idx + 1] = is_edible
            inputs[idx + 2] = is_dangerous_val
            inputs[idx + 3] = is_enemy_val
            idx += 4

        return inputs

    def _get_neighbor_contents(self):
        neighbors = []
        rows = self.grid.get_row_keys()

        current_row_idx = self.grid.get_row_index(self.row_key)
        if current_row_idx < 0:
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
            self.grid.update_empty_hex_tracking(
                self.col_index, self.row_key, True)
        new_col = self.col_index + col_delta
        if row_delta != 0:
            rows = self.grid.get_row_keys()
            current_row_index = self.grid.get_row_index(
                self.row_key)
            if current_row_index >= 0:
                new_row_index = current_row_index + row_delta
                if 0 <= new_row_index < len(rows):
                    new_row_key = rows[new_row_index]
                else:
                    new_row_key = self.row_key
            else:
                new_row_key = self.row_key
        else:
            new_row_key = self.row_key

        if self.can_move_to(new_col, new_row_key):
            self.col_index = new_col
            self.row_key = new_row_key

            current_pos = (self.col_index, self.row_key)
            if current_pos in self.position_history:
                self.position_history.remove(current_pos)
            self.position_history.append(current_pos)
            if len(self.position_history) > self.history_size:
                self.position_history.pop(0)

        new_hex = self.get_current_hex()
        if new_hex:
            dead = (new_hex.content ==
                    Content.CREATURE and new_hex.creature and new_hex.creature.dead and not new_hex.creature.captured)
            eatable_living = (new_hex.content == Content.CREATURE and new_hex.creature and
                              not new_hex.creature.dead and self.is_eatable_creature(new_hex.creature))
            if new_hex.content == Content.FOOD or dead or eatable_living:
                # how faty was the creature
                fats = 0
                eaten_creature = None
                if dead:
                    fats = new_hex.creature.point // 10
                    new_hex.creature.captured = True
                    eaten_creature = new_hex.creature
                elif eatable_living:
                    # Eating a living hungry creature from another mother
                    fats = new_hex.creature.point // 10
                    eaten_creature = new_hex.creature
                    new_hex.creature.dead = True
                    new_hex.creature.captured = True
                self.capture_food(dead or eatable_living, fats, eaten_creature)
            new_hex.content = Content.CREATURE
            new_hex.creature = self
            self.grid.update_empty_hex_tracking(
                self.col_index, self.row_key, False)
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
