---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Apply Routine Opposition

**Evidence:** observed — HeroesHandbook.md lines 1115–1118 and 1128–1133. Routine opposition is the opposing modifier + 10. Attack checks use 10 + defense for that reason. A guard who is looking rolls an active Perception check. **Flagged** — the Defend action is in Action & Adventure, which this slice does not include.

### Domain terms

- ++Routine Opposition++ — the opposing character's modifier plus *10*, with no opposing die

## Behaviors

#### Scenario: An unaware target opposes with modifier plus ten

*Given* a character sits in a park and is not looking for anyone
  *And* that character's Perception modifier is *+6*
*When* the **Simulator** applies routine opposition to a Stealth check
*Then* the ++Difficulty Class++ is *16*
  *But* the target does not roll Perception
  *And* the outcome continues in Compare Trait Rank

#### Scenario: An attack uses ten plus the defense as routine opposition

*Given* the target's Parry is *+5*
  *And* the target is taking other actions rather than going fully on the defensive
*When* the **Simulator** applies routine opposition to the attack check
*Then* the ++Defense Class++ is *15*

#### Scenario: A guard who is looking rolls an active check

*Given* a guard is standing watch and looking for intruders
*When* the **Gamemaster** opposes Stealth with the guard's Perception
*Then* the guard rolls a Perception check
  *But* the opposition is not modifier + 10

#### Scenario: Routine opposition succeeds when the active result is lower

*Given* ++Routine Opposition++ has set the ++Difficulty Class++ to *16*
  *And* the active Stealth total is *15*
*When* the **Simulator** compares the check
*Then* the Stealth check fails
