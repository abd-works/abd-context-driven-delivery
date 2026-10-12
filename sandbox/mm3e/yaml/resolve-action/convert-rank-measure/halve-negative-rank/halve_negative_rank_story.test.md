---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Halve Negative Rank

**Evidence:** observed — HeroesHandbook.md lines 348–352. Each rank below the table halves the previous measure. The handbook states rank -6 as half a pound, 1/16 second, and 3 inches. Time rank -5 on the table is 1/8 second. Distance rank -5 is 6 inches.

### Domain terms

- ++Negative Rank++ — a rank below the printed table, each step half of the previous measure

## Behaviors

#### Scenario: Rank negative six time is one sixteenth of a second

*Given* time rank *-5* measures *1/8 second*
*When* the **Simulator** halves that measure for rank *-6*
*Then* the time measure is *1/16 second*
  *And* the outcome continues in Add Measure Value

#### Scenario: Rank negative six distance is three inches

*Given* distance rank *-5* measures *6 inches*
*When* the **Simulator** halves that measure for rank *-6*
*Then* the distance measure is *3 inches*

#### Scenario: Rank negative six mass is half a pound

*Given* the handbook states the mass for rank *-6*
*When* the **Simulator** converts rank *-6* mass
*Then* the mass measure is *half a pound*

#### Scenario: The next lower rank halves again

*Given* time rank *-6* measures *1/16 second*
*When* the **Simulator** halves that measure for rank *-7*
*Then* the time measure is *1/32 second*
