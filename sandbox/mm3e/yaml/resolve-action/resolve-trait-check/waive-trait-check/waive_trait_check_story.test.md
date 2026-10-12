---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Waive Trait Check

**Evidence:** observed — HeroesHandbook.md lines 831–868. The Gamemaster can treat an action as automatic. Leaping down, smashing the skylight, and flipping the switch need no check in the rooftop example. Swinging is automatic with the Swinging effect.

### Domain terms

- ++Waived Check++ — an action the Gamemaster resolves without a die roll

## Behaviors

#### Scenario: The Gamemaster waives a check that cannot fail

*Given* the hero is smashing through a Plexiglas skylight
*When* the **Gamemaster** waives the trait check
*Then* the smash happens
  *But* no ++Trait Check++ is rolled
  *And* the outcome continues in Roll Percentage Chance

#### Scenario: Leaping down needs no check

*Given* the hero leaps down from the rooftop
*When* the **Gamemaster** waives the trait check
*Then* the leap happens
  *But* no ++Trait Check++ is rolled

#### Scenario: The switch is automatic only after the villain is out of the way

*Given* the Fighting check has already hit the villain
*When* the **Player** flips the switch
*Then* the switch flips
  *But* no ++Trait Check++ is rolled for the switch

#### Scenario: A failed hit leaves the switch unflipped

*Given* the Fighting check against the villain has failed
  *But* the hero has not gotten past the villain
*When* the **Player** tries to flip the switch
*Then* the switch stays unflipped
  *And* the rest of the intended action does not happen

#### Scenario: Swinging is automatic when the hero has the Swinging effect

*Given* the ++Character++ has the Swinging movement effect
*When* the **Player** swings to the catwalk
*Then* the swing happens
  *But* no Acrobatics check is rolled
