---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Remove Condition Part

**Evidence:** observed — HeroesHandbook.md lines 1360–1361. Removing dazed from staggered leaves hindered. Stunning a staggered character replaces dazed and leaves hindered. Immobilizing a staggered character replaces hindered and leaves dazed.

### Domain terms

- ++Condition Part++ — one basic condition inside a combined condition

## Behaviors

#### Scenario: Removing dazed from staggered leaves hindered

*Given* a ++Character++ who is staggered, so dazed and hindered
*When* the **Simulator** removes the dazed part
*Then* the character is hindered
  *But* the character is not dazed
  *And* the outcome continues in Wake Sleeping Character

#### Scenario: Stunning a staggered character replaces dazed

*Given* a ++Character++ who is staggered
*When* the **Simulator** applies stunned
*Then* the character is stunned and hindered
  *But* the character is not dazed

#### Scenario: Immobilizing a staggered character replaces hindered

*Given* a ++Character++ who is staggered
*When* the **Simulator** applies immobile
*Then* the character is dazed and immobile
  *But* the character is not hindered

#### Scenario: The other part of the combined condition stays

*Given* a ++Character++ who is exhausted, so impaired and hindered
*When* the **Simulator** removes the impaired part
*Then* the character is hindered
  *But* the character is not impaired
