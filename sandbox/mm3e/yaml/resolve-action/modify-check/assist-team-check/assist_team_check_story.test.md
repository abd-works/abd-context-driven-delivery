---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Assist Team Check

**Evidence:** observed — HeroesHandbook.md lines 1186–1194. Each helper rolls the same trait against DC 10. Their degrees add. One success degree is +2 for the leader. Three or more are +5. One failure degree changes nothing. Two or more failure degrees are -2. The Gamemaster limits how many characters can help.

### Domain terms

- ++Helper Check++ — the same trait as the leader, against ++Difficulty Class++ *10*

## Behaviors

#### Scenario: A helper's one degree of success gives the leader plus two

*Given* the helper uses the leader's trait
  *And* the helper's modifier is *+0*
*When* the **Player** assists and the die shows *10*
*Then* the helper has one ++Degree of Success++ against ++Difficulty Class++ *10*
  *And* the leader gains a *+2* circumstance bonus
  *And* the outcome continues in Open Action Round

#### Scenario Outline: Helper degrees set the leader's modifier

*Given* the helpers' degrees against ++Difficulty Class++ *10* total {degrees}
*When* the **Simulator** adds the helper degrees
*Then* the leader's circumstance modifier is {modifier}

#### Examples

| scenario | degrees | modifier |
| --- | --- | --- |
| ++one success++ | 1 success | +2 |
| ++two successes++ | 2 success | +2 |
| ++three successes++ | 3 success | +5 |
| ++one failure++ | 1 failure | +0 |
| ++two failures++ | 2 failure | -2 |

#### Scenario: Two helpers add their degrees together

*Given* one helper has two degrees of success against ++Difficulty Class++ *10*
  *And* the other helper has one degree of success against ++Difficulty Class++ *10*
*When* the **Simulator** adds the helper degrees
*Then* the helpers have three degrees of success
  *And* the leader gains a *+5* circumstance bonus

#### Scenario: The Gamemaster limits how many characters help

*Given* more characters are present than the Gamemaster allows to help
*When* the **Gamemaster** sets the helper limit at *2*
*Then* only two characters roll helper checks
  *But* the extra characters do not add degrees
