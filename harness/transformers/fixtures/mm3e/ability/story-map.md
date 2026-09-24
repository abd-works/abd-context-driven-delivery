# Story Map — MM3E [Ability] Module (Pass 2)

Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).
Source epic from global map: **(E) Assign Abilities**. Pass 2 — full decomposition of all four Key Abstractions.

---

(E) Assign Abilities
    (E) Configure Ability Scores
        (S) Player --> Set Ability Rank
        (S) Player --> Designate Ability Rank Portion as Enhanced
        (S) System --> Cascade Trait Changes on Ability Rank Alteration
        (S) System --> Enforce Ability Rank Ceiling per Power Level
    (E) Configure Derived Defenses
        (S) System --> Derive Base Defense Rank from Ability
        (S) Player --> Increase Defense Rank Above Ability Base
        (S) System --> Enforce Toughness Increase Restriction
        (S) System --> Derive Initiative Modifier from Agility
    (E) Handle Absent Ability
        (S) System --> Apply Absent Ability Capability Restrictions
        (S) System --> Grant Bonus Power Points for Absent Ability
        (S) GM --> Authorize Hero to Have Absent Ability
    (E) Handle Debilitated Ability
        (S) System --> Apply Debilitated Ability Condition Effects
        (S) System --> Prevent Further Rank Reduction When Debilitated
        (S) System --> Clear Debilitated State When Ability Rank Recovers

---

## Consolidation Notes (for AC phase)

### Set Ability Rank
Groups buying-up and reducing-below-0 into one parameterized story. The 2 power point per rank formula applies in both directions. AC must specify per direction:
- Buying up (rank 0 → positive): spend 2 pp per +1 rank; each +1 raises ability from current value; cannot exceed power level cap.
- Reducing below 0 (rank 0 → negative): gain 2 pp per −1 rank; cannot go below −5 voluntarily.
- Applies to all eight named abilities (STR, STA, AGL, DEX, FGT, INT, AWE, PRE) with identical formula.

### Apply Absent Ability Capability Restrictions
Groups per-ability absence effects into one parameterized story. All share "automatic fail on related checks" but have distinct capability losses per ability. AC must specify per ability:
- No Strength: cannot exert physical force; auto-fail Athletics, strength-based attack checks.
- No Stamina: no living-body mechanics; damage/recovery as inanimate object; immune to fatigue; no Fortitude defense.
- No Dexterity: cannot manipulate objects; no physical attacks; auto-fail Dexterity checks.
- No Agility: no self-propelled movement; no Dodge defense; auto-fail Agility checks.
- No Fighting: no close attacks; auto-fail close attack checks.
- No Intellect: automaton; immune to mental effects and interaction skills; no Will defense.
- No Awareness: completely unaware; also no Presence automatically; immune to mental effects; treated as inanimate object.
- No Presence: cannot interact; immune to interaction skills; no Will defense.

### Apply Debilitated Ability Condition Effects
Groups four distinct condition sets by ability grouping into one parameterized story. Trigger is the same (rank drops below −5) but outcomes differ by ability. AC must specify per group:
- STR, AGL, or DEX: collapse — defenseless + immobilized + stunned (conscious and aware).
- STA: dying condition + additional −5 modifier on Fortitude checks to avoid death.
- FGT: dazed + defenseless; cannot make close attacks.
- INT, AWE, or PRE: unaware; persists until ability restored to at least −5.

### Passive vs Active Runtime Analysis
- Set Ability Rank → character creation / advancement time; no runtime story needed beyond cascade.
- Designate Ability Rank Portion as Enhanced → character creation time; runtime story is nullification (owned by Power module).
- Cascade Trait Changes → passive system behavior at the moment a rank changes; maps as a system story.
- Derive Base Defense Rank from Ability → passive derivation; automatic at character creation and on any rank change; mapped as system story.
- Apply Absent Ability Capability Restrictions → character design time; applied at creation; no separate runtime story for ongoing enforcement (the restrictions are always in effect).
- Apply Debilitated Ability Condition Effects → runtime (occurs when rank is reduced below −5 by a game effect); maps as system story.
- Clear Debilitated State When Ability Rank Recovers → runtime (recovery when rank returns to −5 or above); maps as system story.

---

## Context Gaps

- **GM authorization workflow for absent abilities**: Source requires GM permission for heroes to lack an ability but does not specify whether an online tool prompts for approval, logs a flag, or blocks the action outright — UX and workflow decision needed.
- **Enhanced ability nullification interaction**: When an enhanced ability rank is nullified, the base (natural) portion of the rank should remain — the exact system behavior for partial nullification (which portion is reduced and in what order) requires clarification from the Power module.
- **Debilitation recovery source**: The specific game effect (power, healing, time) that restores a debilitated ability rank is owned by the module that caused the debilitation — the Ability module detects when rank recovers to ≥ −5 and clears the debilitated state, but does not itself initiate the recovery.
- **Defense class display vs. calculation separation**: Whether the online tool derives and displays defense class (Dodge + 10 etc.) as a separate computed field on the character sheet, or only exposes raw defense ranks, is a UI/product decision.
