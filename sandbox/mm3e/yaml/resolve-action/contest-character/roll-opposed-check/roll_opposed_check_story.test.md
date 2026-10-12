---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Roll Opposed Check

**Evidence:** observed — HeroesHandbook.md lines 1102–1114. The higher result wins. A tie goes to the higher bonus. Equal bonuses split on a d20: 1–10 one character, 11–20 the other, after high and low are chosen.

### Domain terms

- ++Opposed Check++ — each character rolls, and the other character's result is the difficulty class

## Behaviors

#### Scenario: The higher opposed result wins

*Given* the ++Character++ rolls Deception for a total of *18*
  *And* the opposing character rolls Insight for a total of *14*
*When* the **Player** rolls the opposed check
*Then* the ++Character++ wins the opposed check
  *And* the outcome continues in Pick Opposing Trait

#### Scenario: The opposing result wins when it is higher

*Given* the ++Character++ rolls Deception for a total of *12*
  *And* the opposing character rolls Insight for a total of *16*
*When* the **Player** rolls the opposed check
*Then* the opposing character wins the opposed check

#### Scenario: The higher bonus wins a tie

*Given* both opposed totals are *15*
  *And* the ++Character++ bonus is *+7* and the opposing bonus is *+4*
*When* the **Simulator** breaks the tie
*Then* the ++Character++ wins
  *But* no tie-break die is rolled

#### Scenario Outline: Equal bonuses split the tie on a d20

*Given* both opposed totals are *15* and both bonuses are *+5*
  *And* the first character is low and the second character is high
*When* the **Player** rolls the tie die and it shows {die}
*Then* {winner} wins

#### Examples

| scenario | die | winner |
| --- | --- | --- |
| ++low die++ | 1 | the low character |
| ++ten++ | 10 | the low character |
| ++eleven++ | 11 | the high character |
| ++high die++ | 20 | the high character |
