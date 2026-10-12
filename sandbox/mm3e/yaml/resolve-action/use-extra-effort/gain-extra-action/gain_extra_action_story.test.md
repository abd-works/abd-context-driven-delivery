---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Gain Extra Action

**Evidence:** observed — HeroesHandbook.md lines 1429–1434. Extra effort is a free action, once per turn, and one benefit is an additional standard action.

### Domain terms

- ++Extra Effort++ — a free action, once on the hero's turn, that grants one benefit and fatigue on the next turn

## Behaviors

#### Scenario: Extra effort grants another standard action

*Given* it is the hero's turn
  *And* the hero has not used extra effort this turn
*When* the **Player** uses extra effort to gain an extra action
*Then* the hero gains one more standard action this turn
  *And* using extra effort spends a free action
  *And* the outcome continues in Gain Effort Bonus

#### Scenario: The extra standard action can become a move

*Given* extra effort has granted an additional standard action
*When* the **Player** exchanges that action for a move
*Then* the hero gains a move action
  *But* that extra action is not a standard action

#### Scenario: A second extra effort in the same turn does not happen

*Given* the hero has used extra effort this turn
*When* the **Player** uses extra effort again
*Then* the second extra effort does not happen
  *But* no second benefit is gained

#### Scenario: The benefit is not limited by power level

*Given* the hero is already at the series power level
*When* the **Player** uses extra effort to gain an extra action
*Then* the hero still gains the additional standard action
