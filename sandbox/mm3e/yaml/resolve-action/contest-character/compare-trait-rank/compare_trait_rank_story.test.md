---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Compare Trait Rank

**Evidence:** observed — HeroesHandbook.md lines 1119–1126. A comparison uses ranks and no die. The higher rank wins. Identical ranks: 1–10 the first character, 11–20 the second. Extra effort and maneuvers are outside a straight comparison.

### Domain terms

- ++Comparison Check++ — the higher rank wins, with no die unless the ranks match

## Behaviors

#### Scenario: The higher rank wins with no die

*Given* one ++Character++ has Strength *6*
  *And* the other ++Character++ has Strength *3*
  *But* neither character is using extra effort or a maneuver
*When* the **Simulator** compares the Strength ranks
*Then* the Strength *6* character wins the arm wrestle
  *But* no die is rolled
  *And* the outcome continues in Apply Circumstance Modifier

#### Scenario: The faster rank wins a straight race

*Given* one ++Character++ has a speed rank of *8*
  *And* the other ++Character++ has a speed rank of *5*
*When* the **Simulator** compares the speed ranks
*Then* the speed rank *8* character wins
  *But* no die is rolled

#### Scenario Outline: Identical ranks split on a d20

*Given* both characters have Strength *4*
*When* the **Player** rolls the comparison die and it shows {die}
*Then* the {winner} character wins

#### Examples

| scenario | die | winner |
| --- | --- | --- |
| ++first character++ | 1 | first |
| ++first character on ten++ | 10 | first |
| ++second character on eleven++ | 11 | second |
| ++second character++ | 20 | second |

#### Scenario: A rank already increased by extra effort is the rank compared

*Given* a ++Character++ whose Strength was *4* and extra effort has raised it to *5*
  *And* the other ++Character++ has Strength *4*
*When* the **Simulator** compares the Strength ranks
*Then* the Strength *5* character wins
