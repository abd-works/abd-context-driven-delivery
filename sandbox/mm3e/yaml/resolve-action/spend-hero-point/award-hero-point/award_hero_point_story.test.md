---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Award Hero Point

**Evidence:** observed — HeroesHandbook.md lines 1471–1473 and 1534–1541. The Gamemaster awards hero points during the adventure. The handbook names complications, heroism, and roleplaying as sources. **Flagged** — the complication catalog is in Secret Origins, which this slice does not include.

### Domain terms

- ++Awarded Hero Point++ — a hero point the Gamemaster gives during the adventure

## Behaviors

#### Scenario: The Gamemaster awards a hero point for heroism

*Given* the **Player** has *1* ++Hero Point++
  *And* the hero has just acted heroically
*When* the **Gamemaster** awards a hero point
*Then* the **Player** has *2* hero points
  *And* the outcome continues in Reset Hero Point

#### Scenario: Roleplaying can earn a hero point

*Given* the **Player** has *1* ++Hero Point++
*When* the **Gamemaster** awards a hero point for roleplaying
*Then* the **Player** has *2* hero points

#### Scenario: A complication can earn a hero point

*Given* the **Player** has *0* hero points
  *And* a complication has come up in play
*When* the **Gamemaster** awards a hero point
*Then* the **Player** has *1* hero point

#### Scenario: The award raises the count during the adventure

*Given* the **Player** has *2* hero points in this adventure
*When* the **Gamemaster** awards a hero point
*Then* the **Player** has *3* hero points
  *And* the points remain until they are spent or the adventure ends
