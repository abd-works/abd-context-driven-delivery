---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Increase Effort Rank

**Evidence:** observed — HeroesHandbook.md lines 1449–1452 and 1480–1486. One power effect gains +1 rank until the hero's next turn. Speed and Strength each have the same +1 until the next turn. Permanent effects cannot be increased.

### Domain terms

- ++Effort Rank++ — a +1 rank from extra effort that lasts until the start of the hero's next turn

## Behaviors

#### Scenario: One power effect gains a rank until the next turn

*Given* a hero has a non-permanent power effect of rank *8*
  *And* the hero has not used extra effort this turn
*When* the **Player** uses extra effort to increase that effect
*Then* the effect rank is *9* until the start of the hero's next turn
  *And* the outcome continues in Perform Power Stunt

#### Scenario: A permanent effect does not increase

*Given* a hero has a permanent power effect of rank *8*
*When* the **Player** uses extra effort to increase that effect
*Then* the effect rank stays *8*

#### Scenario: Speed gains a rank until the next turn

*Given* a hero has speed rank *4*
*When* the **Player** uses extra effort to increase speed
*Then* the speed rank is *5* until the start of the hero's next turn

#### Scenario: Strength gains a rank until the next turn

*Given* a hero has Strength *4*
*When* the **Player** uses extra effort to increase Strength
*Then* the Strength rank is *5* until the start of the hero's next turn
