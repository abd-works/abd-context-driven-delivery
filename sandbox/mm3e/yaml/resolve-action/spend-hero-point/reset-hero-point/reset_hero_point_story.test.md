---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Reset Hero Point

**Evidence:** observed — HeroesHandbook.md lines 1474. Unspent hero points do not carry to the next adventure. The next adventure starts at 1.

### Domain terms

- ++Hero Point Reset++ — the next adventure starts each hero at 1 hero point

## Behaviors

#### Scenario: Unspent points do not carry over

*Given* the **Player** has *3* unspent hero points at the end of the adventure
*When* the **Simulator** resets hero points for the next adventure
*Then* the **Player** has *1* ++Hero Point++
  *And* the outcome continues in Convert Rank To Measure

#### Scenario: A spent point still starts the next adventure at one

*Given* the **Player** has *0* hero points at the end of the adventure
*When* the **Simulator** resets hero points for the next adventure
*Then* the **Player** has *1* ++Hero Point++

#### Scenario: Points stay during the same adventure

*Given* the **Player** has *2* hero points
  *And* the adventure has not ended
*When* the **Simulator** checks the hero point count
*Then* the **Player** still has *2* hero points

#### Scenario: The new session of the next adventure grants that one point

*Given* a new adventure's session is beginning
  *And* the previous adventure ended with *4* hero points
*When* the **Simulator** grants the session hero point
*Then* the **Player** has *1* ++Hero Point++
  *But* the previous *4* are not added
