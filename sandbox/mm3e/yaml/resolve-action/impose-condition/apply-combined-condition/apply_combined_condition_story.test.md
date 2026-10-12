---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Apply Combined Condition

**Evidence:** observed — HeroesHandbook.md lines 1344–1425. A combined condition is a set of basic conditions. Asleep, bound, dying, and the other combined conditions below are the sets Chapter 1 names.

### Domain terms

- ++Combined Condition++ — basic conditions that share one descriptor, such as staggered or asleep

## Behaviors

#### Scenario: Staggered applies dazed and hindered

*Given* a ++Character++ in a normal state
*When* the **Simulator** applies staggered
*Then* the character is dazed
  *And* the character is hindered
  *And* the outcome continues in Remove Condition Part

#### Scenario Outline: Each combined condition applies its parts

*Given* a ++Character++ in a normal state
*When* the **Simulator** applies {condition}
*Then* the character has {parts}

#### Examples

| scenario | condition | parts |
| --- | --- | --- |
| ++asleep++ | asleep | defenseless, stunned, and unaware |
| ++blind++ | blind | hindered, visually unaware, and vulnerable |
| ++bound++ | bound | defenseless, immobile, and impaired |
| ++exhausted++ | exhausted | impaired and hindered |
| ++incapacitated++ | incapacitated | defenseless, stunned, and unaware |
| ++paralyzed++ | paralyzed | defenseless, immobile, and physically stunned |
| ++deaf++ | deaf | the character cannot hear, and sound has total auditory concealment |
| ++dying++ | dying | incapacitated and near death |
| ++surprised++ | surprised | stunned and vulnerable |
| ++staggered++ | staggered | dazed and hindered |

#### Scenario: Anchored restraints make the character immobile

*Given* a ++Character++ is restrained
  *And* the restraints are anchored to an immobile object
*When* the **Simulator** applies the anchored restraint
*Then* the character is immobile and vulnerable
  *But* the character is not hindered

#### Scenario: A character restraining another can move them

*Given* a ++Character++ is restrained by another character
*When* the **Simulator** applies that restraint
*Then* the restrained character is immobile and vulnerable
  *And* the restraining character can move the restrained character

#### Scenario: An incapacitated character generally falls prone

*Given* a ++Character++ becomes incapacitated
  *But* no outside force keeps the character standing
*When* the **Simulator** applies incapacitated
*Then* the character is defenseless, stunned, and unaware
  *And* the character is prone
