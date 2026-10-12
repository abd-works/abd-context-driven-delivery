---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Choose Next Higher Rank

**Evidence:** observed — HeroesHandbook.md lines 346 and 807. A measure that is not a table row uses the next higher listed rank. Twelve hours is time rank 13. Six miles is distance rank 11. A 10-ton truck is mass rank 9.

### Domain terms

- ++Next Higher Rank++ — the first listed rank whose measure is at least the value in question

## Behaviors

#### Scenario: Twelve hours is time rank thirteen

*Given* a time measure of *12 hours*
  *And* the table lists *8 hours* at rank *12* and *16 hours* at rank *13*
*When* the **Simulator** chooses the next higher rank
*Then* the time rank is *13*
  *And* the outcome continues in Halve Negative Rank

#### Scenario: Six miles is distance rank eleven

*Given* a distance measure of *6 miles*
  *And* the table lists *4 miles* at rank *10* and *8 miles* at rank *11*
*When* the **Simulator** chooses the next higher rank
*Then* the distance rank is *11*

#### Scenario: A ten-ton truck is mass rank nine

*Given* a mass of *10 tons*
  *And* the table lists *6 tons* at rank *8* and *12 tons* at rank *9*
*When* the **Simulator** chooses the next higher rank
*Then* the mass rank is *9*

#### Scenario: A measure that is on the table uses that rank

*Given* a mass of *400 pounds*
  *And* the table lists *400 pounds* at rank *3*
*When* the **Simulator** chooses the rank
*Then* the mass rank is *3*
  *But* the rank is not the next row up
