---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Stand Prone Character

**Evidence:** observed — HeroesHandbook.md lines 1414–1418. Prone is a -5 circumstance penalty on the character's close attacks. Opponents have +5 on close attacks and -5 on ranged attacks. The character is hindered. Standing is a move action.

### Domain terms

- ++Prone++ — lying on the ground

## Behaviors

#### Scenario: Standing from prone spends a move action

*Given* a ++Character++ is prone
  *And* the move action is available this turn
*When* the **Player** stands the prone character
*Then* the character is standing
  *And* the move action is spent
  *But* the character is not prone
  *And* the outcome continues in Gain Extra Action

#### Scenario: A prone character takes minus five on close attacks

*Given* a ++Character++ is prone
  *And* the close attack's other terms total *15*
*When* the **Player** makes a close attack
*Then* the ++Check Result++ is *10*

#### Scenario: Opponents gain five on close attacks and lose five on ranged attacks

*Given* a ++Character++ is prone
  *And* an opponent's attack bonus and die total *10*
*When* the opponent attacks the prone character with a {attack}
*Then* the opponent's ++Check Result++ is {total}

#### Examples

| scenario | attack | total |
| --- | --- | --- |
| ++close attack++ | close attack | 15 |
| ++ranged attack++ | ranged attack | 5 |

#### Scenario: A prone character is hindered

*Given* a ++Character++ is prone
  *And* the character's speed rank is *2*
*When* the **Simulator** applies prone
*Then* the character is hindered
  *And* the speed rank is *1*
