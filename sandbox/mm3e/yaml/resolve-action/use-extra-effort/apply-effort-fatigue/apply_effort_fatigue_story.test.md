---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Apply Effort Fatigue

**Evidence:** observed — HeroesHandbook.md lines 1305 and 1487–1489. At the start of the next turn the hero is fatigued. Fatigued extra effort becomes exhausted. Exhausted extra effort becomes incapacitated. A hero point at the start of that turn removes the fatigue. Fatigued characters are hindered.

### Domain terms

- ++Effort Fatigue++ — the fatigued condition that follows extra effort

## Behaviors

#### Scenario: The next turn starts with fatigue

*Given* a hero used extra effort on the previous turn
  *But* the hero has not spent a hero point to remove that fatigue
*When* the **Simulator** starts the hero's next turn
*Then* the hero is fatigued
  *And* the hero is hindered
  *And* the outcome continues in Grant Session Hero Point

#### Scenario: A fatigued hero who uses extra effort becomes exhausted

*Given* a hero is fatigued
*When* the **Player** uses extra effort
*Then* the hero becomes exhausted when that effort's cost is applied
  *And* exhausted is impaired and hindered

#### Scenario: An exhausted hero who uses extra effort is incapacitated

*Given* a hero is exhausted
*When* the **Player** uses extra effort
*Then* the hero becomes incapacitated when that effort's cost is applied

#### Scenario: A hero point removes the fatigue

*Given* a hero used extra effort on the previous turn
  *And* the hero has a hero point
*When* the **Player** spends a hero point at the start of the next turn
*Then* the hero is not fatigued
  *And* the hero point is spent

#### Scenario: An hour of rest removes fatigue

*Given* a hero is fatigued
*When* the hero rests for *1 hour*
*Then* the hero is no longer fatigued

#### Scenario: An hour of comfortable rest removes exhausted

*Given* a hero is exhausted
*When* the hero rests for *1 hour* in comfortable surroundings
*Then* the hero is no longer exhausted
