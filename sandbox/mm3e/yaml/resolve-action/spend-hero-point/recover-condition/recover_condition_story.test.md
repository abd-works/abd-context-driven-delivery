---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Recover Condition

**Evidence:** observed — HeroesHandbook.md lines 1529–1532. A hero point immediately removes dazed, fatigued, or stunned, with no action. Exhausted becomes fatigued. The same spend removes extra-effort fatigue.

### Domain terms

- ++Recovery++ — a hero point that removes dazed, fatigued, or stunned, or turns exhausted into fatigued

## Behaviors

#### Scenario: A hero point removes dazed

*Given* the hero is dazed
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** recovers
*Then* the hero is not dazed
  *But* no action is spent
  *And* the **Player** has *0* hero points
  *And* the outcome continues in Award Hero Point

#### Scenario Outline: A hero point removes one listed condition

*Given* the hero is {condition}
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** recovers
*Then* the hero is not {condition}

#### Examples

| scenario | condition |
| --- | --- |
| ++dazed++ | dazed |
| ++fatigued++ | fatigued |
| ++stunned++ | stunned |

#### Scenario: Exhausted becomes fatigued

*Given* the hero is exhausted
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** recovers
*Then* the hero is fatigued
  *But* the hero is not exhausted

#### Scenario: The same spend removes extra-effort fatigue

*Given* extra effort on the previous turn is about to fatigue the hero
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** recovers at the start of this turn
*Then* the hero is not fatigued
