---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Roll Attack Check

**Evidence:** observed — HeroesHandbook.md lines 1195–1208. Attack check is d20 + attack bonus + modifiers vs defense class. Parry for close, Dodge for ranged. A natural 20 always hits. A natural 1 always misses. **Flagged** — what a critical hit does beyond the automatic hit is in Action & Adventure, which this slice does not include.

### Domain terms

- ++Attack Check++ — d20 plus attack bonus and modifiers against the target's ++Defense Class++
- ++Defense Class++ — Parry for a close attack, Dodge for a ranged attack

## Behaviors

#### Scenario: A close attack that equals Parry hits

*Given* a ++Character++ whose close attack bonus is *+4*
  *And* the target's Parry ++Defense Class++ is *15*
*When* the **Player** rolls an attack check and the die shows *11*
*Then* the ++Check Result++ is *15*
  *And* the attack hits
  *And* the outcome continues in Roll Resistance Check

#### Scenario: A ranged attack under Dodge misses

*Given* a ++Character++ whose ranged attack bonus is *+4*
  *And* the target's Dodge ++Defense Class++ is *15*
*When* the **Player** rolls an attack check and the die shows *8*
*Then* the ++Check Result++ is *12*
  *And* the attack misses

#### Scenario: A natural 20 hits even when the total is short

*Given* a ++Character++ whose attack bonus is *+0*
  *And* the target's Parry ++Defense Class++ is *25*
*When* the **Player** rolls an attack check and the die shows *20*
*Then* the attack hits
  *And* the hit may be a critical hit

#### Scenario: A natural 1 misses even when the total would hit

*Given* a ++Character++ whose attack bonus is *+20*
  *And* the target's Dodge ++Defense Class++ is *10*
*When* the **Player** rolls an attack check and the die shows *1*
*Then* the ++Check Result++ is *21*
  *And* the attack misses
