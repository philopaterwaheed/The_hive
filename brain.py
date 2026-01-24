import numpy as np
import random
from consts import MUTATION_RATE, MUTATION_STRENGTH


class NeuralNetwork:
    """
    A simple feedforward neural network for creature decision-making.
    Inputs (14 total):
        - 6 hex neighbors: each encoded as [content_type, is_food]
          where content_type: 0=passable, 1=blocked
        - Current hunger level (normalized)
        - Current points (normalized)
    Outputs (7 total):
        - 6 direction preferences (one for each hex neighbor)
        - Stay preference
    """

    def __init__(self, input_size=14, hidden_sizes=None, output_size=7):
        if hidden_sizes is None:
            hidden_sizes = [16, 12]

        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size

        # Initialize weights and biases
        self.weights = []
        self.biases = []

        layer_sizes = [input_size] + hidden_sizes + [output_size]

        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            w = np.random.randn(
                layer_sizes[i], layer_sizes[i + 1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros(layer_sizes[i + 1])
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, inputs):
        x = np.array(inputs, dtype=np.float32)

        for i in range(len(self.weights) - 1):
            x = np.dot(x, self.weights[i]) + self.biases[i]
            x = np.maximum(0, x)  # ReLU

        x = np.dot(x, self.weights[-1]) + self.biases[-1]
        x = np.tanh(x)

        return x

    def decide(self, inputs):
        outputs = self.forward(inputs)

        # Return the index of the highest output (preferred direction)
        return int(np.argmax(outputs))

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
