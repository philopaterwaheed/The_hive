# <img width="40" height="40" style="padding:24px;" alt="the_hive" src="https://github.com/user-attachments/assets/8cb182e5-b978-495e-8ccd-5e1321cbe3f0" /> The Hive

**⬡ Neural evolution meets emergent intelligence**: Watch AI colonies compete for survival on a hexagonal battlefield.



https://github.com/user-attachments/assets/b005a1d1-f205-4490-afc8-2a89db208105




## What It Is

A real-time ecosystem simulation where organisms controlled by dual neural networks evolve strategies, coordinate as hive minds, and adapt to survive. Built from scratch in Python with custom spatial systems and evolutionary algorithms.

## Core Technical Features


 **⬡ Dual-Brain Architecture**
- **MotherBrain** (4→3 network): Generates colony-level strategies for offspring
- **CreatureBrain** (33→7 network): Processes hexagonal environment + mother's goals
- Emergent coordination through shared reward pools

**⬡ Evolutionary System**
- Genetic algorithms with mutation-based adaptation
- Natural selection via hunger, toxins, and predation
- Best-performer persistence and evolution spawning

**⬡ Custom Hexagonal Grid**
- Efficient neighbor calculations for hex topology
- Dirty-rectangle rendering optimization
- **Cellular automata maze generation** — procedural environments using Conway-style rules adapted for hex grids
- O(1) spawn location via empty-hex tracking

**⬡ Performance Optimizations**
- NumPy buffers to minimize allocations
- `__slots__` for memory-efficient instances
- Cached spatial lookups
- Multi-process architecture (simulation + UI)

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

**⬡ Controls:**
- Click: Spawn creature
- `O`: Toggle options (still not implemented)
- `Q`: Save best creature & quit

## Architecture Highlights

```
brain.py       → Neural network implementations (Mother + Creature)
creature.py    → Agent logic with 6-position history, proximity detection
grid.py        → Hex grid manager with cellular automata & evolutionary spawning
hex.py         → Spatial primitives & content types
main.py        → Multi-process orchestration
```

**⬡ Key Design Decisions:**
- **Hexagonal grid** enables richer movement than square tiles
- **Cellular automata** creates dynamic, organic maze structures each run
- **Dual-brain hierarchy** creates emergent hive behaviors
- Position history (6 moves) prevents cycling without complex pathfinding
- Shared point pools incentivize family cooperation

## What Makes This Different

Most evolution sims use fitness functions. This uses **behavioral goals** — mothers dynamically guide offspring based on colony state (hunger levels, population), creating adaptive strategies that emerge rather than being hardcoded.

The combination of **procedurally-generated hex mazes** + **hierarchical neural control** creates unique challenges every session where colonies must adapt both genetically and behaviorally.

---

**⬡ Tech Stack:** Python • NumPy • Pygame • Multiprocessing  
**⬡ License:** MIT
