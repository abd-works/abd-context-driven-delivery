---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Take Standard Action

**Evidence:** observed — HeroesHandbook.md lines 1226–1228. A standard action acts upon something, such as an attack or a power. One standard action each round. It can be traded for a move action.

### Domain terms

- ++Standard Action++ — one action in the round that acts upon something

## Behaviors

#### Scenario: The character takes one standard action

*Given* it is the ++Character++'s turn in the ++Action Round++
  *But* the character has not taken a standard action this turn
*When* the **Player** takes a standard action to attack
*Then* the attack is the character's standard action
  *And* the move action is still available
  *And* the outcome continues in Take Move Action

#### Scenario: A second standard action is not available

*Given* the ++Character++ has taken a standard action this turn
*When* the **Player** takes another standard action
*Then* the second standard action does not happen
  *But* the turn has no standard action left

#### Scenario: The standard action can be traded for a move

*Given* it is the ++Character++'s turn
  *But* the character has not taken a standard action
*When* the **Player** takes a move action in place of the standard action
*Then* the character has a second move action
  *But* no standard action remains

#### Scenario: Using a power on something is a standard action

*Given* it is the ++Character++'s turn
  *But* the character has not taken a standard action
*When* the **Player** uses a power to affect something
*Then* that use is the standard action
