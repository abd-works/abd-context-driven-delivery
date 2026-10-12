---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Take Routine Check

**Evidence:** observed — HeroesHandbook.md lines 972–979. Under no pressure the die counts as 10. A shortfall can still be rolled. The Gamemaster decides when the task is routine.

### Domain terms

- ++Routine Check++ — a check that uses *10* in place of the die

## Behaviors

#### Scenario: An average task with no pressure uses ten for the die

*Given* a ++Character++ with a ++Trait Check++ modifier of *+0*
  *And* the ++Difficulty Class++ is *10*
  *And* the circumstances are not under pressure
*When* the **Player** takes a routine check
*Then* the ++Check Result++ is *10*
  *And* the check succeeds with one ++Degree of Success++
  *And* the outcome continues in Roll Nonroutine Check

#### Scenario: A capable character succeeds at harder routine tasks

*Given* a ++Character++ with a ++Trait Check++ modifier of *+10*
  *And* the circumstances are not under pressure
*When* the **Player** takes a routine check against ++Difficulty Class++ *20*
*Then* the ++Check Result++ is *20*
  *And* the same routine total is three degrees of success against ++Difficulty Class++ *10*

#### Scenario: The Gamemaster decides the circumstances are routine

*Given* a task the ++Character++ would perform at a steady level
  *But* the character is not under the pressure of the action
*When* the **Gamemaster** calls the task a routine check
*Then* the ++Routine Check++ uses *10* instead of a rolled die

#### Scenario: A routine total that falls short stays short until the player rolls

*Given* a ++Character++ with a ++Trait Check++ modifier of *+0*
  *And* the ++Difficulty Class++ is *15*
*When* the **Player** takes a routine check
*Then* the ++Check Result++ is *10*
  *And* the routine check fails
  *And* the player can still roll the die in Roll Nonroutine Check
