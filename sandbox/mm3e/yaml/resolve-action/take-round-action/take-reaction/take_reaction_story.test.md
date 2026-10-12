---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Take Reaction

**Evidence:** observed — HeroesHandbook.md lines 1239–1252. A reaction answers something else, even off the character's turn. It does not use the standard or move allotment. The character reacts only when circumstances call for it.

### Domain terms

- ++Reaction++ — a response to something happening in the round, including off the character's turn

## Behaviors

#### Scenario: The character reacts off turn when circumstances call for it

*Given* it is another character's turn
  *And* something happens that calls for this ++Character++ to respond
*When* the **Player** takes a reaction
*Then* the reaction happens
  *And* the character's standard action and move action stay unspent
  *And* the outcome continues in Apply Basic Condition

#### Scenario: The character can react again when circumstances call again

*Given* the ++Character++ has already taken a reaction this round
  *And* a new circumstance calls for another response
*When* the **Player** takes a reaction
*Then* the second reaction happens

#### Scenario: No circumstance means no reaction

*Given* nothing in the round calls for the ++Character++ to respond
*When* the **Player** takes a reaction
*Then* the reaction does not happen

#### Scenario: A reaction takes no significant time

*Given* a circumstance calls for a reaction
*When* the **Player** takes a reaction
*Then* the reaction resolves in the moment that called for it
  *And* the reaction does not become the character's standard action
