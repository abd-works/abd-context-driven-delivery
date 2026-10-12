---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Convert Rank To Measure

**Evidence:** observed — HeroesHandbook.md lines 376–389 and 399–703. Rank 3 Strength lifts 400 pounds. The Measurements Table pairs each rank with mass, time, and distance. Measures are approximate.

### Domain terms

- ++Rank++ — the number of a trait or a measure
- ++Measure++ — the table value for that rank, such as pounds, seconds, or feet

## Behaviors

#### Scenario: Strength three lifts four hundred pounds

*Given* a ++Character++ has Strength *3*
*When* the **Simulator** converts that rank to a measure
*Then* the lift measure is *400 pounds*
  *And* the outcome continues in Choose Next Higher Rank

#### Scenario Outline: Listed ranks use the table measure

*Given* a rank of {rank} on {column}
*When* the **Simulator** converts that rank to a measure
*Then* the measure is {measure}

#### Examples

| scenario | column | rank | measure |
| --- | --- | --- | --- |
| ++mass three++ | mass | 3 | 400 pounds |
| ++mass ten++ | mass | 10 | 25 tons |
| ++time zero++ | time | 0 | 6 seconds |
| ++time nine++ | time | 9 | 1 hour |
| ++time negative one++ | time | -1 | 3 seconds |
| ++distance one++ | distance | 1 | 60 feet |
| ++distance four++ | distance | 4 | 500 feet |
| ++distance six++ | distance | 6 | 1,800 feet |
| ++distance seven++ | distance | 7 | half a mile |
| ++distance nine++ | distance | 9 | 2 miles |
| ++distance twelve++ | distance | 12 | 16 miles |
| ++distance twenty-one++ | distance | 21 | 8,000 miles |

#### Scenario: The table measure is the ballpark value

*Given* a distance rank of *7*
*When* the **Simulator** converts that rank to a measure
*Then* the measure is about half a mile
  *And* the result is the table's ballpark, not a finer survey

#### Scenario: Strength ten lifts twenty-five tons

*Given* a ++Character++ has Strength *10*
*When* the **Simulator** converts that rank to a measure
*Then* the lift measure is *25 tons*
