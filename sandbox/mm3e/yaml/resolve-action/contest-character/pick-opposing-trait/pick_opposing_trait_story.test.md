---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Pick Opposing Trait

**Evidence:** observed — HeroesHandbook.md lines 991–1037 and 1112–1113. When no rule names the contest, the Gamemaster picks the skill, power, or ability. Named pairs such as Stealth vs Perception stay the pair the table gives.

### Domain terms

- ++Opposing Trait++ — the skill, power, or ability the other character checks

## Behaviors

#### Scenario: The Gamemaster names the trait when no rule does

*Given* two characters contest a task
  *But* no rule names the opposing trait
*When* the **Gamemaster** picks Expertise for both characters
*Then* both characters roll Expertise
  *And* the higher ++Check Result++ wins
  *And* the outcome continues in Apply Routine Opposition

#### Scenario: A named contest keeps the handbook pair

*Given* the task is sneaking up on someone
*When* the **Gamemaster** sets the opposed check
*Then* the active trait is Stealth
  *And* the opposing trait is Perception

#### Scenario Outline: Handbook opposed pairs stay fixed

*Given* the contest is {task}
*When* the **Gamemaster** sets the opposed check
*Then* the active trait is {active}
  *And* the opposing trait is {opposed}

#### Examples

| scenario | task | active | opposed |
| --- | --- | --- | --- |
| ++sneak++ | sneak up on someone | Stealth | Perception |
| ++con++ | con someone | Deception | Insight |
| ++race++ | win a car race | Vehicles | Vehicles |
| ++disguise++ | pretend to be someone else | Deception | Insight |
| ++filch++ | steal a key chain unnoticed | Sleight of Hand | Perception |
| ++trivia++ | win a trivia contest | Expertise | Expertise |
| ++security++ | break computer security | Technology | Technology |

#### Scenario: The highest result wins the contest the Gamemaster picked

*Given* the **Gamemaster** has both characters check the picked trait
  *And* one ++Check Result++ is *17* and the other is *11*
*When* the **Simulator** compares the results
*Then* the result *17* wins
