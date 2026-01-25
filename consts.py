W, H = 1800, 900
HEX_SIZE = 10
X_DIFF, Y_DIFF, X_OFFSET = 1.75, 1.51, 0.87
MAX_HUNGER = 500
REPRODUCTION_THRESHOLD = 250  # Hunger needed to reproduce (lowered to encourage faster reproduction)
REPRODUCTION_COST = 5  # Hunger cost to reproduce (lowered to make reproduction easier)
# Probability of reproduction when conditions are met
REPRODUCTION_PROBABILITY = 0.15  # Increased to encourage more offspring

# Neural Network Constants
MUTATION_RATE = 0.15  # Increased mutation rate for more diversity
MUTATION_STRENGTH = 0.4  # Increased mutation strength for exploration behavior

# Evolution Spawn Constants
EVOLUTION_SPAWN_INTERVAL = 1  # Number of ticks between evolution spawn attempts
# Probability of spawning evolved creature when interval reached
EVOLUTION_SPAWN_PROBABILITY = 0.5

# Toxin Constants
TOXIN_DAMAGE = 100  # Hunger damage when stepping on a toxin
# Probability of spawning a toxin per tick per empty hex (low to keep rare)
TOXIN_SPAWN_PROBABILITY = 0.01
TOXIN_SPAWN_INTERVAL = 10  # Number of ticks between toxin spawn attempts

# Colony Behavior Constants
EXPLORATION_REWARD = 8  # Reward for moving to unexplored areas
FAMILY_PROXIMITY_PENALTY = 12  # Penalty for being too close to family members
FAMILY_PROXIMITY_THRESHOLD = 3  # Distance threshold for proximity penalty
DISTANCE_FROM_MOTHER_BONUS = 5  # Bonus for being far from mother
