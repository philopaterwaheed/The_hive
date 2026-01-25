W, H = 1800, 900
HEX_SIZE = 10
X_DIFF, Y_DIFF, X_OFFSET = 1.75, 1.51, 0.87
MAX_HUNGER = 500
REPRODUCTION_THRESHOLD = 300  # Hunger needed to reproduce
REPRODUCTION_COST = 10  # Hunger cost to reproduce
# Probability of reproduction when conditions are met
REPRODUCTION_PROBABILITY = 0.1

# Neural Network Constants
MUTATION_RATE = 0.1  # Probability of each weight being mutated
MUTATION_STRENGTH = 0.3  # Standard deviation of mutations

# Evolution Spawn Constants
EVOLUTION_SPAWN_INTERVAL = 1  # Number of ticks between evolution spawn attempts
# Probability of spawning evolved creature when interval reached
EVOLUTION_SPAWN_PROBABILITY = 0.5

# Toxin Constants
TOXIN_DAMAGE = 100  # Hunger damage when stepping on a toxin
# Probability of spawning a toxin per tick per empty hex (low to keep rare)
TOXIN_SPAWN_PROBABILITY = 0.01
TOXIN_SPAWN_INTERVAL = 10  # Number of ticks between toxin spawn attempts
