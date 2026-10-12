---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Request Inspiration

**Evidence:** observed — HeroesHandbook.md lines 1521–1523. A hero point buys a significant hint, clue, or bit of help from the Gamemaster. How it manifests is the Gamemaster's choice. **Intended** — the Simulator records the spent point and presents the hint the Gamemaster supplies.

### Domain terms

- ++Inspiration++ — a hint, clue, or help the Gamemaster gives for a hero point

## Behaviors

#### Scenario: The Gamemaster gives a significant hint

*Given* the heroes are stuck in a deathtrap
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** requests inspiration
*Then* the **Gamemaster** gives a significant way out
  *And* the **Player** has *0* hero points
  *And* the outcome continues in Counter Effect

#### Scenario: Inspiration can be a clue

*Given* the heroes are solving a mystery
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** requests inspiration
*Then* the **Gamemaster** gives a vital clue
  *And* the **Player** has *0* hero points

#### Scenario: The hint is the one the Gamemaster chooses

*Given* the **Player** has asked for inspiration
*When* the **Gamemaster** chooses how the help manifests
*Then* the help is the hint the Gamemaster states

#### Scenario: No hero point means no inspiration

*Given* the **Player** has *0* hero points
*When* the **Player** requests inspiration
*Then* the **Gamemaster** does not give a hint
