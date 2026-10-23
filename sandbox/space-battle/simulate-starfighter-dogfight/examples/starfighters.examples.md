---
fidelity: specification
artifact: story-scenarios
format: md
section: examples
---

# Shared examples — Simulate Starfighter Dogfight

Shared by every story in the epic. All values are **intended** (proposed for the walking skeleton, not confirmed by the user).

### Domain terms

- ++Engagement++ — one battle; the aggregate root. Owns the ++Arena++, its ++Starfighters++, and the current ++Turn++.
- ++Arena++ — the 2D grid the battle is fought on. Cells run from *(0,0)* to *(19,19)*.
- ++Starfighter++ — one craft in the engagement, with a ++Starfighter Type++, ++Position++, ++Heading++, ++Speed++ and ++Hull++.
- ++Starfighter Type++ — X-wing or TIE fighter; fixes top speed, max turn, hull and lasers.
- ++Position++ — a cell *(x,y)*. x grows to the east, y grows to the north.
- ++Heading++ — compass degrees in 45° steps: *0* north, *90* east, *180* south, *270* west.
- ++Speed++ — cells moved per activation; set by throttle, capped at the type's top speed.
- ++Turn++ — one round in which every surviving starfighter activates once, fastest first.
- ++Activation++ — one starfighter's slot in a turn: its pilot commits ++Activation Orders++, then the Simulation Engine applies them.
- ++Activation Orders++ — throttle, turn (degrees left or right) and an optional laser target.
- ++Range++ — distance between two positions in cells, counting a diagonal step as one cell.
- ++Firing Arc++ — the 90° cone ahead of a starfighter (heading ± 45°).

### Starfighter Types

| Type | Top speed | Max turn per activation | Hull | Laser range | Laser damage | Firing arc |
|------|-----------|-------------------------|------|-------------|--------------|------------|
| X-wing | *4* | *90°* | *4* | *3* | *1* | *90°* |
| TIE fighter | *5* | *135°* | *3* | *3* | *1* | *90°* |

### Starfighters

| Name | Type | Flown by | Start position | Start heading |
|------|------|----------|----------------|---------------|
| ++Red Five++ | X-wing | Pilot (the person) | *(2,10)* | *90* (east) |
| ++Black Two++ | TIE fighter | AI Pilot | *(17,10)* | *270* (west) |

### Engagement

| Name | Arena | Starfighters |
|------|-------|--------------|
| ++Dogfight One++ | 20 × 20 | ++Red Five++, ++Black Two++ |
