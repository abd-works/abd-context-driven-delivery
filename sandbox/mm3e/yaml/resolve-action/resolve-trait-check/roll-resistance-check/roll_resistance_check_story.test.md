---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Roll Resistance Check

**Evidence:** observed — HeroesHandbook.md lines 1209–1218. Resistance is d20 + defense vs generally 10 + rank. Defenses named here are Dodge, Fortitude, Toughness, and Will. **Flagged** — effect-by-effect resistance results live in the Powers chapter, which this slice does not include. This story asserts the degree, not a power's damage table.

### Domain terms

- ++Resistance Check++ — d20 plus a defense against a hazard difficulty class, generally *10* + the hazard's rank

## Behaviors

#### Scenario: A resistance check that equals the hazard difficulty class succeeds

*Given* a ++Character++ whose Toughness is *+2*
  *And* the hazard rank is *5*, so the ++Difficulty Class++ is *15*
*When* the **Player** rolls a resistance check and the die shows *13*
*Then* the ++Check Result++ is *15*
  *And* the resistance succeeds with one ++Degree of Success++
  *And* the outcome continues in Roll Opposed Check

#### Scenario: A resistance check under the hazard difficulty class fails

*Given* a ++Character++ whose Toughness is *+2*
  *And* the hazard rank is *5*, so the ++Difficulty Class++ is *15*
*When* the **Player** rolls a resistance check and the die shows *6*
*Then* the ++Check Result++ is *8*
  *And* the resistance fails with one ++Degree of Failure++

#### Scenario Outline: The defense used is the one the hazard calls for

*Given* a hazard that calls for {defense}
*When* the **Player** rolls a resistance check
*Then* the ++Resistance Check++ adds {defense}

#### Examples

| scenario | defense |
| --- | --- |
| ++dodge resistance++ | Dodge |
| ++fortitude resistance++ | Fortitude |
| ++toughness resistance++ | Toughness |
| ++will resistance++ | Will |

#### Scenario: A resistance check is graded in five-point degrees

*Given* a ++Character++ whose Fortitude is *+0*
  *And* the hazard rank is *0*, so the ++Difficulty Class++ is *10*
*When* the **Player** rolls a resistance check and the die shows *20*
*Then* the ++Check Result++ is *20*
  *And* the resistance succeeds with three degrees of success
