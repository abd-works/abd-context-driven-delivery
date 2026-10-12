---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Take Move Action

**Evidence:** observed — HeroesHandbook.md lines 1230–1234. The move can come before or after the standard action. It cannot be split around the standard action. Drawing a weapon, standing up, and picking up an object are move actions.

### Domain terms

- ++Move Action++ — one move in the round, taken whole before or after the standard action

## Behaviors

#### Scenario: The character moves and then takes the standard action

*Given* it is the ++Character++'s turn
  *But* neither the move nor the standard action has been taken
*When* the **Player** takes the move action
*Then* the move happens before the standard action
  *And* the standard action is still available
  *And* the outcome continues in Take Free Action

#### Scenario: The character takes the standard action and then moves

*Given* the ++Character++ has taken the standard action
  *But* the move action has not been taken
*When* the **Player** takes the move action
*Then* the move happens after the standard action

#### Scenario: The move is not split around the standard action

*Given* the ++Character++ has used part of the move
*When* the **Player** takes the standard action and then the rest of that same move
*Then* the split move does not happen
  *And* the move stays one action on one side of the standard action

#### Scenario Outline: Other move actions use the same allotment

*Given* it is the ++Character++'s turn and the move action is available
*When* the **Player** takes a move action to {action}
*Then* the {action} spends the move action

#### Examples

| scenario | action |
| --- | --- |
| ++draw++ | draw a weapon |
| ++stand++ | stand up |
| ++pick up++ | pick up an object |
