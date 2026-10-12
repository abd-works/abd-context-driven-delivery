---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Grant Session Hero Point

**Evidence:** observed — HeroesHandbook.md lines 1471–1478. Each session starts with 1 hero point. Spending one is a reaction and takes no time. The player can spend as many as they have.

### Domain terms

- ++Hero Point++ — a point the player spends as a reaction

## Behaviors

#### Scenario: The session starts with one hero point

*Given* a game session is beginning
*When* the **Simulator** grants the session hero point
*Then* the **Player** has *1* ++Hero Point++
  *And* the outcome continues in Edit Scene

#### Scenario: Spending a hero point is a reaction

*Given* the **Player** has *1* ++Hero Point++
  *And* it is not the hero's turn
*When* the **Player** spends a hero point
*Then* the spend happens as a reaction
  *And* the **Player** has *0* hero points
  *And* the standard action is not spent

#### Scenario: The player can spend every hero point they have

*Given* the **Player** has *2* hero points
*When* the **Player** spends both hero points
*Then* both spends happen
  *And* the **Player** has *0* hero points

#### Scenario: A player with no hero point cannot spend one

*Given* the **Player** has *0* hero points
*When* the **Player** spends a hero point
*Then* no hero point is spent
