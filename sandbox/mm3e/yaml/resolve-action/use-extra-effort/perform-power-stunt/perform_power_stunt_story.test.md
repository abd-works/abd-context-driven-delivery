---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Perform Power Stunt

**Evidence:** observed — HeroesHandbook.md lines 1453–1455. A power stunt grants an Alternate Effect until the end of the scene or until that effect's duration ends. Permanent effects cannot be used. **Flagged** — how an Alternate Effect is built is in the Powers chapter, which this slice does not include.

### Domain terms

- ++Power Stunt++ — a temporary Alternate Effect gained through extra effort

## Behaviors

#### Scenario: The hero gains an Alternate Effect until the scene ends

*Given* a hero has a non-permanent power effect
  *And* the hero has not used extra effort this turn
*When* the **Player** uses extra effort to perform a power stunt
*Then* the hero gains an Alternate Effect
  *And* the Alternate Effect lasts until the end of the scene
  *And* the outcome continues in Gain Extra Resistance Check

#### Scenario: The stunt ends when its duration ends first

*Given* the power stunt's duration ends before the scene ends
*When* the **Simulator** reaches the end of that duration
*Then* the Alternate Effect ends
  *And* the scene is still going

#### Scenario: A permanent effect cannot be used for a power stunt

*Given* the only effect offered for the stunt is permanent
*When* the **Player** uses extra effort to perform a power stunt with that effect
*Then* the hero does not gain an Alternate Effect

#### Scenario: The stunt lasts through the scene when the duration is longer

*Given* the Alternate Effect's duration is longer than the scene
*When* the **Simulator** reaches the end of the scene
*Then* the Alternate Effect ends with the scene
