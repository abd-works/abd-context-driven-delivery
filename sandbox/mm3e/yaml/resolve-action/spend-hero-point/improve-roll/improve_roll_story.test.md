---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Improve Roll

**Evidence:** observed — HeroesHandbook.md lines 1517–1519. One hero point rerolls any die the player rolled and keeps the better result. A second roll of 1 through 10 has 10 added, so the reroll is 11 through 20. The point is spent before the Gamemaster announces the outcome. Rolls by the Gamemaster or other players are not improved without Luck Control. **Flagged** — Luck Control is in the Powers chapter.

### Domain terms

- ++Improved Roll++ — a reroll that keeps the better of the two dice

## Behaviors

#### Scenario: A low reroll has ten added and the better die stands

*Given* the **Player** has rolled a *12* and the Gamemaster has not announced the outcome
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** improves the roll and the second die shows *7*
*Then* the second die counts as *17*
  *And* the check uses *17*
  *And* the **Player** has *0* hero points
  *And* the outcome continues in Request Inspiration

#### Scenario: A high reroll stays as rolled

*Given* the **Player** has rolled an *18* and the Gamemaster has not announced the outcome
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** improves the roll and the second die shows *14*
*Then* the second die stays *14*
  *And* the check uses *18*

#### Scenario: The reroll replaces a worse first die

*Given* the **Player** has rolled a *4* and the Gamemaster has not announced the outcome
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** improves the roll and the second die shows *11*
*Then* the second die stays *11*
  *And* the check uses *11*

#### Scenario: The point cannot be spent after the outcome is announced

*Given* the Gamemaster has announced the outcome of the roll
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** improves that roll
*Then* the die is not rerolled
  *And* the **Player** still has *1* hero point

#### Scenario: Another person's die is not improved

*Given* the die was rolled by the Gamemaster
  *But* the hero does not have Luck Control
  *And* the **Player** has *1* ++Hero Point++
*When* the **Player** improves that roll
*Then* the die is not rerolled
  *And* the **Player** still has *1* hero point
