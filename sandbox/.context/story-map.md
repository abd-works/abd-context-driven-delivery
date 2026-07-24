---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Heroes Handbook

**Sources / context:** `sandbox/modules/checks/.context/module-context.md`, `sandbox/modules/character/.context/module-context.md`, `sandbox/modules/character/.context/character-segment.md`, `sandbox/modules/skills/.context/module-context.md`, `sandbox/modules/skills/.context/skills-segment.md`, `sandbox/modules/advantages/.context/module-context.md`, `sandbox/modules/advantages/.context/advantages-segment.md`, `sandbox/modules/conflicts/conditions/.context/module-context.md`, `sandbox/modules/conflicts/conditions/.context/conditions-segment.md` (basic/combined conditions, hazards, recovery — not index stubs; Damage/Affliction resist deferred to power-use), `sandbox/modules/conflicts/actions/.context/module-context.md`, `sandbox/modules/conflicts/actions/.context/actions-segment.md` (action types, named actions, maneuvers — not index stubs), `sandbox/modules/powers/.context/module-context.md`, `sandbox/modules/powers/effect/.context/effect-segment.md` (shared Effect acquire/cost/descriptors/modifiers/activate/counter — not index stubs), `sandbox/stories/play-core-mechanics/story-context.md` (name reconciliation). Further power children deferred.

---

(E) Resolve Check
    (E) Resolve Checks
        (S) Player --> Resolve Ability Check
        (S) Player --> Make Routine Check
        (S) Player --> Perform Opposing Check
        (S) Player --> Perform Assisted Check

(E) Build Character
    (E) Build Character Sheet
        (S) Player --> Create Character
        (S) Player --> Update Ability Rank
        (S) Player --> Update Defense Ranks
        (S) Player --> Read Initiative

(E) Purchase Skills
    (E) Purchase Skill Ranks
        (S) Player --> Update Skill Rank
        (S) Player --> Update Expertise Rank
        (S) Player --> Update Combat Skill Rank

(E) Use Skills
    (E) Resolve Skill Uses
        (S) Player --> Resolve Skill Check
        (S) Player --> Oppose Skill Check
        (S) Player --> Notice Detail
        (S) Player --> Investigate Scene
        (S) Player --> Gather Information
    (E) Interact Socially
        (S) Player --> Bluff Target
        (S) Player --> Disguise Appearance
        (S) Player --> Feint in Combat
        (S) Player --> Trick Opponent
        (S) Player --> Coerce Target
        (S) Player --> Demoralize Opponent
    (E) Apply Craft Skills
        (S) Player --> Perform Sleight
        (S) Player --> Work Technology
        (S) Player --> Treat Condition
        (S) Player --> Operate Vehicle

(E) Purchase Advantages
    (E) Purchase Advantage Ranks
        (S) Player --> Update Advantage Rank
        (S) Player --> Take Advantage

(E) Use Advantages
    (E) Apply Advantage Benefits
        (S) Player --> Apply Combat Advantage
        (S) Player --> Spend Fortune Advantage
        (S) Player --> Substitute Skill Advantage
        (S) Player --> Fascinate Target
        (S) Player --> Call Connected Favor
        (S) Player --> Field Follower
        (S) Player --> Claim Benefit

(E) Resolve Conditions
    (E) Resolve Condition State
        (S) Player --> Suffer Condition
        (S) Player --> Suffer Combined Condition
        (S) Player --> Recover From Harm
        (S) Player --> Resist Poison
        (S) Player --> Resist Disease
        (S) Player --> Endure Environment

(E) Resolve Actions
    (E) Resolve Action Economy
        (S) Player --> Aid Ally
        (S) Player --> Delay Turn
        (S) Player --> Disarm Opponent
        (S) Player --> Grab Opponent
        (S) Player --> Escape Grab
        (S) Player --> Move Character
        (S) Player --> Ready Action
        (S) Player --> Perform Maneuver

(E) Powers
    (E) Effect
        (S) Player --> Compose Effect
        (S) Player --> Pay Power Cost
        (S) Player --> Apply Descriptor
        (S) Player --> Apply Extra
        (S) Player --> Apply Flaw
        (S) Player --> Activate Effect
        (S) Player --> Counter Effect
        (S) Player --> Resist Power Effect

---

## Scope boundary

**In scope:** `Resolve Check`; `Build Character`; `Purchase Skills` / `Use Skills`; `Purchase Advantages` / `Use Advantages`; `Resolve Conditions`; `Resolve Actions`; `Powers` master epic with `Effect` sub-epic (shared Effect protocol from effect-segment — compose, cost, descriptors, extras/flaws, activate, counter, resist). Point totals refresh as a consequence of rank mutation, not a named story.
**Out of scope:** Typed power children (attack/control/defense/movement/general/extras/flaws/sensory) until their ticks; complications; PL enforcement; turns / initiative allotment; thin-slice backlog. Feint/Demoralize stay under Use Skills. Damage/Affliction specifics deepen under attack (and peers) later; Resist Power Effect is the shared resist seam. Deeper activity/sub-epic redesign deferred. Index mid-epic columns are stubs, not story inventory.

---
