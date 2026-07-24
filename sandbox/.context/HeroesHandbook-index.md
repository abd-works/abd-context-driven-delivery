# HeroesHandbook index

Corpus: `sandbox/HeroesHandbook.md`  
Lenses: **clean_engineering** (modules + chunks) + **stories** (epics mapped onto those chunks).  
Existing ground: `sandbox/checks`.

Index file: `.context/HeroesHandbook-index.md`.  
Chunks: `{module}/.context/{leaf}-segment.md` — **verbatim source**; Stories pass is **additive** (no re-chunk).

Lens applied: `stories.md` § Contexts + `contexts/stories/partition.md` (additive multi-pass).


| Module path                   | Role            | Chunk                                                                                                           | Epic            | Suggested Mid-epic /                                                     | Evidence (source spans)                                                                                                  | Rough seam / API                                                | Thin deps                                          |
| ----------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- | -------------------------------------------------- |
| `checks`                      | flat            | `[checks/.context/checks-segment.md](../checks/.context/checks-segment.md)`                                     | `Resolve Check` | `Make Trait Check`, `Oppose Check`, `Assist Check`, `Make Routine Check` | Ch1 Checks→degrees; Ch4 How Skills Work; Ch6 Effect Checks                                                               | `Check` / `OpposedCheck` / `TeamCheck`; check-time `Trait` rank | `measurement`                                      |
| `character`                   | flat            | `[character/.context/character-segment.md](../character/.context/character-segment.md)`                         | `Create Hero`   | `Spend Power Points`, `Choose Complications`, `Pick Archetype` (TODO)    | Ch2 full; Ch1 Complications primer; Ch9 Awards                                                                           | points, PL, complications, advance                              | opaque ranks later                                 |
| `character` (abilities spans) | folded          | `[character/.context/abilities-segment.md](../character/.context/abilities-segment.md)`                         | `Create Hero`   | `Buy Ability Ranks`, `Derive Defenses`                                   | Ch1 Abilities primer; Ch3                                                                                                | ability ranks; defense/initiative inputs                        | measurement                                        |
| `skills`                      | flat            | `[skills/.context/skills-segment.md](../skills/.context/skills-segment.md)`                                     | `Create Hero`   | `Train Skills`, `Attempt Untrained Skill`                                | Ch1 Skills primer; Ch4                                                                                                   | skill ranks                                                     | ability **key** only                               |
| `advantages`                  | flat            | `[advantages/.context/advantages-segment.md](../advantages/.context/advantages-segment.md)`                     | `Create Hero`   | `Take Advantages`, `Unlock Maneuver`                                     | Ch1 Advantages primer; Ch5                                                                                               | grants / unlock tags                                            | none                                               |
| `powers/effect`               | **parent base** | `[powers/effect/.context/effect-segment.md](../powers/effect/.context/effect-segment.md)`                       | `Wield Power`   | `Compose Effect`, `Pay Power Cost`, `Apply Descriptors`                  | Ch1 Powers primer; Ch6 acquire/cost/descriptors; Effect Types overview; How Powers Work; Applying Modifiers; Descriptors | shared effect compose/activate/cost protocol                    | `checks` when resolving                            |
| `powers/attack`               | child           | `[powers/attack/.context/attack-segment.md](../powers/attack/.context/attack-segment.md)`                       | `Wield Power`   | `Activate Attack Effect`                                                 | Ch6 Attack type + Affliction/Damage/Nullify/Weaken                                                                       | attack effects                                                  | `powers/effect`, `checks`                          |
| `powers/control`              | child           | `[powers/control/.context/control-segment.md](../powers/control/.context/control-segment.md)`                   | `Wield Power`   | `Activate Control Effect`                                                | Ch6 Control type + control-typed effects                                                                                 | control/alter effects                                           | `powers/effect`, `checks`                          |
| `powers/defense`              | child           | `[powers/defense/.context/defense-segment.md](../powers/defense/.context/defense-segment.md)`                   | `Wield Power`   | `Activate Defense Effect`                                                | Ch6 Defense type + defense-typed effects                                                                                 | defense effects                                                 | `powers/effect`                                    |
| `powers/movement`             | child           | `[powers/movement/.context/movement-segment.md](../powers/movement/.context/movement-segment.md)`               | `Wield Power`   | `Activate Movement Effect`                                               | Ch6 Movement type + movement-typed effects                                                                               | movement effects                                                | `powers/effect`; `conflicts/turns` allotment later |
| `powers/sensory`              | child           | `[powers/sensory/.context/sensory-segment.md](../powers/sensory/.context/sensory-segment.md)`                   | `Wield Power`   | `Activate Sensory Effect`                                                | Ch6 Sensory type + Sense Types + sensory-typed effects                                                                   | sensory effects                                                 | `powers/effect`                                    |
| `powers/general`              | child           | `[powers/general/.context/general-segment.md](../powers/general/.context/general-segment.md)`                   | `Wield Power`   | `Activate General Effect`                                                | Ch6 General type + general-typed effects                                                                                 | general effects                                                 | `powers/effect`                                    |
| `powers/extras`               | child           | `[powers/extras/.context/extras-segment.md](../powers/extras/.context/extras-segment.md)`                       | `Wield Power`   | `Apply Extra`                                                            | Ch6 Extras                                                                                                               | positive modifiers                                              | `powers/effect`                                    |
| `powers/flaws`                | child           | `[powers/flaws/.context/flaws-segment.md](../powers/flaws/.context/flaws-segment.md)`                           | `Wield Power`   | `Apply Flaw`                                                             | Ch6 Flaws                                                                                                                | negative modifiers                                              | `powers/effect`                                    |
| `gear/equipment`              | child           | `[gear/equipment/.context/equipment-segment.md](../gear/equipment/.context/equipment-segment.md)`               | `Outfit Hero`   | `Equip Device`, `Invent Equipment`, `Command Construct`                  | Ch7 Devices/Equipment/Weapons/Armor/Inventing + Constructs                                                               | possession / invent / repair                                    | effect ids, not impl                               |
| `gear/headquarters`           | child           | `[gear/headquarters/.context/headquarters-segment.md](../gear/headquarters/.context/headquarters-segment.md)`   | `Outfit Hero`   | `Outfit Headquarters`                                                    | Ch7 Headquarters                                                                                                         | HQ features                                                     | little from equipment                              |
| `gear/vehicles`               | child           | `[gear/vehicles/.context/vehicles-segment.md](../gear/vehicles/.context/vehicles-segment.md)`                   | `Outfit Hero`   | `Outfit Vehicle`                                                         | Ch7 Vehicles                                                                                                             | vehicle traits                                                  | little from equipment                              |
| `conflicts/conditions`        | child           | `[conflicts/conditions/.context/conditions-segment.md](../conflicts/conditions/.context/conditions-segment.md)` | `Run Conflict`  | `Suffer Condition`, `Recover From Harm`                                  | Ch1 Conditions; Ch8 Challenges/hazards; Attacks; Defenses; Recovery                                                      | conditions, damage, recovery                                    | `checks`; **not** turns                            |
| `conflicts/actions`           | child           | `[conflicts/actions/.context/actions-segment.md](../conflicts/actions/.context/actions-segment.md)`             | `Run Conflict`  | `Spend Action`, `Perform Maneuver`                                       | Ch8 Action Types; Actions; Maneuvers                                                                                     | action types + maneuvers                                        | advantage tags; **not** initiative                 |
| `conflicts/turns`             | child           | `[conflicts/turns/.context/turns-segment.md](../conflicts/turns/.context/turns-segment.md)`                     | `Run Conflict`  | `Roll Initiative`, `Take Turn`                                           | Ch1 Action Round; Ch8 Action Rounds/Initiative/Taking Your Turn                                                          | initiative, turn order, allotments                              | stubs actions — almost no resolution               |




## Stories overlay (epic → chunks)

One epic may span many module chunks; one chunk may support more than one epic.


| Epic            | Chunks (existing)                                                                                                                                            | Mid-epic / grounding stories                                                                                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Create Hero`   | `character` (+ abilities spans), `skills`, `advantages`                                                                                                      | `Spend Power Points`, `Choose Complications`, `Buy Ability Ranks`, `Train Skills`, `Take Advantages`, `Pick Archetype` (TODO)                                                                          |
| `Advance Hero`  | `character` (awards / PL improvement spans)                                                                                                                  | `Raise Power Level`, `Spend Award Points` (TODO: more award paths)                                                                                                                                     |
| `Resolve Check` | `checks`                                                                                                                                                     | `Make Trait Check`, `Oppose Check`, `Assist Check`, `Make Routine Check`                                                                                                                               |
| `Wield Power`   | `powers/effect`, `powers/attack`, `powers/control`, `powers/defense`, `powers/movement`, `powers/sensory`, `powers/general`, `powers/extras`, `powers/flaws` | `Compose Effect`, `Pay Power Cost`, `Apply Extra`, `Apply Flaw`, `Activate Attack Effect`, `Activate Control Effect`, `Activate Defense Effect`, `Activate Movement Effect`, `Activate Sensory Effect` |
| `Outfit Hero`   | `gear/equipment`, `gear/headquarters`, `gear/vehicles`                                                                                                       | `Equip Device`, `Invent Equipment`, `Outfit Headquarters`, `Outfit Vehicle`, `Command Construct`                                                                                                       |
| `Run Conflict`  | `conflicts/turns`, `conflicts/actions`, `conflicts/conditions`                                                                                               | `Roll Initiative`, `Take Turn`, `Spend Action`, `Perform Maneuver`, `Suffer Condition`, `Recover From Harm`                                                                                            |


**Gap-fill segments:** none — all epics map to existing CE chunks.

**Nest map (CE — unchanged):**

```
powers/
  effect
  attack|control|defense|movement|sensory|general -> effect
  extras|flaws -> effect
conflicts/
  turns | actions | conditions
gear/
  equipment | headquarters | vehicles
checks | character | skills | advantages
```



## Independence (CE)

- Children depend on **parent base** (`powers/effect`), not on sibling children.
- `conflicts/turns` ⟂ `conflicts/actions` — sequence vs resolution.
- No `series` megamodule; no flat `powers`/`conflicts`/`gear` without children.



## Done-check



### Clean engineering

- [x] Nested where shared base exists; flat otherwise.
- [x] Shared effect mechanics once under `powers/effect`.
- [x] Domain-noun paths; independent-implement grain.
- [x] Segments under `{module}/.context/` (same tree as generate).
- [x] Every module row **points at** its chunk path.



### Stories (additive)

- [x] `stories.md` lens applied.
- [x] Epics / grounding stories are verb–noun; stakeholder-observable.
- [x] Epic count = 6 ≠ chapter / major-heading count (not TOC-mirrored).
- [x] Prior CE columns and chunk links preserved; Stories **added**, not substituted.
- [x] Every epic maps to ≥1 existing chunk; no re-chunk.