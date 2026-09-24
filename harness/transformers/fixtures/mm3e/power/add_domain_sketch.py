#!/usr/bin/env python3
"""Add #### Domain Sketch sections to each #### term in power.md."""
import re

SKETCH_DATA = {
    "effect": [
        "is the *atomic rules-defined unit* of superhuman capability — the named, typed, mechanically complete building block",
        "carries five fixed properties: type, action, range, duration, and cost per rank — all set at acquisition",
        "is acquired in ranks; higher rank means greater scale, intensity, reach, or effect magnitude",
        "exposes its default stat block to the modifier system; extras and flaws alter those defaults",
        "Invariant: every effect has exactly one type, one action, one range, one duration, and one cost per rank at any point in time",
        "Collaborates with: Modifier (extras/flaws change its properties and cost), Effect Cost (calculates its price), Power (groups one or more effects into a named capability)",
    ],
    "power": [
        "is the *player-facing named capability* that appears on a character sheet — the fiction label wrapping one or more effects",
        "acquires one or more effects, each paying its own cost; total power cost = sum of all effect costs",
        "carries at least one descriptor; the descriptor is not optional",
        "is approved by the GM before play; the GM may veto or modify powers for series appropriateness",
        "Invariant: every power must contain at least one effect and at least one descriptor",
        "Collaborates with: effect (its mechanical content), descriptor (its thematic identity), power point (its economic cost in Character Construction)",
    ],
    "power type": [
        "is the *category label* on every effect that governs which general rules apply",
        "classifies each effect into exactly one of six categories: Attack, Control, Defense, General, Movement, Sensory",
        "determines whether an effect requires an attack check, allows a resistance check, is activated as free action, or is permanent",
        "Invariant: every effect belongs to exactly one power type; a power type cannot be changed by modifiers",
        "Collaborates with: effect (carries the type label), modifier (extras can sometimes change apparent type behavior but not the official type)",
    ],
    "base cost": [
        "is the *unmodified power-point cost per rank* as printed in the rules for a specific effect",
        "is immutable — set at effect design time and cannot be changed by play or by modifiers",
        "seeds the modifier math: cost per rank = base cost + extras − flaws",
        "Invariant: base cost is always a positive integer ≥ 1 for every defined effect",
        "Collaborates with: effect (carries its base cost), modifier (extra and flaw adjust from this baseline), cost per rank (derived from this value)",
    ],
    "cost per rank": [
        "is the *final modified cost per rank* paid for each rank of an effect after modifier math is complete",
        "is computed as: base cost + (sum of per-rank extras) − (sum of per-rank flaws)",
        "drives the bulk of power cost: total effect cost = (cost per rank × ranks) + flat modifiers",
        "Invariant: cost per rank cannot drop below 1 pp/rank regardless of flaws applied",
        "Collaborates with: base cost (starting value), extra/flaw (modifiers applied), flat modifier (applied after the rank multiplication), rank (the multiplier)",
    ],
    "flat modifier": [
        "is a *fixed-point price adjustment* applied to the final total cost after the per-rank calculation",
        "adds (flat extra) or subtracts (flat flaw) a set number of points from the total, regardless of rank",
        "is applied last in the cost formula: (cost per rank × rank) + flat extras − flat flaws",
        "Invariant: flat modifiers cannot reduce total power cost below 1 power point",
        "Collaborates with: extra (flat extras add to total), flaw (flat flaws subtract from total), cost per rank (applied after this is multiplied by rank)",
    ],
    "extra": [
        "is a *modifier that enhances an effect* — it broadens, extends, or improves the effect beyond its defaults",
        "is either per-rank (adds to cost per rank) or flat (adds to the final total cost)",
        "must grant a genuine improvement; cosmetic changes are descriptors, not extras",
        "Invariant: an effect cannot receive an extra for a property it already has (e.g., cannot apply Ranged extra to an already-Ranged effect)",
        "Collaborates with: effect (is applied to an effect), base cost (raises it to produce cost per rank), flat modifier (for flat-value extras)",
    ],
    "flaw": [
        "is a *modifier that limits an effect* — it restricts, narrows, or conditions the effect below its defaults",
        "is either per-rank (reduces cost per rank) or flat (reduces the final total cost)",
        "must represent a genuine limitation reducing utility by approximately half or more; cosmetic restrictions are descriptors",
        "Invariant: flaws cannot reduce cost per rank below 1 pp/rank; total cost cannot drop below 1 pp",
        "Collaborates with: effect (is applied to an effect), base cost (reduces it to produce cost per rank), flat modifier (for flat-value flaws)",
    ],
    "Affliction": [
        "is an *Attack effect* that imposes progressively worsening conditions on a target who fails a resistance check",
        "requires an attack check before the target makes a resistance check (Fortitude or Will — chosen at acquisition)",
        "applies conditions based on degree of failure: first degree applies condition 1, second adds condition 2, third adds condition 3",
        "allows the target to make a resistance check at end of each of their turns; success removes one degree (from worst)",
        "enforces special recovery for third degree: full minute (or outside aid) after the Affliction ends",
        "Invariant: exactly three conditions must be specified at acquisition, in degree order; each must be progressively worse",
        "Collaborates with: resistance check (Fort or Will), condition (the output applied), attack check (prerequisite)",
    ],
    "Blast (Damage, Ranged)": [
        "is *Damage with the Ranged extra* — a preconfigured combination at 2 pp/rank, not a separate effect type",
        "requires a ranged attack check vs. target's Dodge defense; on a hit, target makes Toughness check vs. DC 15 + rank",
        "applies damage conditions on failed Toughness checks using the standard Damage degree-of-failure table",
        "Invariant: Blast costs exactly 2 pp/rank (base Damage 1 + Ranged extra 1); this is already factored in",
        "Collaborates with: Damage (its base effect), Ranged (the extra that creates Blast), Toughness (the resistance check), attack check",
    ],
    "Burrowing": [
        "is a *Movement effect* that grants the ability to move through earth, soil, clay, or rock",
        "calculates speed rank as Burrowing rank − 5; applies terrain penalties (clay −1, solid rock −2)",
        "lets the character choose on each use whether the tunnel is permanent or collapses behind them",
        "Invariant: Burrowing does not grant underwater breathing or any other survival capability",
        "Collaborates with: Movement (its type), speed rank (the output), terrain type (penalty input)",
    ],
    "Communication": [
        "is a *Sensory effect* that sends and receives information over distance via a chosen sense type medium",
        "determines range by effect rank on the distance table; operates as point-to-point by default",
        "requires a shared language between sender and receiver; language-dependent unless modified",
        "Invariant: Communication requires a chosen sense type medium at acquisition; this cannot be changed without GM approval",
        "Collaborates with: sense type (the medium), range (determined by rank), language (a prerequisite for exchange)",
    ],
    "Comprehend": [
        "is a *Sensory effect* that grants understanding of and ability to communicate with otherwise inaccessible beings or languages",
        "allocates each rank to exactly one communication type at acquisition: Animals, Languages, Machines, Objects, Plants, Spirits",
        "is permanent — always active, requires no action to invoke",
        "Invariant: each rank covers exactly one communication type; types do not stack within one rank",
        "Collaborates with: sense type (implicit), communication type (the chosen category per rank)",
    ],
    "Concealment": [
        "is a *Sensory effect* that makes the character undetectable to one specific sense type",
        "grants total concealment — characters relying on that sense cannot perceive the character at all",
        "costs 2 ranks per visual sense type; costs 1 rank for most other sense types",
        "is activated as a free action; must be sustained — lapses if concentration is broken",
        "Invariant: concealment from tactile (touch) sense is not possible",
        "Collaborates with: sense type (the sense being blocked), Senses (a target's sensing capability), attack check (attackers relying on concealed sense are effectively blind)",
    ],
    "Create": [
        "is a *Control effect* that forms solid physical objects with Toughness and volume derived from effect rank",
        "sets created object Toughness = effect rank; sets max volume from effect rank on volume table",
        "sustains the object — objects vanish when the effect is not maintained; character can spend PP = rank for permanence",
        "can trap, block, or restrain targets; restraining uses effect rank as effective Strength",
        "Invariant: created objects are solid and physical — they have Toughness and can be damaged and destroyed",
        "Collaborates with: rank (sets volume and Toughness), PP spending (for permanence), grab/restrain (combat application)",
    ],
    "Damage": [
        "is the *foundational Attack effect* for direct physical harm at close range",
        "sets resistance check DC = 15 + effect rank against target's Toughness",
        "applies damage conditions in four degrees: minor penalty → dazed and penalized → staggered and penalized → incapacitated",
        "stacks with character's Strength for unarmed attacks",
        "Invariant: Damage has Close range by default; it requires the Ranged extra to become Blast",
        "Collaborates with: Toughness (the resistance), DC (15 + rank), Strength (stacks for unarmed), damage condition (the output)",
    ],
    "Deflect": [
        "is a *Defense effect* that intercepts incoming ranged attacks for the user or nearby allies",
        "substitutes its rank (plus modifiers) for the normal active defense value of the protected target",
        "applies range penalties for medium and long range interceptions",
        "Invariant: Deflect intercepts attacks; it does not prevent the attack from being made — it substitutes the defense roll",
        "Collaborates with: active defense (Dodge/Parry — replaced by Deflect rank), range penalties (medium/long apply), attack check (what it is countering)",
    ],
    "Elongation": [
        "is a *General effect* that extends the character's body or limbs to reach distant targets",
        "sets reach = size rank + effect rank on the distance table",
        "grants +1 to grab check rolls per rank due to improved leverage",
        "Invariant: Elongation does not grant enhanced Strength, Toughness, or any other physical enhancement beyond reach",
        "Collaborates with: size rank (contributes to total reach), grab check (the combat application of reach)",
    ],
    "Enhanced Trait": [
        "is a *General effect* that temporarily raises an existing character trait above its base value",
        "requires the target trait to already exist on the character sheet; Enhanced Trait raises it further",
        "costs per rank equal to the target trait's own base cost per rank",
        "drops the enhanced trait back to base if the character cannot maintain it",
        "Invariant: Enhanced Trait is subject to PL limits on the resulting combined total",
        "Collaborates with: the enhanced trait (the target), PL limits (the cap), sustained duration (the maintenance requirement)",
    ],
    "Environment": [
        "is a *Control effect* that alters environmental conditions in a radius area",
        "offers selectable changes: Cold, Heat, Light, Visibility impairment, Movement impede",
        "determines radius from effect rank on the area table; additional environmental changes cost additional ranks",
        "Invariant: Environment does not directly damage targets — it creates hazardous or difficult conditions",
        "Collaborates with: effect rank (sets radius), environmental conditions (the changes made), movement speed (impede reduces it)",
    ],
    "Feature": [
        "is a *General effect* where each rank purchases one minor, permanently active game capability",
        "requires each Feature to have a concrete game-mechanical effect approved by the GM",
        "is distinct from descriptors — descriptors are free flavor; Features cost PP and provide real benefits",
        "Invariant: each rank equals exactly one Feature with exactly one minor game effect",
        "Collaborates with: GM approval (required for each Feature definition), descriptor (conceptually adjacent but mechanically distinct)",
    ],
    "Flight": [
        "is a *Movement effect* that grants the ability to fly at a speed rank equal to the effect rank",
        "provides hovering capability by default — the character can remain stationary in midair",
        "activates as a free action; moving while airborne requires a move action as normal",
        "is sustained — the character falls if they cannot maintain it",
        "Invariant: Flight does not grant additional protection from the fall if the effect ends mid-air",
        "Collaborates with: speed rank (the output), sustained duration (the maintenance requirement), move action (required for actual movement)",
    ],
    "Growth": [
        "is a *General effect* that increases the character's size rank, gaining physical power at the cost of defenses and concealment",
        "applies per-rank bonuses: +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth",
        "applies per-2-rank changes: −1 Dodge, −1 Parry, +1 Intimidation",
        "applies per-8-rank bonus: +1 Speed",
        "is sustained; returning to normal is a free action",
        "Invariant: Growth is sustained — if disrupted, the character immediately returns to normal size",
        "Collaborates with: size rank (the change driver), Strength/Stamina/Dodge/Parry/Stealth (the traits modified), sustained duration",
    ],
    "Healing": [
        "is a *General effect* that removes damage conditions from a willing target",
        "makes a check vs. DC 10; each degree of success removes one condition from most severe",
        "stabilizes a dying character as part of its effect",
        "cannot be used on the same target more than once per scene",
        "does not function on targets incapable of natural recovery (constructs, undead — unless modified)",
        "Invariant: Healing removes conditions in order from most severe to least; it cannot skip conditions",
        "Collaborates with: damage conditions (the output), stabilize (dying target special case), scene (the reuse boundary)",
    ],
    "Illusion": [
        "is a *Control effect* that creates false sensory impressions for targets in perception range",
        "costs 1–5 pp/rank depending on number of sense types covered; each additional sense type adds 1 pp/rank",
        "allows an Insight check (DC 10 + rank) to detect the illusion — success reveals falsehood but does not remove it",
        "has no physical substance — cannot block movement, cause damage, or provide cover",
        "is maintained and altered as a free action each turn",
        "Invariant: Illusions cannot cause actual harm or provide real physical barriers",
        "Collaborates with: sense type (the dimension of the illusion), Insight check (the detection mechanism), sustained duration",
    ],
    "Immortality": [
        "is a *Defense effect* that allows the character to return from death after a time period determined by rank",
        "calculates recovery time as time rank (19 − Immortality rank); at rank 20, recovers each action round",
        "does not prevent death — it only enables post-death return",
        "is permanent and always active; cannot be turned off",
        "Invariant: Immortality only triggers after death; it has no effect before death occurs",
        "Collaborates with: death (the trigger), time rank (the recovery schedule), permanent duration",
    ],
    "Immunity": [
        "is a *Defense effect* that grants automatic success on resistance checks against a specified effect set",
        "scales cost by scope: 1 rank for narrow immunity, up to 80 ranks for all Toughness effects",
        "provides complete protection against the covered set with no check required",
        "offers partial immunity (half effect) for half the full rank cost",
        "is permanent and always active; cannot be deactivated",
        "Invariant: Immunity works against the specified descriptor/effect set only; it has no effect outside that set",
        "Collaborates with: descriptor (the matching criterion), resistance check (bypassed), partial immunity (the half-cost variant)",
    ],
    "Insubstantial": [
        "is a *General effect* with 4 progressive forms representing decreasing physicality",
        "form 1 (Fluid): liquid-like; form 2 (Gaseous): gas-like; form 3 (Energy): energy-like; form 4 (Incorporeal): immaterial",
        "allows switching between available forms as a free action",
        "form 4 (Incorporeal) allows passing through solid matter and ignoring most physical effects",
        "is sustained; returning to normal is a free action",
        "Invariant: higher rank forms include all lower rank capabilities; you must purchase ranks in order",
        "Collaborates with: descriptor (defines the fiction of each form), sustained duration, Affects Insubstantial extra (for others to affect an Insubstantial character)",
    ],
    "Leaping": [
        "is a *Movement effect* that extends jumping distance to superhuman scales",
        "calculates jump distance rank = Leaping rank − 2 on the distance table",
        "prevents fall damage when landing within maximum jump distance",
        "follows a ballistic arc — the character cannot change direction mid-air",
        "Invariant: Leaping has Instant duration — it does not sustain; each jump is a discrete action",
        "Collaborates with: distance rank (the jump reach), Instant duration (discrete per-jump activation)",
    ],
    "Luck Control": [
        "is a *Control effect* that manipulates the hero point economy at perception range",
        "allocates each rank to one capability: spend a hero point on behalf of another, transfer a hero point, negate a hero point use, or force a re-roll",
        "is a Reaction — triggers in response to hero point use by another character",
        "Invariant: each rank of Luck Control provides exactly one capability from the defined list",
        "Collaborates with: hero point (the currency manipulated), perception range (the range requirement), Combat module (owns hero point mechanics)",
    ],
    "Mind Reading": [
        "is a *Sensory effect* that accesses target's thoughts via an opposed check",
        "initiates contact with an opposed check (effect rank vs. target Will); degree of success determines depth of access",
        "degree 1: surface thoughts; degree 2: personal thoughts; degree 3: memories; degree 4: subconscious",
        "allows target to make a Will check at end of each of their turns; success breaks contact",
        "is sustained; contact ends if concentration is broken",
        "Invariant: Mind Reading cannot directly harm the target — it extracts information only",
        "Collaborates with: Will (the resistance), perception range (the targeting requirement), sustained duration",
    ],
    "Move Object": [
        "is a *Control effect* that telekinetically lifts and moves objects or unwilling targets",
        "provides effective Strength = effect rank for all lifting and moving calculations",
        "cannot directly damage targets — force can be used for disarm, grab, or trip maneuvers only",
        "allows targets to resist with a Strength check vs. effect rank; objects do not resist",
        "is sustained — the held object or creature drops if concentration is broken",
        "Invariant: Move Object cannot deal Damage as a primary action; object-throwing damage is a secondary incidental",
        "Collaborates with: effective Strength (rank), grab/disarm/trip (the combat applications), Strength check (target resistance), sustained duration",
    ],
    "Movement": [
        "is a *Movement effect* that grants one special movement mode per rank from a defined list",
        "offers modes: Dimension Travel, Environmental Adaptation, Permeate, Safe Fall, Slithering, Space Travel, Sure-Footed, Swinging, Time Travel, Trackless, Wall-Crawling, Water-Walking",
        "activates as free action; requires a move action for actual movement (as all movement effects)",
        "is sustained; losing it ends the movement mode until reactivated",
        "Invariant: each rank grants exactly one mode; modes are independent — multiple modes require multiple ranks",
        "Collaborates with: movement mode (the specific capability acquired), sustained duration, GM (for Dimension/Time Travel interactions with setting)",
    ],
    "Nullify": [
        "is an *Attack effect* that suppresses other power effects matching a chosen descriptor",
        "requires a ranged attack check, then an opposed check: Nullify rank vs. target effect rank (or Will, whichever is higher)",
        "on success, the targeted effect is countered (turned off); the target can reactivate on their next action",
        "targets effects by descriptor; Broad and Simultaneous extras expand targeting scope",
        "Invariant: Nullify suppresses; it does not destroy or permanently remove effects",
        "Collaborates with: descriptor (the targeting criterion), ranged attack check, opposed check, Will (alternate resistance), sustained vs permanent effects (reactivation rules differ)",
    ],
    "Protection": [
        "is a *Defense effect* that adds directly to the character's Toughness defense",
        "provides +1 Toughness per rank; stacks with Stamina-derived Toughness and Impervious",
        "is permanent and always active — cannot be deactivated and cannot benefit from extra effort",
        "Invariant: Protection is always on; there is no version that can be turned off without a flaw",
        "Collaborates with: Toughness (the defense it enhances), Stamina (stacks with), Impervious extra (can be combined with)",
    ],
    "Quickness": [
        "is a *General effect* that accelerates completion of routine tasks",
        "reduces the time rank of routine tasks by 1 per rank; at high ranks, hours become minutes, minutes become seconds",
        "does not affect non-routine tasks (those requiring checks) or movement speed",
        "Invariant: Quickness only applies to routine tasks; any task requiring a roll is not affected",
        "Collaborates with: time rank (the reduction target), routine check (the scope of tasks affected)",
    ],
    "Regeneration": [
        "is a *Defense effect* that progressively removes damage conditions over time",
        "recovers in two phases: first removes Toughness penalties at rank per minute, then removes damage conditions at rank per minute from most severe",
        "is permanent and always active — cannot be deactivated",
        "Invariant: Regeneration cannot affect conditions that have not occurred naturally — it only repairs existing damage",
        "Collaborates with: damage conditions (the target of recovery), Toughness penalty (the first-phase target), permanent duration",
    ],
    "Remote Sensing": [
        "is a *Sensory effect* that displaces the character's senses to a remote location",
        "costs 1–5 pp/rank based on sense types covered (same scale as Illusion and Communication)",
        "suppresses normal senses while active — the character perceives only through the remote location",
        "marks the character as vulnerable (halved active defenses) while Remote Sensing is active",
        "Invariant: Remote Sensing suppresses normal senses; the character cannot perceive both locations simultaneously",
        "Collaborates with: sense type (the displaced senses), vulnerable condition (the cost of using it), range (determined by rank)",
    ],
    "Senses": [
        "is a *Sensory effect* that acts as the catch-all for any sensory enhancement not covered by a dedicated effect",
        "allocates each rank to one enhancement from a large menu of options",
        "is permanent — all purchased enhancements are always active",
        "covers enhancements including Accurate, Acute, Analytical, Awareness, Communication Link, Counters Concealment, Counters Illusion, Danger Sense, Darkvision, Detect, Direction Sense, Distance Sense, Extended, Infravision, Low-Light Vision, Microscopic Vision, Penetrates Concealment, Postcognition, Precognition, Radio, Radius, Ranged, Rapid, Time Sense, Tracking, Ultra-Hearing, Ultravision",
        "Invariant: each rank of Senses provides exactly one enhancement from the defined list",
        "Collaborates with: sense type (the sense being enhanced), permanent duration, Concealment (countered by Counters Concealment enhancement)",
    ],
    "Shrinking": [
        "is a *General effect* that decreases the character's size rank, improving defenses and stealth at cost of Strength and reach",
        "applies per-4-rank size category reduction",
        "applies per-rank bonuses: +1 Stealth; per-2-rank changes: +1 Dodge, +1 Parry, −1 Speed, −1 Intimidation",
        "reduces Strength for size-based purposes per size category reduction",
        "Invariant: Shrinking is sustained — returning to normal is a free action",
        "Collaborates with: size rank (the change driver), Dodge/Parry/Stealth/Speed (the traits modified), sustained duration",
    ],
    "Speed": [
        "is a *Movement effect* that increases ground movement speed",
        "sets ground speed rank = effect rank; improves all speed-based ground movement actions",
        "does not grant flight, aquatic movement, or any non-ground mode",
        "Invariant: Speed only enhances ground movement; each other movement mode requires its own effect",
        "Collaborates with: speed rank (the output), ground movement (the only context it improves), move action (required for actual movement)",
    ],
    "Summon": [
        "is a *Control effect* that calls an independently acting minion",
        "defines minion as having power points = effect rank × 15 and power level ≤ effect rank",
        "applies dazed condition to the minion on arrival (standard action only on first turn)",
        "directs the minion with a move action each turn; minion otherwise follows last instructions",
        "dismisses the minion if it is incapacitated; the summoner can re-summon later",
        "Invariant: minion PL cannot exceed the Summon effect rank; minion PP is fixed at rank × 15",
        "Collaborates with: effect rank (sets minion PP and PL cap), dazed condition (on arrival), move action (directing cost), incapacitated condition (dismissal trigger)",
    ],
    "Swimming": [
        "is a *Movement effect* that grants enhanced aquatic movement speed",
        "sets water speed rank = effect rank − 2 on the speed table",
        "makes routine Athletics (Swimming) checks automatic — no roll required",
        "does not grant underwater breathing capability",
        "Invariant: Swimming does not prevent suffocation underwater; Immunity (Suffocation) must be purchased separately",
        "Collaborates with: speed rank (the aquatic output), Athletics (Swimming) check (made automatic), Immunity (for breathing)",
    ],
    "Teleport": [
        "is a *Movement effect* that provides instantaneous point-to-point relocation",
        "requires the destination to be either well-known or accurately sensed; unperceived destinations risk teleport error",
        "preserves the character's velocity from before the teleport (momentum is conserved)",
        "carries mass rank 0 additional mass by default (Mass extra extends this)",
        "Invariant: Teleport is Instant — there is no transit, no passage through intervening space",
        "Collaborates with: perception (for destination targeting), mass rank (for carrying capacity), Instant duration",
    ],
    "Transform": [
        "is a *Control effect* that changes one type of object into another type at close range",
        "scales cost by scope: 2 pp/rank (narrow: one substance to one), up to 5 pp/rank (broad: anything to anything)",
        "determines transformable mass from effect rank on the mass table (rank − 6)",
        "allows inanimate objects to be transformed without resistance; living targets make Fortitude checks",
        "is sustained — transformation reverts when the effect ends unless the Continuous extra is applied",
        "Invariant: Transform requires a defined target type and result type at acquisition (or defined scope for broad transforms)",
        "Collaborates with: effect rank (sets mass limit), Fortitude (living target resistance), sustained duration (reversibility), Continuous extra (permanence)",
    ],
    "Variable": [
        "is a *General effect* that provides a pool of power points the character can allocate to any effects of a defined type or descriptor",
        "sets pool size = effect rank × 5 power points; any effects of the defined type can be built from this pool",
        "reallocates the pool as a standard action; all effects built from the pool are subject to PL limits",
        "resets the pool if the effect is not maintained (all active allocated effects end)",
        "Invariant: the pool size is exactly rank × 5; Variable-built effects cannot exceed PL limits",
        "Collaborates with: effect rank (sets pool size), PP pool (the allocatable resource), PL limits (the constraint on built effects), sustained duration",
    ],
    "Weaken": [
        "is an *Attack effect* that temporarily reduces a specific trait of the target",
        "applies reduction equal to degree of failure on the resistance check, up to the Weaken rank maximum",
        "is cumulative — multiple Weaken applications on the same trait stack up to the rank maximum",
        "allows targets to recover at 1 point of the reduced trait per round (automatic, no action)",
        "Invariant: Weaken is cumulative to rank maximum; beyond rank maximum, additional Weaken has no further effect",
        "Collaborates with: resistance check (Fort or Will), degree of failure (determines reduction amount), target trait (chosen at acquisition), recovery (1 per round automatic)",
    ],
    "Accurate": [
        "is a *flat extra* that adds +2 per rank to attack checks made with the specific effect",
        "costs 1 flat point per rank of accuracy bonus (i.e., 1 pp for +2, 2 pp for +4, etc.)",
        "applies only to the specific effect it is purchased for",
        "Invariant: the attack bonus from Accurate cannot push total attack bonus beyond PL × 2",
        "Collaborates with: attack check (the thing improved), PL limits (the cap), flat modifier (the cost mechanism)",
    ],
    "Area": [
        "is a *per-rank extra* that removes the attack check requirement and instead affects all targets in a defined area",
        "allows targets a Dodge resistance check (DC 10 + effect rank) to avoid the effect (success = half rank effect)",
        "offers shapes: Burst, Cloud, Cone, Cylinder, Line, Perception, Shapeable",
        "costs +1 per rank; each additional rank of Area increases the area dimensions",
        "Invariant: Area effects cannot exclude specific targets within the area without the Selective extra",
        "Collaborates with: Dodge (the resistance check), area shape (the dimension of coverage), effect rank (sets DC and area size), Selective extra (for target exclusion)",
    ],
    "Multiattack": [
        "is a *per-rank extra* that allows an effect to hit multiple targets or strike a single target multiple times",
        "against a single target: +2 to effect DC at 2 degrees of attack success; +5 at 3+ degrees",
        "against multiple targets: one attack roll with penalty equal to number of targets; each target whose Dodge is exceeded is hit",
        "costs +1 per rank",
        "Invariant: Multiattack has two distinct modes (single-target boost vs. multi-target spray); the character chooses each time they use the effect",
        "Collaborates with: attack check (the roll used for both modes), Dodge (the defense of each target in spray mode), DC (increased in single-target mode)",
    ],
    "Penetrating": [
        "is a *flat extra* that allows an effect to bypass Impervious resistance",
        "costs 1 flat point per rank of Penetrating; overcomes Impervious to degree equal to Penetrating rank",
        "forces targets with Impervious Toughness to resist damage rank equal to the Penetrating rank",
        "Invariant: Penetrating only bypasses Impervious; it does not increase the attack's DC or rank",
        "Collaborates with: Impervious extra (what it bypasses), Toughness (the resistance still applied), flat modifier (the cost mechanism)",
    ],
    "Activation": [
        "is a *flat flaw* that requires the character to spend an action activating the power before any effects become available",
        "costs −1 (move action) or −2 (standard action) from the power's total cost",
        "applies to the entire power — all effects within the power require the activation",
        "requires reactivation after being Nullified or deactivated",
        "Invariant: Activation applies to the whole power, not individual effects within it",
        "Collaborates with: flat modifier (the cost mechanism), Nullify (the deactivation trigger), the entire power (all effects affected)",
    ],
    "Check Required": [
        "is a *flat flaw* that requires a successful skill or ability check before the effect activates",
        "costs −1 per rank of the effect",
        "sets check DC = 10 + extra ranks beyond base; natural 1 always fails",
        "grants 1 effective rank per point exceeding the DC on a success",
        "Invariant: Check Required is in addition to any other checks the effect normally requires (attack checks, resistance checks)",
        "Collaborates with: skill check (the gate), DC (10 + extra ranks), flat modifier (the cost mechanism), effect rank (increased by exceeding DC)",
    ],
    "Limited": [
        "is a *per-rank flaw* that restricts an effect to function only under certain circumstances, against certain targets, or in certain conditions",
        "costs −1 per rank",
        "requires the limitation to genuinely reduce utility to approximately half or less; GM determines qualification",
        "is distinct from complications — complications trigger narrative events with hero point rewards; Limited reduces mechanical cost",
        "Invariant: Limited must be a genuine mechanical restriction, not a cosmetic or flavor restriction",
        "Collaborates with: per-rank flaw (the cost mechanism), GM approval (required to qualify), circumstance (the limiting condition)",
    ],
    "Removable": [
        "is a *flat flaw* that represents a power built into an item that can be physically taken from the character",
        "costs −1 per 5 points of final power cost (or −2 if easily removable)",
        "allows the item to be taken when the character is both stunned and defenseless, or via a disarm/grab",
        "applies to the entire power — all effects are unavailable if the item is taken",
        "allows the item itself to be damaged using object damage rules; Toughness = character's PL",
        "Invariant: Removable applies to the whole power, not individual effects",
        "Collaborates with: flat modifier (the cost mechanism), stunned+defenseless conditions (the vulnerability window), item Toughness (= PL), object damage rules",
    ],
    "descriptor": [
        "is a free *thematic label* on a power that connects it to the game fiction and mechanical interaction systems",
        "costs no power points — it is purely a label attached at acquisition",
        "governs what Nullify can counter and what Immunity can block",
        "supports GM rulings on descriptor interactions in play",
        "Invariant: every power must have at least one descriptor; descriptors may not be changed without GM approval",
        "Collaborates with: Nullify (uses descriptor to target), Immunity (uses descriptor to define coverage), GM (final arbitrator of descriptor interactions)",
    ],
    "origin descriptor": [
        "is a *descriptor subtype* that identifies how the character came to have their powers",
        "covers categories: Accidental, Bestowed, Invented, Mutant, Training",
        "typically applies to the character's entire power set rather than individual powers",
        "Invariant: origin descriptor rarely has direct mechanical effects; it is primarily a narrative and GM-ruling tool",
        "Collaborates with: descriptor (its parent concept), power set (the scope it typically covers)",
    ],
    "source descriptor": [
        "is a *descriptor subtype* that identifies the energy or force a power draws upon",
        "covers categories: Biological, Cosmic, Divine, Extradimensional, Magical, Moral, Psionic, Technological",
        "has direct mechanical significance — Nullify targeting 'magical effects' counters all powers with Magical source",
        "a power can have multiple source descriptors if it draws on more than one source",
        "Invariant: source descriptor determines Nullify and Immunity interactions more directly than origin descriptor",
        "Collaborates with: descriptor (its parent concept), Nullify (the primary mechanical consumer), Immunity (the secondary mechanical consumer)",
    ],
    "Array": [
        "is the *container concept* for a collection of Alternate Effects that share a cost pool under mutual exclusivity",
        "enforces the rule: only one effect in the Array can be active at a time (for non-Dynamic effects)",
        "propagates disable state: if any effect in the Array is Nullified or disabled, all are equally affected",
        "allows switching between effects as a free action once per turn",
        "Invariant: an Array requires at least one base effect and at least one Alternate Effect to be meaningful",
        "Collaborates with: Alternate Effect (the variants it contains), Dynamic Alternate Effect (the simultaneous variant), Nullify (the propagation trigger), free action (the switch mechanism)",
    ],
    "Alternate Effect": [
        "is a *variant effect in an Array* that can substitute for the primary effect at flat cost",
        "costs 1 flat point per Alternate Effect added",
        "must have a total cost (not just rank) ≤ the primary effect's total cost",
        "cannot be a permanent effect (permanent effects cannot be switched in/out)",
        "Invariant: only one Alternate Effect (or the primary) can be active at a time",
        "Collaborates with: Array (the container), flat modifier (the cost mechanism), primary effect (the cost ceiling), mutual exclusivity rule",
    ],
    "Dynamic Alternate Effect": [
        "is a *variant of Alternate Effect* that can share power points with other Dynamic effects and operate simultaneously",
        "costs 2 flat points per Dynamic Alternate (the base effect costs 1 extra point to become dynamic)",
        "allows the character to reallocate points among Dynamic effects once per turn as a free action",
        "operates at reduced effectiveness when sharing — combined point allocation cannot exceed the Array pool",
        "Invariant: Dynamic effects can operate simultaneously; standard Alternate Effects cannot",
        "Collaborates with: Array (the container), power points (the shared resource), free action (the reallocation mechanism), pool size (the upper limit)",
    ],
}

def add_domain_sketch_to_term(content: str, term_name: str, bullets: list) -> str:
    """Add #### Domain Sketch after the #### Domain Language section of a term."""
    # Find the #### term heading
    term_pattern = f"#### {re.escape(term_name)}\n"
    idx = content.find(term_pattern)
    if idx == -1:
        print(f"  WARN: term not found: {term_name}")
        return content
    
    # Find the next #### heading after this term (to bound the search)
    next_h4 = content.find("\n#### ", idx + len(term_pattern))
    next_h3 = content.find("\n### ", idx + len(term_pattern))
    next_h2 = content.find("\n## ", idx + len(term_pattern))
    
    # Find end of term block
    candidates = [x for x in [next_h4, next_h3, next_h2] if x != -1]
    block_end = min(candidates) if candidates else len(content)
    
    term_block = content[idx:block_end]
    
    # Check if Domain Sketch already added
    if "#### Domain Sketch" in term_block:
        return content  # Already added
    
    # Find where to insert: after "#### Domain Language" block, before "#### References" or "#### Decisions made"
    # Look for #### References or #### Decisions made within the term block
    ref_pos = term_block.find("\n#### References")
    dec_pos = term_block.find("\n#### Decisions made")
    
    if ref_pos != -1 and (dec_pos == -1 or ref_pos < dec_pos):
        insert_before = ref_pos
    elif dec_pos != -1:
        insert_before = dec_pos
    else:
        # Insert at end of term block
        insert_before = len(term_block)
    
    # Build domain sketch section
    sketch_lines = "\n\n#### Domain Sketch\n\n"
    sketch_lines += "\n".join(f"- {b}" for b in bullets)
    sketch_lines += "\n"
    
    # Insert into term block
    new_term_block = term_block[:insert_before] + sketch_lines + term_block[insert_before:]
    
    return content[:idx] + new_term_block + content[block_end:]


def main():
    path = r"c:\dev\mm3e-online-holistic\docs\power\power.md"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for term_name, bullets in SKETCH_DATA.items():
        content = add_domain_sketch_to_term(content, term_name, bullets)
        print(f"  Added domain sketch for: {term_name}")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\nDone. Updated {path}")


if __name__ == "__main__":
    main()
