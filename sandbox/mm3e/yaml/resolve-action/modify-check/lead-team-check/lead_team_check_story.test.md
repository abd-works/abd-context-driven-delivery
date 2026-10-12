---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Lead Team Check

**Evidence:** observed — HeroesHandbook.md lines 1186–1194. The leader, usually the highest bonus, rolls the check normally. Help cannot push the leader beyond +5 or below -2.

### Domain terms

- ++Team Check++ — one leader's check plus the helpers' degrees against difficulty class 10

## Behaviors

#### Scenario: The leader rolls the team check

*Given* the leader has the highest bonus on the trait, *+6*
  *And* help has already produced one degree of success, a *+2* circumstance bonus
  *And* the ++Difficulty Class++ of the team task is *15*
*When* the **Player** leads the team check and the die shows *8*
*Then* the ++Check Result++ is *16*
  *And* the team check succeeds
  *And* the outcome continues in Assist Team Check

#### Scenario: Help cannot raise the leader above plus five

*Given* helpers have produced five degrees of success
*When* the **Simulator** caps the leader's help modifier
*Then* the leader's circumstance bonus from the team is *+5*
  *But* the bonus is not higher than *+5*

#### Scenario: Help cannot push the leader below minus two

*Given* helpers have produced four degrees of failure
*When* the **Simulator** caps the leader's help penalty
*Then* the leader's circumstance penalty from the team is *-2*
  *But* the penalty is not worse than *-2*

#### Scenario: The leader is the character with the highest bonus

*Given* one ++Character++ has a bonus of *+6* and another has *+3*
*When* the **Player** leads the team check
*Then* the character with *+6* is the leader
  *And* the character with *+3* helps in Assist Team Check
