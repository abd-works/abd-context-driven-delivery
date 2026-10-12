---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Shake Entranced Character

**Evidence:** observed — HeroesHandbook.md lines 1391–1394. Entranced is stunned except for paying attention. An ally's interaction skill against DC 10 + effect rank shakes the character free. An obvious threat breaks the trance.

### Domain terms

- ++Entranced++ — stunned, taking no actions other than paying attention to the effect

## Behaviors

#### Scenario: An interaction check at ten plus effect rank breaks the trance

*Given* a ++Character++ is entranced by an effect of rank *5*
  *And* an ally attempts an interaction skill check
*When* the **Player** shakes the entranced character and the result is *15*
*Then* the ++Difficulty Class++ is *15*
  *And* the character is no longer entranced
  *And* the outcome continues in Stand Prone Character

#### Scenario: A short interaction check leaves the trance

*Given* a ++Character++ is entranced by an effect of rank *5*
*When* the **Player** shakes the entranced character and the result is *14*
*Then* the character stays entranced
  *And* the character takes no action other than paying attention

#### Scenario: An obvious threat breaks the trance

*Given* a ++Character++ is entranced
*When* an obvious threat reaches the character
*Then* the trance breaks
  *But* no interaction check is required

#### Scenario: The entranced character does not act

*Given* a ++Character++ is entranced
  *But* no threat has broken the trance
*When* the **Player** takes a standard action with that character
*Then* the standard action does not happen
  *And* the character pays attention to the entrancing effect
