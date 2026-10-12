---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Set Difficulty Class

**Evidence:** observed — HeroesHandbook.md lines 876–880 and 885–970. The Gamemaster sets the difficulty class. The check equals or exceeds it to succeed.

### Domain terms

- ++Difficulty Class++ — the number the check must equal or exceed
- ++Difficulty++ — the named band from very easy (0) through nigh-impossible (40)

## Behaviors

#### Scenario: The Gamemaster sets the number the check must reach

*Given* a ++Trait Check++ whose die and modifier are not yet the question
*When* the **Gamemaster** sets the ++Difficulty Class++ to *15*
*Then* the check succeeds when the ++Check Result++ equals or exceeds *15*
  *And* the check fails when the ++Check Result++ is lower than *15*
  *And* the outcome continues in Take Routine Check

#### Scenario Outline: Named difficulties use the handbook bands

*Given* a task whose handbook difficulty is {difficulty}
*When* the **Gamemaster** sets the ++Difficulty Class++ for that task
*Then* the ++Difficulty Class++ is {difficulty class}
  *And* the example task is {example}

#### Examples

| scenario | difficulty | difficulty class | example |
| --- | --- | --- | --- |
| ++very easy notice++ | very easy | 0 | notice something in plain sight with Perception |
| ++easy climb++ | easy | 5 | climb a knotted rope with Athletics |
| ++average listen++ | average | 10 | hear an approaching security guard with Perception |
| ++tough disarm++ | tough | 15 | disarm an explosive with Technology |
| ++challenging swim++ | challenging | 20 | swim against a strong current with Athletics |
| ++formidable climb++ | formidable | 25 | climb a wet, slippery rock-face with Athletics |
| ++heroic security++ | heroic | 30 | overcome a sophisticated security system with Technology |
| ++super-heroic bluff++ | super-heroic | 35 | convince the guards to let you in without a badge, using Deception |
| ++nigh-impossible track++ | nigh-impossible | 40 | track a trained commando through the jungle with Perception |

#### Scenario: A result under the Gamemaster's difficulty class fails

*Given* the **Gamemaster** has set the ++Difficulty Class++ to *15*
  *And* the ++Character++ has a ++Check Result++ of *14*
*When* the **Simulator** compares the check with the difficulty class
*Then* the check fails
  *And* the failure is one ++Degree of Failure++

#### Scenario: The trait for the task is the one the handbook names

*Given* the task is socking a villain in the jaw
*When* the **Gamemaster** sets the check as Close Combat or Fighting
*Then* the ++Trait Check++ uses Close Combat or Fighting
  *And* a ranged attack on that villain would use Dexterity instead
