---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Add Measure Value

**Evidence:** observed — HeroesHandbook.md lines 354 and 782–808. Add the measures, then convert back. Rank 4 distance plus rank 6 distance is about 2,300 feet, rank 7, not rank 10. Distance rank = time rank + speed rank. Time rank = distance rank - speed rank. Throwing distance rank = Strength rank - mass rank.

### Domain terms

- ++Added Measure++ — measures added together, then turned back into a rank

## Behaviors

#### Scenario: Two distances add as feet and come back as rank seven

*Given* one distance is rank *4*, *500 feet*
  *And* the other distance is rank *6*, *1,800 feet*
*When* the **Simulator** adds the measures
*Then* the sum is *2,300 feet*
  *And* the distance rank is *7*
  *But* the rank is not *10*

#### Scenario Outline: Time plus speed is the distance rank

*Given* a {mover} has speed rank {speed}
  *And* the time rank is {time}
*When* the **Simulator** adds the time rank and the speed rank
*Then* the distance rank is {distance}
  *And* the distance measure is {measure}

#### Examples

| scenario | mover | speed | time | distance | measure |
| --- | --- | --- | --- | --- | --- |
| ++walking an hour++ | normal person | 0 | 9 | 9 | 2 miles |
| ++flight an hour++ | Flight 12 | 12 | 9 | 21 | 8,000 miles |
| ++flight one round++ | Flight 12 | 12 | 0 | 12 | 16 miles |

#### Scenario: Distance minus speed is the time rank

*Given* a hero has speed rank *14*
  *And* the distance is *30 miles*, rank *13*
*When* the **Simulator** subtracts the speed rank from the distance rank
*Then* the time rank is *-1*
  *And* the time measure is *3 seconds*

#### Scenario: Strength minus mass is the throwing distance

*Given* a hero has Strength *10*
  *And* the hero picks up a *10-ton* truck, mass rank *9*
*When* the **Simulator** subtracts the mass rank from the Strength rank
*Then* the throwing distance rank is *1*
  *And* the throwing distance is *60 feet*
