# Story Map — Power Module (Pass 2)

Module scope: Power effects (Affliction through Weaken), power types, action/range/duration defaults, Extras, Flaws, Descriptors, and modifier math.
Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).
Maps to existing backbone epic: **(E) Configure Powers**

---

(E) Configure Powers
    (E) Configure Attack Effect
        (S) Player --> Select Affliction Effect and Configure Condition Set
        (S) Player --> Select Damage Effect for Close Combat
        (S) Player --> Select Blast Effect for Ranged Energy Attack
        (S) Player --> Select Deflect Effect for Ranged Protection
        (S) Player --> Select Nullify Effect and Define Target Descriptor
        (S) Player --> Select Weaken Effect and Define Target Trait
        (S) System --> Resolve Affliction Resistance Check and Apply Condition Degree
        (S) System --> Recover from Affliction Condition at End of Turn
        (S) System --> Resolve Damage Resistance Check and Apply Damage Condition
        (S) System --> Resolve Weaken Resistance Check and Reduce Target Trait
        (S) System --> Recover Weakened Trait at One Point per Round
        (S) System --> Resolve Nullify Opposed Check Against Target Effect Rank
    (E) Configure Defense Effect
        (S) Player --> Select Protection Effect for Toughness Bonus
        (S) Player --> Select Immunity Effect and Define Covered Effect Set
        (S) Player --> Configure Partial Immunity for Half-Effect Protection
        (S) Player --> Select Regeneration Effect for Progressive Damage Recovery
        (S) Player --> Select Immortality Effect for Death Recovery
        (S) System --> Apply Immunity Check Against Matching Power Descriptor
        (S) System --> Remove Toughness Penalty via Regeneration Recovery Phase
        (S) System --> Remove Damage Condition via Regeneration Condition Phase
        (S) System --> Recover from Death via Immortality After Time Elapses
    (E) Configure Mobility Effect
        (S) Player --> Select Flight Effect for Aerial Movement
        (S) Player --> Select Speed Effect for Ground Velocity Enhancement
        (S) Player --> Select Burrowing Effect for Underground Movement
        (S) Player --> Select Swimming Effect for Aquatic Movement
        (S) Player --> Select Leaping Effect for Extended Jumping
        (S) Player --> Select Teleport Effect for Instantaneous Relocation
        (S) Player --> Select Movement Effect and Choose Special Movement Mode
        (S) System --> Calculate Flight Speed Rank from Effect Rank
        (S) System --> Calculate Burrowing Speed Rank with Terrain Penalty
        (S) System --> Calculate Jump Distance Rank from Leaping Rank
        (S) System --> Validate Teleport Destination as Known or Accurately Sensed
    (E) Configure Sensory Effect
        (S) Player --> Select Senses Effect and Allocate Sense Enhancements
        (S) Player --> Select Concealment Effect and Choose Hidden Sense Type
        (S) Player --> Select Remote Sensing Effect for Displaced Perception
        (S) Player --> Select Mind Reading Effect for Mental Contact
        (S) Player --> Select Communication Effect and Choose Sense Type Medium
        (S) Player --> Select Comprehend Effect and Choose Communication Type
        (S) System --> Grant Total Concealment Against Chosen Sense Type
        (S) System --> Suppress Normal Senses During Remote Sensing
        (S) System --> Mark Character as Vulnerable During Remote Sensing
        (S) System --> Resolve Mind Reading Opposed Check Against Will Defense
        (S) System --> Break Mind Reading Contact on Target Will Check Success
    (E) Configure Control Effect
        (S) Player --> Select Create Effect and Set Volume Parameters
        (S) Player --> Select Move Object Effect for Telekinetic Manipulation
        (S) Player --> Select Environment Effect and Choose Environmental Changes
        (S) Player --> Select Illusion Effect and Choose Sense Type Coverage
        (S) Player --> Select Luck Control Effect and Define Hero Point Capability
        (S) Player --> Select Summon Effect and Define Minion Parameters
        (S) Player --> Select Transform Effect and Set Transformation Scope
        (S) System --> Enforce Created Object Volume and Toughness from Effect Rank
        (S) System --> Dissolve Created Object When Effect is Not Maintained
        (S) System --> Resolve Move Object Strength Check for Resisting Targets
        (S) System --> Resolve Insight Check to Detect Illusion
        (S) System --> Apply Summon Dazed Condition on Minion Arrival
        (S) System --> Dismiss Summon When Minion is Incapacitated
        (S) System --> Resolve Transform Fortitude Resistance for Living Targets
        (S) System --> Revert Transformation When Sustained Effect Ends
    (E) Configure General Effect
        (S) Player --> Select Variable Effect and Define Effect Type Pool
        (S) Player --> Select Growth Effect for Physical Size Increase
        (S) Player --> Select Shrinking Effect for Physical Size Reduction
        (S) Player --> Select Insubstantial Effect and Choose Physical Form
        (S) Player --> Select Enhanced Trait Effect and Choose Target Trait
        (S) Player --> Select Healing Effect for Damage Condition Removal
        (S) Player --> Select Elongation Effect for Extended Reach
        (S) Player --> Select Quickness Effect for Task Time Reduction
        (S) Player --> Select Feature Effect and Define Minor Game Capability
        (S) System --> Apply Growth Ability and Size Bonuses and Penalties per Rank
        (S) System --> Apply Shrinking Defense and Stealth Bonuses and Penalties per Rank
        (S) System --> Enforce Variable Pool Size as Rank Times Five Points
        (S) System --> Enforce PL Limits on Variable-Built Effects
        (S) System --> Apply Healing Check and Remove Damage Condition from Most Severe
        (S) System --> Block Healing Reuse on Same Target Within Scene
    (E) Apply Per-Rank Modifiers
        (S) System --> Set Default Action, Range, Duration for Effect Type
        (S) System --> Calculate Base Cost per Rank from Effect Definition
        (S) Player --> Apply Per-Rank Extra to Raise Cost per Rank
        (S) Player --> Apply Per-Rank Flaw to Lower Cost per Rank
        (S) System --> Enforce Minimum One Point per Rank Floor After Flaws
        (S) Player --> Apply Area Extra to Replace Attack Check with Dodge Save
        (S) System --> Apply Area Dodge Save DC as Ten Plus Effect Rank
        (S) System --> Reduce Area Effect to Half Rank on Dodge Save Success
        (S) Player --> Apply Multiattack Extra for Multiple Target Coverage
        (S) System --> Apply Multiattack Bonus DC on Multiple Success Degrees
    (E) Apply Flat Modifiers
        (S) Player --> Apply Accurate Extra for Attack Check Bonus
        (S) Player --> Apply Penetrating Extra to Overcome Impervious Defense
        (S) Player --> Apply Activation Flaw to Require Power Preparation
        (S) Player --> Apply Check Required Flaw to Gate Effect on Skill Check
        (S) Player --> Apply Limited Flaw to Restrict Effect Circumstances
        (S) Player --> Apply Removable Flaw to Convert Power to Device
        (S) System --> Calculate Final Power Cost with Flat Modifier Adjustments
        (S) System --> Enforce Minimum One Point Total Power Cost After Flat Flaws
        (S) System --> Apply Penetrating Rank Against Impervious Toughness Threshold
        (S) System --> Require Activation Action Before Power Effects Become Available
        (S) System --> Gate Effect Activation on Check Required Skill Check Success
        (S) System --> Allow Removal of Device When Character is Stunned and Defenseless
    (E) Assign Power Descriptors
        (S) Player --> Assign Origin Descriptor to Power Set
        (S) Player --> Assign Source Descriptor to Power Effect
        (S) Player --> Assign Result Descriptor to Power Effect
        (S) System --> Match Power Descriptor Against Immunity Effect Coverage
        (S) System --> Match Power Descriptor Against Nullify Effect Target
        (S) GM --> Approve Descriptor Interaction Between Powers
    (E) Organize Power Arrays
        (S) Player --> Build Power Array with Base Effect
        (S) Player --> Add Alternate Effect to Array within Primary Effect Cost Limit
        (S) Player --> Add Dynamic Alternate Effect for Simultaneous Use
        (S) Player --> Switch Active Effect in Array as Free Action
        (S) System --> Enforce Array Mutual Exclusivity Rule for Non-Dynamic Effects
        (S) System --> Propagate Array Disable Equally to All Alternate Effects
        (S) System --> Reallocate Power Points Among Dynamic Array Effects per Turn
        (S) System --> Enforce Dynamic Effect Point Total Against Array Pool Size

---

## Consolidation Notes (for AC phase)

### Configure Attack Effect
- **Select Affliction Effect and Configure Condition Set** / **Resolve Affliction Resistance Check and Apply Condition Degree** / **Recover from Affliction Condition at End of Turn**: These three stories form a natural cluster — acquisition, resolution, and recovery. AC must cover: condition set definition at acquisition (exactly 3 conditions in degree order), attack check prerequisite, resistance type choice (Fort vs Will), degree of failure mapping, end-of-turn recovery check, and third-degree special recovery rule (1 minute after effect ends).
- **Select Blast Effect** is mechanically identical to Damage + Ranged extra. AC must confirm the 2 pp/rank cost is already calculated (base 1 + Ranged 1) and that the attack check uses Ranged vs Dodge.
- **Resolve Nullify Opposed Check**: AC must specify both branches — success (effect countered, target can reactivate) and failure (effect continues). Also specify what "countered" means for sustained vs permanent effects.

### Configure Defense Effect
- **Configure Partial Immunity**: Half-rank immunity costs half the full rank cost. AC must specify that partial immunity reduces the effect rank by half (round down) against the covered effect, not that it provides a bonus.
- **Recover from Death via Immortality**: AC must specify the time-rank formula (19 − Immortality rank) and the edge case at rank 20 (recover at start of each action round).

### Configure Mobility Effect
- **Select Movement Effect and Choose Special Movement Mode**: Each mode (Dimension Travel, Wall-Crawling, etc.) has sub-rules. AC can parametrize by mode or write per-mode AC. Consolidation note: pass 2 groups all Movement modes under one story; AC phase should expand per mode if distinct behavior is needed.

### Configure Control Effect
- **Select Create Effect** / **Enforce Created Object Volume and Toughness from Effect Rank** / **Dissolve Created Object**: AC must specify permanence option (spend PP equal to rank).
- **Select Summon Effect** / **Apply Summon Dazed Condition** / **Dismiss Summon**: AC must cover PP = rank × 15, PL ≤ rank, dazed on arrival, directing = move action, and disappearance on incapacitation.

### Configure General Effect
- **Select Insubstantial Effect**: 4 ranks at 5 pp/rank each — AC must confirm cost per form rank and rules per form (especially rank 4 Incorporeal interaction with physical world).
- **Select Variable Effect**: AC must cover pool size = rank × 5, standard action to reallocate, PL limits on built effects, and pool reset when effect not maintained.

### Apply Per-Rank Modifiers
- **Enforce Minimum One Point per Rank Floor**: Edge case when flaws reduce cost to fractional — at this point each extra flaw grants ranks at ratio (e.g., 1:2 = 1 pp per 2 ranks). AC must specify the fractional cost progression.

### Assign Power Descriptors
- **Match Power Descriptor Against Immunity / Nullify**: AC must specify matching logic — descriptors are intentionally flexible (lightning matches electricity); GM is final arbitrator.

### Organize Power Arrays
- **Add Alternate Effect within Primary Effect Cost Limit**: AC must confirm: (a) total cost including all extras and flaws on the alternate, not just rank × cost, must be ≤ primary; (b) permanent effects cannot be alternates.
- **Reallocate Power Points Among Dynamic Array Effects**: AC must confirm: reallocation once per turn as free action; points not allocated = inactive at that rank; combined allocation cannot exceed total pool.

---

## Context Gaps

- **Morph effect**: Referenced in source chunks (chunk_121) as a distinct named effect but not included in the module partition's core terms list. Potentially belongs in this module or a separate "Form Change" module.
- **Mind Control**: Referenced in source (chunk_120) as a significant effect but not in the partition's core terms. May be in scope — partition may under-represent Affliction-based control.
- **Mental Blast**: Referenced in source (chunk_117). May be Damage (Perception range) preconfiguration — not in partition.
- **Extra Limbs**: Referenced in source (chunk_104). Not in partition core terms — may be a Feature instance rather than a standalone effect.
- **Element Control and Energy Control**: Referenced in source (chunks 100, 103) as power families rather than individual effects. Not in partition — context only.
- **Force Field**: Referenced in source (chunk_107) as a named configuration (Protection + Sustained extra). Not in partition.
- **Full Extras/Flaws catalog**: Only the 8 most common extras and flaws are in the partition. The full catalog includes Increased Duration, Extended Range, Increased Action, Secondary Effect, Variable Descriptor, Side Effect, and many others. AC phase should note these as out-of-scope for MVP but available via the Modifier KA pattern.
- **Routine effect checks**: Chunk_086 covers routine use of effects. Not mapped as a story — may need a story under Configure Attack Effect or Configure General Effect if the application builds an "auto-resolve" feature.
- **Countering effects**: Chunk_088 (N-W table section) mentions countering in the same section as power effect summaries. Countering as a combat mechanic (not Nullify) may need a story under Combat module.
