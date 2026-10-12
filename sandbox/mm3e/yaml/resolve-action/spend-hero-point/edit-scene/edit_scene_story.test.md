---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Edit Scene

**Evidence:** observed — HeroesHandbook.md lines 1482–1499. A hero point can add or change a detail that has not already been stated, such as defoliant chemicals in the lab. It cannot change an event that already happened or a detail already explained. The Gamemaster can refuse an edit that ruins the adventure.

### Domain terms

- ++Scene Edit++ — a detail the player adds by spending a hero point

## Behaviors

#### Scenario: A hero point adds a detail the scene has not stated

*Given* the hero is fighting a plant-powered villain in a lab
  *But* nobody has said whether defoliant chemicals are there
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** edits the scene to add defoliant chemicals
*Then* the chemicals are close at hand
  *And* the **Player** has *0* hero points
  *And* the outcome continues in Perform Heroic Feat

#### Scenario: A detail already explained stays as explained

*Given* the Gamemaster has already said the lab has no useful chemicals
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** edits the scene to add defoliant chemicals
*Then* the lab still has no useful chemicals
  *And* the **Player** still has *1* hero point

#### Scenario: Damage that already happened is not edited away

*Given* the hero has already taken damage
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** edits the scene to remove that damage
*Then* the damage remains
  *And* the **Player** still has *1* hero point

#### Scenario: The Gamemaster can refuse an edit that ruins the adventure

*Given* the edit would make the adventure trivial
  *And* the **Player** has *1* ++Hero Point++
*When* the **Gamemaster** refuses the scene edit
*Then* the detail is not added
  *And* the **Player** still has *1* hero point
