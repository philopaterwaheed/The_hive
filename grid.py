import math
import random
from consts import HEX_SIZE, W, H, X_DIFF, Y_DIFF, X_OFFSET, EVOLUTION_SPAWN_INTERVAL, EVOLUTION_SPAWN_PROBABILITY
from hex import Hex, Content, COLORS
from creature import Creature


class Grid:

    hexs: dict[float, list] = {}
    creatures = []
    taken_colors = set()

    def __init__(self):
        self.evolution_tick_counter = 0
        self.best_mother = None
        toggle = False
        for y in range(HEX_SIZE, H-HEX_SIZE, int(HEX_SIZE * Y_DIFF)):
            for x in range(HEX_SIZE, W-HEX_SIZE, int(HEX_SIZE * X_DIFF)):
                if x <= (W - (2 * HEX_SIZE)) and y <= H - math.sqrt(3) * HEX_SIZE:
                    new_hex = Hex(x+(int(HEX_SIZE*X_OFFSET*(toggle))),
                                  y, HEX_SIZE)
                    self.add_hex(new_hex)
            toggle = not toggle
        self.generate_maze_cellular_automata()

    def add_hex(self, hex: Hex):
        if not self.hexs.get(hex.center_y):
            self.hexs[hex.center_y] = []
        self.hexs.get(hex.center_y).append(hex)

    def draw(self, screen):
        for raw in self.hexs.values():
            for hex in raw:
                hex.draw(screen)

    def move_creatures(self):
        for creature in self.creatures:
            creature.think()
            if creature.is_mother:
                self.update_best_mother_creature(creature)

    def remove_dead_creatures(self):
        """Remove creatures that are dead or have been captured"""
        creatures_to_remove = []

        for creature in self.creatures:
            if creature.dead and creature.captured:
                creatures_to_remove.append(creature)
        for creature in creatures_to_remove:
            self.creatures.remove(creature)
            # Also remove from mother's offspring list if applicable
            if creature.mother is not None and creature in creature.mother.offspring:
                creature.mother.offspring.remove(creature)
            if creature.is_mother and len(creature.offspring) == 0 or (creature.dead and not creature.is_mother and len(creature.mother.offspring) == 1):
                self.taken_colors.discard(creature.color)
                for child in creature.offspring:
                    child.mother = None
                creature.offspring.clear()

    def handle_reproduction(self):
        new_creatures = []
        for creature in self.creatures:
            if creature.can_reproduce():
                offspring = self.reproduce_creature(creature)
                if offspring:
                    new_creatures.append(offspring)
        self.creatures.extend(new_creatures)

    def reproduce_creature(self, parent):
        # Find an empty adjacent hex
        parent_hex = parent.get_current_hex()
        if not parent_hex:
            return None

        rows = list(self.hexs.keys())
        try:
            current_row_idx = rows.index(parent.row_key)
        except ValueError:
            return None

        row = self.hexs[parent.row_key]
        is_even_row = current_row_idx % 2 == 0

        # empty spaces
        adjacent_positions = []

        # Left and right
        if parent.col_index > 0:
            adjacent_positions.append((parent.col_index - 1, parent.row_key))
        if parent.col_index < len(row) - 1:
            adjacent_positions.append((parent.col_index + 1, parent.row_key))

        # Previous row
        if current_row_idx > 0:
            prev_y = rows[current_row_idx - 1]
            prev_row = self.hexs[prev_y]
            if is_even_row:
                if parent.col_index < len(prev_row):
                    adjacent_positions.append((parent.col_index, prev_y))
                if parent.col_index > 0:
                    adjacent_positions.append((parent.col_index - 1, prev_y))
            else:
                if parent.col_index < len(prev_row):
                    adjacent_positions.append((parent.col_index, prev_y))
                if parent.col_index + 1 < len(prev_row):
                    adjacent_positions.append((parent.col_index + 1, prev_y))

        # Next row
        if current_row_idx < len(rows) - 1:
            next_y = rows[current_row_idx + 1]
            next_row = self.hexs[next_y]
            if is_even_row:
                if parent.col_index < len(next_row):
                    adjacent_positions.append((parent.col_index, next_y))
                if parent.col_index > 0:
                    adjacent_positions.append((parent.col_index - 1, next_y))
            else:
                if parent.col_index < len(next_row):
                    adjacent_positions.append((parent.col_index, next_y))
                if parent.col_index + 1 < len(next_row):
                    adjacent_positions.append((parent.col_index + 1, next_y))

        # Shuffle to randomize spawn position
        random.shuffle(adjacent_positions)

        # Find first empty position
        for col_idx, row_key in adjacent_positions:
            row = self.hexs[row_key]
            if 0 <= col_idx < len(row):
                hex = row[col_idx]
                if hex.content == Content.EMPTY:
                    if parent.reproduce():
                        if parent.mother:
                            mother = parent.mother
                        else:
                            mother = parent
                        # Pass parent's brain for inheritance, link to root mother
                        offspring = Creature(
                            self, col_idx, row_key, parent_brain=parent.brain, mother=mother)
                        offspring.color = parent.color
                        mother.offspring.append(offspring)
                        hex.content = Content.CREATURE
                        hex.creature = offspring
                        return offspring
        return None

    def add_creature(self, x, y):
        i, y = self.get_hex_pos(x, y) or (-1, -1)
        if i > -1 and y > -1 and self.hexs[y][i].content == Content.EMPTY:
            # Get all existing creature colors
            creature = Creature(self, i, y, self.taken_colors)
            creature.is_mother = True  # Mark user-created creatures as mothers
            self.creatures.append(creature)
            # Mark the hex as filled
            self.hexs[y][i].content = Content.CREATURE
            self.hexs[y][i].creature = creature

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

    def generate_maze_cellular_automata(self, wall_probability=0.45, iterations=5):
        for row in self.hexs.values():
            for hex in row:
                if random.random() < wall_probability:
                    hex.content = Content.WALL
                    hex.fill = True
                else:
                    hex.content = Content.EMPTY
                    hex.fill = False

        for _ in range(iterations):
            self._apply_ca_rules()

    def _apply_ca_rules(self):
        new_states = {}

        for y_coord, row in self.hexs.items():
            new_states[y_coord] = []
            for i, hex in enumerate(row):
                wall_count = self._count_wall_neighbors(i, y_coord)

                # Apply rules
                if hex.content == Content.WALL:
                    # Wall becomes passage if too few wall neighbors
                    new_content = Content.EMPTY if wall_count < 3 else Content.WALL
                else:
                    # Passage becomes wall if too many wall neighbors
                    new_content = Content.WALL if wall_count >= 5 else Content.EMPTY

                # Occasionally add food to empty cells
                if new_content == Content.EMPTY and random.random() < 0.1:
                    new_content = Content.FOOD

                new_states[y_coord].append(new_content)

        # Apply new states
        for y_coord, row in self.hexs.items():
            for i, hex in enumerate(row):
                hex.content = new_states[y_coord][i]
                hex.color = COLORS[hex.content]
                hex.fill = hex.content != Content.EMPTY

    def _count_wall_neighbors(self, col_index, y_coord):
        count = 0
        row = self.hexs[y_coord]

        rows = list(self.hexs.keys())
        current_row_idx = rows.index(y_coord)

        # Todo you can do better than this
        is_even_row = current_row_idx % 2 == 0

        if col_index > 0 and row[col_index - 1].content == Content.WALL:
            count += 1
        if col_index < len(row) - 1 and row[col_index + 1].content == Content.WALL:
            count += 1

        # Previous row (up-left, up-right)
        if current_row_idx > 0:
            prev_y = rows[current_row_idx - 1]
            prev_row = self.hexs[prev_y]

            if is_even_row:
                # Even row: check col and col-1
                if col_index < len(prev_row) and prev_row[col_index].content == Content.WALL:
                    count += 1
                if col_index > 0 and prev_row[col_index - 1].content == Content.WALL:
                    count += 1
            else:
                # Odd row: check col and col+1
                if col_index < len(prev_row) and prev_row[col_index].content == Content.WALL:
                    count += 1
                if col_index + 1 < len(prev_row) and prev_row[col_index + 1].content == Content.WALL:
                    count += 1

        # Next row (down-left, down-right)
        if current_row_idx < len(rows) - 1:
            next_y = rows[current_row_idx + 1]
            next_row = self.hexs[next_y]

            if is_even_row:
                # Even row: check col and col-1
                if col_index < len(next_row) and next_row[col_index].content == Content.WALL:
                    count += 1
                if col_index > 0 and next_row[col_index - 1].content == Content.WALL:
                    count += 1
            else:
                # Odd row: check col and col+1
                if col_index < len(next_row) and next_row[col_index].content == Content.WALL:
                    count += 1
                if col_index + 1 < len(next_row) and next_row[col_index + 1].content == Content.WALL:
                    count += 1

        return count

    def update_best_mother_creature(self, creature):
        if self.best_mother is None or creature.point > self.best_mother.point:
            self.best_mother = creature

    def find_empty_spawn_location(self):
        empty_locations = []

        for y_coord, row in self.hexs.items():
            for i, hex in enumerate(row):
                if hex.content == Content.EMPTY:
                    empty_locations.append((i, y_coord))

        if empty_locations:
            return random.choice(empty_locations)
        return None

    def handle_evolution_spawn(self):
        self.evolution_tick_counter += 1

        # Check if it's time to consider spawning an evolved creature
        if self.evolution_tick_counter >= EVOLUTION_SPAWN_INTERVAL:
            self.evolution_tick_counter = 0

            if random.random() < EVOLUTION_SPAWN_PROBABILITY:
                best_creature = self.best_mother
                if best_creature is None:
                    best_creature = Creature(self, 0, 0, self.taken_colors)
                spawn_location = self.find_empty_spawn_location()

                if best_creature and spawn_location:
                    col_idx, row_key = spawn_location

                    # Create evolved creature using best creature's brain and mother brain
                    evolved_creature = Creature(
                        self, col_idx, row_key,
                        self.taken_colors,
                        parent_brain=best_creature.brain,
                        parent_mother_brain=best_creature.mother_brain
                    )

                    # Apply additional evolution pressure - extra mutations for more variation
                    evolved_creature.brain.mutate(
                        rate=0.2, strength=0.5)  # Stronger mutations
                    # Second round of mutations
                    evolved_creature.brain.mutate(rate=0.15, strength=0.4)

                    # Also apply extra mutations to the mother brain for goal evolution
                    if evolved_creature.mother_brain is not None:
                        evolved_creature.mother_brain.mutate(
                            rate=0.2, strength=0.5)
                        evolved_creature.mother_brain.mutate(
                            rate=0.15, strength=0.4)
                    evolved_creature.is_mother = True

                    self.creatures.append(evolved_creature)
                    hex = self.hexs[row_key][col_idx]
                    hex.content = Content.CREATURE
                    hex.creature = evolved_creature

                    return evolved_creature

        return None
