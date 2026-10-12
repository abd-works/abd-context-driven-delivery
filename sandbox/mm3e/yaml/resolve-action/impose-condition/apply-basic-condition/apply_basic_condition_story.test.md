---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Apply Basic Condition

**Evidence:** observed — HeroesHandbook.md lines 1254–1342. Basic conditions are single modifiers. When several apply, use all of their effects. The handbook names which conditions supersede lesser ones. Disabled supersedes impaired, and debilitated supersedes disabled, only when they apply to the same traits (lines 1321 and 1285). A defenseless character has active defense bonuses of 0; an attack against that character can be a routine check, and a normal hit is a critical hit (lines 1286–1289). The defense class is 10 plus the defense bonus (lines 1117–1118), so a bonus of 0 is defense class 10. **Flagged** — Debilitated Abilities are detailed in the Abilities chapter, Weaken is detailed in Powers, and what a critical hit does beyond the hit is in Action & Adventure. This story uses only what Chapter 1 states.

### Domain terms

- ++Basic Condition++ — one game modifier, such as vulnerable, dazed, or hindered
- ++Normal++ — the character is unaffected by other conditions

## Behaviors

#### Scenario: Vulnerable halves active defenses

*Given* a ++Character++ whose active defense is *5*
*When* the **Simulator** applies vulnerable
*Then* the active defense is *3*
  *And* the character is vulnerable
  *And* the outcome continues in Apply Combined Condition

#### Scenario Outline: Each basic condition imposes its handbook effect

*Given* a ++Character++ in a normal state
*When* the **Simulator** applies {condition}
*Then* the character is {condition}
  *And* {effect}

#### Examples

| scenario | condition | effect |
| --- | --- | --- |
| ++compelled++ | compelled | the controlling character chooses the free actions and the one standard action |
| ++dazed++ | dazed | the character is limited to free actions and one standard action |
| ++defenseless++ | defenseless | active defense bonuses are 0 |
| ++disabled++ | disabled | checks take a -5 circumstance penalty |
| ++fatigued++ | fatigued | the character is hindered |
| ++hindered++ | hindered | speed is half, one speed rank lower |
| ++immobile++ | immobile | the character cannot leave the spot |
| ++impaired++ | impaired | checks take a -2 circumstance penalty |
| ++stunned++ | stunned | the character takes no actions, including free actions |
| ++controlled++ | controlled | the controlling character dictates the character's actions |
| ++debilitated++ | debilitated | an ability is below -5 |
| ++unaware++ | unaware | the character makes no Perception checks |
| ++weakened++ | weakened | the character has lost power points in a trait |
| ++transformed++ | transformed | traits are altered and the power point total does not increase |

#### Scenario Outline: A greater condition supersedes the lesser one

*Given* a ++Character++ who is {lesser}
*When* the **Simulator** applies {greater}
*Then* the character is {greater}
  *But* the character is not {lesser}

#### Examples

| scenario | lesser | greater |
| --- | --- | --- |
| ++controlled replaces compelled++ | compelled | controlled |
| ++stunned replaces dazed++ | dazed | stunned |
| ++immobile replaces hindered++ | hindered | immobile |
| ++defenseless replaces vulnerable++ | vulnerable | defenseless |
| ++debilitated replaces weakened++ | weakened | debilitated |

#### Scenario: Conditions that do not supersede each other all apply

*Given* a ++Character++ who is impaired
*When* the **Simulator** applies hindered
*Then* the character is impaired and hindered
  *And* checks take a -2 circumstance penalty
  *And* speed is half

#### Scenario: Normal leaves the character unaffected

*Given* a ++Character++ who is vulnerable
*When* the **Simulator** applies normal
*Then* the character is unaffected by vulnerable
  *And* the active defense is no longer halved

#### Scenario: Disabled supersedes impaired on the same trait

*Given* a ++Character++ who is impaired on Fighting
*When* the **Simulator** applies disabled to Fighting
*Then* the character is disabled
  *But* the character is not impaired

#### Scenario: Debilitated supersedes disabled on the same trait

*Given* a ++Character++ who is disabled on Fighting
  *And* that Fighting rank is *-6*
*When* the **Simulator** applies debilitated to Fighting
*Then* the character is debilitated
  *But* the character is not disabled

#### Scenario: A routine attack hits a defenseless character

*Given* a ++Character++ who is defenseless, so the Parry bonus is *0*
  *And* an attacker whose attack bonus is *+5*
*When* the **Player** takes a routine check to attack that character
*Then* the ++Check Result++ is *15*
  *And* the ++Defense Class++ is *10*
  *And* the attack hits

#### Scenario: A normal hit on a defenseless character is a critical hit

*Given* a ++Character++ who is defenseless, so the Parry bonus is *0*
  *And* an attacker whose attack bonus is *+4*
  *But* the attacker has not taken a routine check
*When* the **Player** rolls an attack check and the die shows *11*
*Then* the ++Check Result++ is *15*
  *And* the ++Defense Class++ is *10*
  *And* the hit is a critical hit
