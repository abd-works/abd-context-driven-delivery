---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Perform Heroic Feat

**Evidence:** observed — HeroesHandbook.md lines 1501–1516. One hero point grants one rank of an advantage the hero does not have, until the end of the next turn. Fortune advantages are excluded. Prerequisites are required. The hero must be capable of using the advantage. **Flagged** — the advantage list is in the Advantages chapter, which this slice does not include.

### Domain terms

- ++Heroic Feat++ — one rank of an advantage gained until the end of the next turn

## Behaviors

#### Scenario: The hero gains one rank of an advantage until the next turn ends

*Given* the hero does not have the advantage
  *And* the hero can use that advantage and meets its prerequisites
  *And* the advantage is not a fortune advantage
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** performs a heroic feat
*Then* the hero has one rank of that advantage until the end of the next turn
  *And* the **Player** has *0* hero points
  *And* the outcome continues in Improve Roll

#### Scenario: A fortune advantage is not gained

*Given* the advantage is a fortune advantage
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** performs a heroic feat for that advantage
*Then* the hero does not gain the advantage
  *And* the **Player** still has *1* hero point

#### Scenario: Missing prerequisites block the feat

*Given* the advantage has a prerequisite the hero does not have
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** performs a heroic feat for that advantage
*Then* the hero does not gain the advantage
  *But* the prerequisite is unmet

#### Scenario: An advantage the hero cannot use is not gained

*Given* the hero is not capable of using the advantage
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** performs a heroic feat for that advantage
*Then* the hero does not gain the advantage
