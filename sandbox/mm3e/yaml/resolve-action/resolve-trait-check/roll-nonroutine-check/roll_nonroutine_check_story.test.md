---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Roll Nonroutine Check

**Evidence:** observed — HeroesHandbook.md lines 979. When the routine result is not up to the task, the player may roll the die. The task is not routine for that character.

### Domain terms

- ++Nonroutine Check++ — the die roll the player chooses after a ++Routine Check++ falls short

## Behaviors

#### Scenario: The player rolls after the routine result falls short

*Given* a ++Routine Check++ of *10* against ++Difficulty Class++ *15*
  *And* the ++Character++ modifier is *+0*
*When* the **Player** rolls the die and it shows *16*
*Then* the ++Check Result++ is *16*
  *And* the check succeeds with one ++Degree of Success++
  *And* the outcome continues in Waive Trait Check

#### Scenario: The rolled die can still fail

*Given* a ++Routine Check++ of *10* against ++Difficulty Class++ *15*
  *And* the ++Character++ modifier is *+0*
*When* the **Player** rolls the die and it shows *4*
*Then* the ++Check Result++ is *4*
  *And* the check fails

#### Scenario: A natural 20 on the shortfall roll is a critical success

*Given* a ++Routine Check++ of *10* against ++Difficulty Class++ *25*
  *And* the ++Character++ modifier is *+0*
*When* the **Player** rolls the die and it shows *20*
*Then* the ++Check Result++ *20* is below the difficulty class
  *And* the ++Critical Success++ makes the check a success

#### Scenario: Pressure means the die is rolled from the start

*Given* the task is under the pressure of the action
  *But* the **Gamemaster** has not called the task routine
*When* the **Player** rolls a trait check
*Then* the ++Check Result++ uses the rolled die
  *But* the die is not replaced with *10*
