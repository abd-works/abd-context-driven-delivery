---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Take Free Action

**Evidence:** observed — HeroesHandbook.md lines 1235–1238. Free actions are minor. The character can take as many as the Gamemaster considers reasonable. They include talking, dropping something, ending a power, and activating or maintaining a power.

### Domain terms

- ++Free Action++ — a minor action that does not spend the standard or move action

## Behaviors

#### Scenario: Talking does not spend the standard or move action

*Given* it is the ++Character++'s turn
  *And* the standard action and the move action are still available
*When* the **Player** takes a free action to talk
*Then* the character speaks
  *And* the standard action and the move action stay available
  *And* the outcome continues in Take Reaction

#### Scenario Outline: Listed minor acts are free actions

*Given* it is the ++Character++'s turn
*When* the **Player** takes a free action to {action}
*Then* the {action} happens
  *And* the standard action is not spent

#### Examples

| scenario | action |
| --- | --- |
| ++drop++ | drop an object |
| ++end a power++ | end the use of a power |
| ++activate a power++ | activate a power |
| ++maintain a power++ | maintain a power |

#### Scenario: The Gamemaster stops an unreasonable free action

*Given* the ++Character++ has already taken the free actions the Gamemaster considers reasonable
*When* the **Player** takes another free action
*Then* that further free action does not happen

#### Scenario: Several reasonable free actions can share the turn

*Given* it is the ++Character++'s turn
*When* the **Player** talks and then drops an object
*Then* both free actions happen
  *And* the standard action is still available
