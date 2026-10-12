---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Gain Effort Bonus

**Evidence:** observed — HeroesHandbook.md lines 1436–1439. One check gains +2, or an existing +2 becomes +5. A -2 penalty is negated. A -5 penalty becomes -2.

### Domain terms

- ++Effort Bonus++ — a circumstance bonus from extra effort on one check

## Behaviors

#### Scenario: Extra effort adds two to one check

*Given* a check's other terms total *13* and the ++Difficulty Class++ is *15*
  *And* the hero has not used extra effort this turn
*When* the **Player** uses extra effort to gain a bonus on that check
*Then* the ++Check Result++ is *15*
  *And* the check succeeds
  *And* the outcome continues in Increase Effort Rank

#### Scenario: An existing plus two becomes a major plus five

*Given* a check already has a *+2* circumstance bonus and its other terms total *10*
*When* the **Player** uses extra effort to improve that bonus
*Then* the circumstance bonus is *+5*
  *And* the ++Check Result++ is *15*

#### Scenario: A minor penalty is negated

*Given* a check has a *-2* circumstance penalty and its other terms total *15*
*When* the **Player** uses extra effort to negate that penalty
*Then* the ++Check Result++ is *15*
  *But* the -2 penalty is not applied

#### Scenario: A major penalty shrinks to a minor penalty

*Given* a check has a *-5* circumstance penalty and its other terms total *15*
*When* the **Player** uses extra effort to reduce that penalty
*Then* the penalty is *-2*
  *And* the ++Check Result++ is *13*
