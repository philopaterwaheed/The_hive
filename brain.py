import numpy as np
import random
from consts import MUTATION_RATE, MUTATION_STRENGTH, MAX_HUNGER

_MOTHER_INPUT_BUFFER = np.zeros(4, dtype=np.float32)
_CREATURE_INPUT_BUFFER = np.zeros(33, dtype=np.float32)


class MotherBrain:
    """
    Inputs (4 total):
        - Mother's hunger level (normalized)
        - Mother's points (normalized)
        - Number of offspring (normalized)
        - Average offspring hunger (normalized)

    Outputs (3 total - goal signals):
        - Food priority (how much offspring should prioritize food)
        - Exploration (how much offspring should explore)
        - Safety (how cautious offspring should be)
    """
    __slots__ = ('input_size', 'hidden_sizes',
                 'output_size', 'weights', 'biases')

    def __init__(self, input_size=4, hidden_sizes=None, output_size=3):
        if hidden_sizes is None:
            hidden_sizes = [8, 6]

        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size

        self.weights = []
        self.biases = []

        layer_sizes = [input_size] + hidden_sizes + [output_size]

        for i in range(len(layer_sizes) - 1):
            w = (np.random.randn(layer_sizes[i], layer_sizes[i + 1]) *
                 np.sqrt(2.0 / layer_sizes[i])).astype(np.float32)
            b = np.zeros(layer_sizes[i + 1], dtype=np.float32)
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, inputs):
        x = np.asarray(inputs, dtype=np.float32)

        for i in range(len(self.weights) - 1):
            x = np.dot(x, self.weights[i]) + self.biases[i]
            np.maximum(x, 0, out=x)  # ReLU

        x = np.dot(x, self.weights[-1]) + self.biases[-1]
        return np.tanh(x)

    def get_goals(self, mother_hunger, mother_points, num_offspring, avg_offspring_hunger):
        _MOTHER_INPUT_BUFFER[0] = mother_hunger / MAX_HUNGER
        _MOTHER_INPUT_BUFFER[1] = min(mother_points / 100.0, 1.0)
        _MOTHER_INPUT_BUFFER[2] = min(num_offspring / 10.0, 1.0)
        _MOTHER_INPUT_BUFFER[3] = avg_offspring_hunger / \
            MAX_HUNGER if num_offspring > 0 else 0.0
        return self.forward(_MOTHER_INPUT_BUFFER)

    def copy(self):
        new_brain = MotherBrain(
            self.input_size, self.hidden_sizes.copy(), self.output_size)
        new_brain.weights = [w.copy() for w in self.weights]
        new_brain.biases = [b.copy() for b in self.biases]
        return new_brain

    def mutate(self, rate=None, strength=None):
        if rate is None:
            rate = MUTATION_RATE
        if strength is None:
            strength = MUTATION_STRENGTH

        for i in range(len(self.weights)):
            mask = np.random.random(self.weights[i].shape) < rate
            mutations = np.random.randn(*self.weights[i].shape) * strength
            self.weights[i] += mask * mutations

            mask = np.random.random(self.biases[i].shape) < rate
            mutations = np.random.randn(*self.biases[i].shape) * strength
            self.biases[i] += mask * mutations


class NeuralNetwork:
    """
    A simple feedforward neural network for creature decision-making.
    Inputs (33 total):
        - 6 hex neighbors: each encoded as [content_type, is_food, is_dangerous, is_enemy, is_toxin]
          where content_type: 0=passable, 1=blocked
          is_food: 1 if edible, 0 otherwise
          is_dangerous: 1 if creature can capture us, 0 otherwise
          is_enemy: 1 if creature from different mother, 0 otherwise
          is_toxin: 1 if hex contains toxin, 0 otherwise
        - 3 goal signals from mother (food priority, exploration, safety)
    Outputs (7 total):
        - 6 direction preferences (one for each hex neighbor)
        - Stay preference
    """
    __slots__ = ('input_size', 'hidden_sizes',
                 'output_size', 'weights', 'biases')

    def __init__(self, input_size=33, hidden_sizes=None, output_size=7):
        if hidden_sizes is None:
            hidden_sizes = [24, 16]

        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size

        # Initialize weights and biases
        self.weights = []
        self.biases = []

        layer_sizes = [input_size] + hidden_sizes + [output_size]

        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            w = (np.random.randn(layer_sizes[i], layer_sizes[i + 1]) *
                 np.sqrt(2.0 / layer_sizes[i])).astype(np.float32)
            b = np.zeros(layer_sizes[i + 1], dtype=np.float32)
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, inputs):
        x = np.asarray(inputs, dtype=np.float32)

        for i in range(len(self.weights) - 1):
            x = np.dot(x, self.weights[i]) + self.biases[i]
            np.maximum(x, 0, out=x)  # In-place ReLU

        x = np.dot(x, self.weights[-1]) + self.biases[-1]
        return np.tanh(x)

    def decide(self, inputs):
        x = np.asarray(inputs, dtype=np.float32)

        weights = self.weights
        biases = self.biases
        num_hidden = len(weights) - 1

        for i in range(num_hidden):
            x = np.dot(x, weights[i]) + biases[i]
            np.maximum(x, 0, out=x)  # In-place ReLU

        x = np.dot(x, weights[-1]) + biases[-1]
        return int(np.argmax(np.tanh(x)))

    def copy(self):
        new_nn = NeuralNetwork(
            self.input_size, self.hidden_sizes.copy(), self.output_size)
        new_nn.weights = [w.copy() for w in self.weights]
        new_nn.biases = [b.copy() for b in self.biases]
        return new_nn

    def mutate(self, rate=None, strength=None):
        if rate is None:
            rate = MUTATION_RATE
        if strength is None:
            strength = MUTATION_STRENGTH

        for i in range(len(self.weights)):
            mask = np.random.random(self.weights[i].shape) < rate
            mutations = np.random.randn(*self.weights[i].shape) * strength
            self.weights[i] += mask * mutations

            # Mutate biases
            mask = np.random.random(self.biases[i].shape) < rate
            mutations = np.random.randn(*self.biases[i].shape) * strength
            self.biases[i] += mask * mutations

    def crossover(self, other):

        child = self.copy()

        for i in range(len(child.weights)):
            # Randomly select weights from either parent
            mask = np.random.random(child.weights[i].shape) < 0.5
            child.weights[i] = np.where(
                mask, self.weights[i], other.weights[i])

            # Same for biases
            mask = np.random.random(child.biases[i].shape) < 0.5
            child.biases[i] = np.where(mask, self.biases[i], other.biases[i])

        return child
