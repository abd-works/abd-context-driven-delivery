---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Counter Effect

**Evidence:** observed — HeroesHandbook.md lines 1525–1527. A hero point attempts to counter an effect as a reaction. **Flagged** — the countering procedure is in the Powers chapter, which this slice does not include. The intended behavior is that the spend offers the counter attempt.

### Domain terms

- ++Instant Counter++ — a reaction, bought with a hero point, that attempts to counter an effect

## Behaviors

#### Scenario: The hero spends a point to attempt a counter

*Given* an effect is used against the hero
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** counters the effect
*Then* the counter is attempted as a reaction
  *And* the **Player** has *0* hero points
  *And* the outcome continues in Recover Condition

#### Scenario: The counter does not spend a standard action

*Given* an effect is used against the hero off the hero's turn
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** counters the effect
*Then* the counter happens off the hero's turn
  *And* the hero's standard action stays unspent

#### Scenario: No hero point means no counter

*Given* an effect is used against the hero
  *And* the **Player** has *0* hero points
*When* the **Player** counters the effect
*Then* no counter is attempted

#### Scenario: The Powers chapter procedure is not in this slice

*Given* the counter attempt has been offered
  *But* Chapter 1 does not state the counter check
*When* the **Simulator** resolves the counter
*Then* the counter attempt is recorded
  *And* the check that decides the counter is not invented here
