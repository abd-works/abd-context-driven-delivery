---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Roll Trait Check

**Evidence:** observed — HeroesHandbook.md lines 257–281, 816–878, and 1038–1154. The check is d20 + modifiers vs a difficulty class. A natural 20 increases the degree of success by one. **Intended** — the Simulator shows that result because the user asked for an online simulator of these rules.

### Domain terms

- ++Trait Check++ — d20 plus the character's modifiers, compared with a ++Difficulty Class++
- ++Degree of Success++ — one degree for meeting the difficulty class, plus one for every five full points over it
- ++Degree of Failure++ — one degree for falling short, plus one for every five full points under it
- ++Critical Success++ — a natural 20 increases the degree of success by one

## Behaviors

#### Scenario: A trait check that meets the difficulty class succeeds

*Given* a ++Character++ whose ++Trait Check++ modifier is *+3*
  *And* the ++Difficulty Class++ is *15*
*When* the **Player** rolls a trait check and the die shows *12*
*Then* the ++Check Result++ is *15*
  *And* the check succeeds with one ++Degree of Success++
  *And* the outcome continues in Set Difficulty Class

#### Scenario Outline: Degrees follow five-point margins

*Given* a ++Character++ whose ++Trait Check++ modifier is {modifier}
  *And* the ++Difficulty Class++ is {difficulty class}
*When* the **Player** rolls a trait check and the die shows {die}
*Then* the ++Check Result++ is {total}
  *And* the check shows {outcome}

#### Examples

| scenario | modifier | difficulty class | die | total | outcome |
| --- | --- | --- | --- | --- | --- |
| ++three over the difficulty class++ | +3 | 10 | 10 | 13 | one degree of success |
| ++two under the difficulty class++ | +3 | 10 | 5 | 8 | one degree of failure |
| ++five over a DC 20 check++ | +10 | 20 | 15 | 25 | two degrees of success |
| ++ten over a DC 20 check++ | +10 | 20 | 20 | 30 | three degrees of success |
| ++fifteen over a DC 20 check++ | +15 | 20 | 20 | 35 | four degrees of success |
| ++five under a DC 20 check++ | +5 | 20 | 10 | 15 | one degree of failure |
| ++ten under a DC 20 check++ | +5 | 20 | 5 | 10 | two degrees of failure |
| ++fifteen under a DC 20 check++ | +0 | 20 | 5 | 5 | three degrees of failure |
| ++twenty under a DC 20 check++ | -1 | 20 | 1 | 0 | four degrees of failure |

#### Scenario: A natural 20 increases a success by one degree

*Given* a ++Character++ whose ++Trait Check++ modifier is *+0*
  *And* the ++Difficulty Class++ is *15*
*When* the **Player** rolls a trait check and the die shows *20*
*Then* the ++Check Result++ *20* is two degrees of success before the critical
  *And* the ++Critical Success++ raises it to three degrees of success

#### Scenario: A natural 20 turns a failed total into a success

*Given* a ++Character++ whose ++Trait Check++ modifier is *+0*
  *And* the ++Difficulty Class++ is *25*
*When* the **Player** rolls a trait check and the die shows *20*
*Then* the ++Check Result++ *20* is below the difficulty class
  *And* the ++Critical Success++ makes the check a success

#### Scenario: Training adds the skill rank to the ability

*Given* a ++Character++ with Agility *6* and Acrobatics *7*
  *And* the ++Difficulty Class++ is *15*
*When* the **Player** rolls an Acrobatics check and the die shows *4*
*Then* the ++Check Result++ is *17*
  *And* the check succeeds with one ++Degree of Success++
