---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Heroes Handbook

**Sources / context:** `sandbox/stories/play-core-mechanics/story-context.md` (name reconciliation only)

---

(E) Build Character
    **Sources / context:** `sandbox/modules/character/.context/module-context.md`, `sandbox/modules/character/.context/character-segment.md`, `sandbox/modules/checks/.context/module-context.md`
    (E) Build Character Sheet
        (S) Player --> Create Character
        (S) Player --> Update Ability Rank
        (S) Player --> Update Defense Ranks
        (S) Player --> Read Initiative
    (E) Resolve Checks
        (S) Player --> Resolve Ability Check
        (S) Player --> Make Routine Check
        (S) Player --> Perform Opposing Check
        (S) Player --> Perform Assisted Check

(E) Use Skills
    **Sources / context:** `sandbox/modules/skills/.context/module-context.md`, `sandbox/modules/skills/.context/skills-segment.md`
    (E) Purchase Skills
        (S) Player --> Update Skill Rank
        (S) Player --> Update Expertise Rank
        (S) Player --> Update Combat Skill Rank
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

(E) Use Advantages
    **Sources / context:** `sandbox/modules/advantages/.context/module-context.md`, `sandbox/modules/advantages/.context/advantages-segment.md`
    (E) Purchase Advantages
        (S) Player --> Update Advantage Rank
        (S) Player --> Take Advantage
    (E) Apply Advantage Benefits
        (S) Player --> Apply Combat Advantage
        (S) Player --> Spend Fortune Advantage
        (S) Player --> Substitute Skill Advantage
        (S) Player --> Fascinate Target
        (S) Player --> Call Connected Favor
        (S) Player --> Field Follower
        (S) Player --> Claim Benefit

(E) Resolve Conflict
    (E) Resolve Conditions
        **Sources / context:** `sandbox/modules/conflicts/conditions/.context/module-context.md`, `sandbox/modules/conflicts/conditions/.context/conditions-segment.md`
        (E) Resolve Condition State
            (S) Player --> Suffer Condition
            (S) Player --> Suffer Combined Condition
            (S) Player --> Recover From Harm
            (S) Player --> Resist Poison
            (S) Player --> Resist Disease
            (S) Player --> Endure Environment
    (E) Resolve Actions
        **Sources / context:** `sandbox/modules/conflicts/actions/.context/module-context.md`, `sandbox/modules/conflicts/actions/.context/actions-segment.md`
        (E) Resolve Action Economy
            (S) Player --> Aid Ally
            (S) Player --> Delay Turn
            (S) Player --> Disarm Opponent
            (S) Player --> Grab Opponent
            (S) Player --> Escape Grab
            (S) Player --> Move Character
            (S) Player --> Ready Action
            (S) Player --> Perform Maneuver
    (E) Resolve Turns
        **Sources / context:** `sandbox/modules/conflicts/turns/.context/module-context.md`, `sandbox/modules/conflicts/turns/.context/turns-segment.md`
        (E) Resolve Turn Cycle
            (S) Player --> Roll Initiative
            (S) Player --> Resolve Surprise
            (S) Player --> Start Turn
            (S) Player --> Allot Turn Actions
            (S) Player --> End Turn

(E) Use Powers
    **Sources / context:** `sandbox/modules/powers/.context/module-context.md`
    (E) Use Effect
        **Sources / context:** `sandbox/modules/powers/effect/.context/effect-segment.md`
        (S) Player --> Compose Effect
        (S) Player --> Pay Power Cost
        (S) Player --> Apply Descriptor
        (S) Player --> Activate Effect
        (S) Player --> Counter Effect
        (S) Player --> Resist Power Effect
    (E) Use Attack Powers
        **Sources / context:** `sandbox/modules/powers/attack/.context/module-context.md`, `sandbox/modules/powers/attack/.context/attack-segment.md`
        (S) Player --> Inflict Damage
        (S) Player --> Resist Damage
        (S) Player --> Impose Affliction
        (S) Player --> Shake Off Affliction
        (S) Player --> Nullify Power
        (S) Player --> Weaken Trait
        (S) Player --> Resist Weaken
    (E) Use Control Powers
        **Sources / context:** `sandbox/modules/powers/control/.context/module-context.md`, `sandbox/modules/powers/control/.context/control-segment.md`
        (S) Player --> Create Object
        (S) Player --> Alter Environment
        (S) Player --> Project Illusion
        (S) Player --> Disbelieve Illusion
        (S) Player --> Control Luck
        (S) Player --> Move Object
        (S) Player --> Summon Minion
        (S) Player --> Transform Object
    (E) Use Defense Powers
        **Sources / context:** `sandbox/modules/powers/defense/.context/module-context.md`, `sandbox/modules/powers/defense/.context/defense-segment.md`
        (S) Player --> Use Deflect
        (S) Player --> Use Immortality
        (S) Player --> Use Immunity
        (S) Player --> Activate Insubstantial
        (S) Player --> Use Protection
        (S) Player --> Use Regeneration
        (S) Player --> Use Healing
    (E) Use Movement Powers
        **Sources / context:** `sandbox/modules/powers/movement/.context/module-context.md`, `sandbox/modules/powers/movement/.context/movement-segment.md`
        (S) Player --> Use Speed Movement
        (S) Player --> Use Leaping
        (S) Player --> Use Teleport
        (S) Player --> Use Dimension Travel
        (S) Player --> Use Movement Mode
    (E) Use General Powers
        **Sources / context:** `sandbox/modules/powers/general/.context/module-context.md`, `sandbox/modules/powers/general/.context/general-segment.md`
        (S) Player --> Activate Size Change
        (S) Player --> Use Enhanced Trait
        (S) Player --> Use Extra Limbs
        (S) Player --> Use Feature
        (S) Player --> Use Elongation
        (S) Player --> Use Morph
        (S) Player --> Use Quickness
        (S) Player --> Use Variable
    (E) Use Powers with Modifiers
        **Sources / context:** `sandbox/modules/powers/extras/.context/module-context.md`, `sandbox/modules/powers/extras/.context/extras-segment.md`, `sandbox/modules/powers/flaws/.context/module-context.md`, `sandbox/modules/powers/flaws/.context/flaws-segment.md`
        **Verify:** `sandbox/.context/sessions/discovery/segment-verify-extras-flaws.md` — completeness PASS (59/59). Inventory re-proved against OK bodies: eleven mechanic sub-epics stay (not one-story-per-modifier-title); Apply / Arrays / Area / Attack Delivery / Who Affected / Resistance Path / Timing·Scale / Link·Multiattack / Conceal / Constrain.
        (E) Apply Modifiers
            (S) Player --> Apply Extra
            (S) Player --> Apply Flaw
            (S) Player --> Apply Feature Modifier
            (S) Player --> Apply Quirk
            (S) Player --> Apply Sleep Modifier
        (E) Resolve Arrays
            (S) Player --> Switch Alternate Effect
            (S) Player --> Allocate Dynamic Array
        (E) Resolve Area Effects
            (S) Player --> Resolve Area Effect
            (S) Player --> Resolve Lingering Area
            (S) Player --> Resolve Perception Area
        (E) Modify Attack Delivery
            (S) Player --> Apply Accurate Bonus
            (S) Player --> Resolve Homing Attack
            (S) Player --> Resolve Indirect Attack
            (S) Player --> Resolve Ricochet Attack
            (S) Player --> Split Effect
            (S) Player --> Extend Close Reach
            (S) Player --> Make Effect Precise
        (E) Modify Who Is Affected
            (S) Player --> Affect Corporeal Target
            (S) Player --> Affect Insubstantial Target
            (S) Player --> Affect Objects
            (S) Player --> Affect Others
            (S) Player --> Convert Personal to Attack
            (S) Player --> Select Affected Targets
        (E) Modify Resistance Path
            (S) Player --> Apply Impervious
            (S) Player --> Apply Penetrating
            (S) Player --> Change Resistance Defense
            (S) Player --> Apply Incurable
            (S) Player --> Spread Contagious Effect
            (S) Player --> Resolve Secondary Effect
            (S) Player --> Reverse Effect Conditions
        (E) Modify Timing and Scale
            (S) Player --> Increase Effect Duration
            (S) Player --> Increase Effect Range
            (S) Player --> Extend Effect Range
            (S) Player --> Increase Carried Mass
            (S) Player --> Use Effect as Reaction
            (S) Player --> Sustain Effect
            (S) Player --> Trigger Effect
            (S) Player --> Vary Effect Descriptor
            (S) Player --> Cross Dimensional Range
        (E) Link and Multiattack
            (S) Player --> Link Effects
            (S) Player --> Resolve Multiattack
        (E) Conceal Modifier Presence
            (S) Player --> Make Effect Subtle
            (S) Player --> Make Effect Insidious
            (S) Player --> Make Effect Innate
        (E) Constrain Effect Use
            (S) Player --> Activate Constrained Power
            (S) Player --> Require Effect Check
            (S) Player --> Maintain Concentration
            (S) Player --> Diminish Effect Range
            (S) Player --> Suffer Distraction
            (S) Player --> Fade Effect Ranks
            (S) Player --> Suffer Feedback
            (S) Player --> Require Grab to Use
            (S) Player --> Increase Required Action
            (S) Player --> Limit Effect Circumstances
            (S) Player --> Make Effect Noticeable
            (S) Player --> Make Effect Permanent
            (S) Player --> Remove Device Power
            (S) Player --> Add Resistance Check
            (S) Player --> Require Sense Dependence
            (S) Player --> Suffer Side Effect
            (S) Player --> Suffer Tiring Fatigue
            (S) Player --> Lose Effect Control
            (S) Player --> Roll Unreliable Effect
    (E) Use Sensory Powers
        **Sources / context:** `sandbox/modules/powers/sensory/.context/module-context.md`, `sandbox/modules/powers/sensory/.context/sensory-segment.md`
        **Verify:** `sandbox/.context/sessions/discovery/segment-verify-sensory.md` — Senses options re-extracted (PDF pp.177–180); `verify_segment_completeness` PASS (27/27). Sense Danger stays split; missing X-Ray Vision header in Deluxe PDF (primer-only) → scenario under Use Senses / Penetrates Concealment if needed.
        (S) Player --> Communicate Remotely
        (S) Player --> Use Comprehend
        (S) Player --> Activate Concealment
        (S) Player --> Read Mind
        (S) Player --> Use Remote Sensing
        (S) Player --> Sense Danger
        (S) Player --> Use Senses

(E) Use Gear
    **Sources / context:** `sandbox/modules/gear/equipment/.context/module-context.md` (gear peers; equipment → vehicles → headquarters per build-order)
    **Verify:** `sandbox/.context/sessions/discovery/segment-verify-gear.md` — equipment weapons/armor + vehicles + HQ features re-extracted; HQ `verify_segment_completeness` PASS (28/28). Weapon/armor table rows stay scenarios under Use Equipment Effect; Operate Vehicle under Use Skills.
    (E) Use Equipment
        **Sources / context:** `sandbox/modules/gear/equipment/.context/module-context.md`, `sandbox/modules/gear/equipment/.context/equipment-segment.md`
        (S) Player --> Acquire Device
        (S) Player --> Borrow Device
        (S) Player --> Invent Device
        (S) Player --> Jury-Rig Invention
        (S) Player --> Perform Magical Ritual
        (S) Player --> Purchase Equipment
        (S) Player --> Outfit Utility Belt
        (S) Player --> Ready On-Hand Equipment
        (S) Player --> Damage Gear Item
        (S) Player --> Repair Gear Item
        (S) Player --> Use Equipment Effect
        (S) Player --> Create Construct
        (S) Player --> Command Construct
        (S) Player --> Repair Construct
    (E) Use Vehicles
        **Sources / context:** `sandbox/modules/gear/vehicles/.context/module-context.md`, `sandbox/modules/gear/vehicles/.context/vehicles-segment.md`
        (S) Player --> Outfit Vehicle
        (S) Player --> Share Team Vehicle
        (S) Player --> Swap Alternate Vehicle
        (S) Player --> Activate Vehicle Feature
        (S) Player --> Outfit Special Vehicle
    (E) Use Headquarters
        **Sources / context:** `sandbox/modules/gear/headquarters/.context/module-context.md`, `sandbox/modules/gear/headquarters/.context/headquarters-segment.md`
        (S) Player --> Outfit Headquarters
        (S) Player --> Share Team Headquarters
        (S) Player --> Swap Alternate Headquarters
        (S) Player --> Use Combat Simulator
        (S) Player --> Use HQ Defense
        (S) Player --> Open HQ Portal
        (S) Player --> Apply Dual Size
        (S) Player --> Use Temporal Limbo
        (S) Player --> Use HQ Facility
        (S) Player --> Rebuild Headquarters

---

## Scope boundary

**In scope:** `Build Character` (sheet + Resolve Checks); `Use Skills` (purchase + use); `Use Advantages` (purchase + use); `Resolve Conflict` (Conditions / Actions / Turns); `Powers` (`Use Effect` + typed Use … Powers + `Use Powers with Modifiers` + `Use Sensory Powers`); `Use Gear` (Equipment / Vehicles / Headquarters). Sensory: Activate Concealment covers impose/attack-area scenarios; Sense Danger split from Use Senses. Operate Vehicle stays under Use Skills. Sources hang on the epic/sub-epic they ground. Point totals refresh as a consequence of rank mutation, not a named story.
**Map status:** discovery story-map **done** — thin-slice unlocked (order: `sandbox/modules/.context/module-build-order.md`, checks/character spine first).
**Out of scope:** TBD story scaffolds (map discovery stories named); duplicating Operate Vehicle under Use Vehicles; separate Impose Concealment story; measurement as its own epic (folded into checks); blank Activate wrappers; Purchase typed power siblings (acquire stays Effect); complications; PL enforcement. Feint/Demoralize stay under Use Skills. Disbelieve Illusion stays under Use Control. Damage recovery remains Recover From Harm; Resist Damage stays under Use Attack Powers. Index mid-epic columns are stubs, not story inventory. Chunk repairs done: extras/flaws 59/59, Senses options 27/27, HQ features 28/28.

---
