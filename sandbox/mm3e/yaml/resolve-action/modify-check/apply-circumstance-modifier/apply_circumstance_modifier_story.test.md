---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Apply Circumstance Modifier

**Evidence:** observed — HeroesHandbook.md lines 1156–1184. Minor is ±2. Major is ±5. The handbook applies the modifier to the check result.

### Domain terms

- ++Circumstance Modifier++ — +2 or -2 for a minor edge or hindrance, +5 or -5 for a major one, applied to the check result

## Behaviors

#### Scenario: A minor favorable circumstance adds two to the check

*Given* a ++Trait Check++ die of *11* and a modifier of *+2*
  *And* the ++Difficulty Class++ is *15*
  *And* the situation is a minor favorable circumstance
*When* the **Gamemaster** applies the circumstance modifier
*Then* the ++Check Result++ is *15*
  *And* the check succeeds
  *And* the outcome continues in Apply Tool Penalty

#### Scenario Outline: Circumstance modifiers use two or five

*Given* a ++Trait Check++ whose die and trait modifier already total *10*
  *And* the situation is {situation}
*When* the **Gamemaster** applies the circumstance modifier
*Then* the ++Check Result++ is {total}

#### Examples

| scenario | situation | total |
| --- | --- | --- |
| ++minor bonus++ | minor favorable | 12 |
| ++minor penalty++ | minor disadvantage | 8 |
| ++major bonus++ | major favorable | 15 |
| ++major penalty++ | major disadvantage | 5 |

#### Scenario: The modifier lands on the check result

*Given* a major favorable circumstance
  *And* the ++Difficulty Class++ stays *15*
*When* the **Gamemaster** applies a *+5* circumstance modifier to a check whose other terms total *10*
*Then* the ++Check Result++ is *15*
  *And* the ++Difficulty Class++ is still *15*

#### Scenario: A two-point bonus turns a short result into a success

*Given* a ++Trait Check++ whose die and trait modifier total *13*
  *And* the ++Difficulty Class++ is *15*
*When* the **Gamemaster** applies a minor favorable *+2*
*Then* the ++Check Result++ is *15*
  *And* the check succeeds
