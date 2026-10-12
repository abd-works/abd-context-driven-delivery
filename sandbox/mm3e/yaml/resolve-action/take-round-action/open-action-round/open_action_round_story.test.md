---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Open Action Round

**Evidence:** observed — HeroesHandbook.md lines 809–814 and 1220–1226. When the action starts, time breaks into six-second rounds. Each character has a turn. A quiet scene stays in description.

### Domain terms

- ++Action Round++ — a six-second span in which each character takes a turn

## Behaviors

#### Scenario: The action opens a six-second round

*Given* the heroes are fighting or staving off a disaster
*When* the **Simulator** opens an action round
*Then* the round is six seconds
  *And* each character has a turn in that round
  *And* the outcome continues in Take Standard Action

#### Scenario: The turn offers one standard action and one move action

*Given* an ++Action Round++ is open
  *And* it is the ++Character++'s turn
*When* the **Simulator** opens that turn
*Then* the character can take one standard action and one move action
  *And* the character can take free actions the Gamemaster allows

#### Scenario: A quiet scene does not open a round

*Given* the heroes are talking with the supporting cast
  *But* no disaster or fight has started
*When* the **Gamemaster** asks what the heroes are doing
*Then* the scene stays in description
  *But* no ++Action Round++ is open

#### Scenario: The round goes once around the characters

*Given* three characters are in the scene
*When* the **Simulator** opens an action round
*Then* each of the three characters gets a turn before the round ends
