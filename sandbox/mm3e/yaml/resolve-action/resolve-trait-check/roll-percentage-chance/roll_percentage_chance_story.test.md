---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Roll Percentage Chance

**Evidence:** observed — HeroesHandbook.md lines 202–213. Multiply the die by 5. A 45% chance succeeds on a roll of 9 or less.

### Domain terms

- ++Percentage Chance++ — the die times *5*, from *5%* on a 1 to *100%* on a 20

## Behaviors

#### Scenario: A forty-five percent chance succeeds on nine or less

*Given* a ++Percentage Chance++ of *45%*
*When* the **Player** rolls the die and it shows *9*
*Then* the percentage is *45%*
  *And* the chance succeeds
  *And* the outcome continues in Roll Attack Check

#### Scenario Outline: The die converts to a percentage in steps of five

*Given* a percentage roll with no other modifier
*When* the **Player** rolls the die and it shows {die}
*Then* the percentage is {percentage}

#### Examples

| scenario | die | percentage |
| --- | --- | --- |
| ++percentage five++ | 1 | 5% |
| ++percentage forty-five++ | 9 | 45% |
| ++percentage fifty++ | 10 | 50% |
| ++percentage one hundred++ | 20 | 100% |

#### Scenario: A roll above the chance fails

*Given* a ++Percentage Chance++ of *45%*
*When* the **Player** rolls the die and it shows *10*
*Then* the percentage is *50%*
  *And* the chance fails

#### Scenario: A roll under the chance succeeds

*Given* a ++Percentage Chance++ of *45%*
*When* the **Player** rolls the die and it shows *8*
*Then* the percentage is *40%*
  *And* the chance succeeds
