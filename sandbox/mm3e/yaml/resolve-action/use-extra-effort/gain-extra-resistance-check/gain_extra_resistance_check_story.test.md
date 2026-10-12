---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Gain Extra Resistance Check

**Evidence:** observed — HeroesHandbook.md lines 1457–1459. Extra effort grants an immediate extra resistance check against an ongoing effect. While compelled or controlled, the fatigue waits until the character is free.

### Domain terms

- ++Extra Resistance Check++ — one more resistance check, taken immediately, from extra effort

## Behaviors

#### Scenario: The hero immediately checks resistance again

*Given* an ongoing effect still affects the hero
  *And* the hero has not used extra effort this turn
*When* the **Player** uses extra effort to gain an extra resistance check
*Then* the hero rolls a ++Resistance Check++ against that effect now
  *And* the outcome continues in Retry Failed Effect

#### Scenario: Fatigue waits while the hero is compelled

*Given* the hero is compelled
  *And* the hero uses extra effort for an extra resistance check
*When* the **Simulator** reaches the start of the hero's next turn
*Then* the hero is not fatigued yet
  *And* the fatigue applies when the hero is no longer compelled

#### Scenario: Fatigue waits while the hero is controlled

*Given* the hero is controlled
  *And* the hero uses extra effort for an extra resistance check
*When* the **Simulator** reaches the start of the hero's next turn
*Then* the hero is not fatigued yet
  *And* the fatigue applies when the hero is no longer controlled

#### Scenario: A free hero is fatigued on the next turn

*Given* the hero is not compelled or controlled
  *And* the hero used extra effort for an extra resistance check
*When* the **Simulator** reaches the start of the hero's next turn
*Then* the hero is fatigued
