# Story Map — Character Construction Module

Pass 2 (Level 2 — Increment Discovery) scoped to the **(E) Construct Hero** epic from the MM3E holistic story map.
Actors: **Player** (human building a hero), **GM** (Gamemaster), **System** (rules engine / application).

---

(E) Construct Hero
    (E) Allocate Resources
        (S) GM --> Set Series Power Level
        (S) System --> Derive Starting Power Points from Power Level
        (S) Player --> Spend Power Points on Ability Ranks
        (S) Player --> Spend Power Points on Defense Ranks
        (S) Player --> Spend Power Points on Skill Ranks
        (S) Player --> Spend Power Points on Advantages
        (S) Player --> Spend Power Points on Powers
        (S) System --> Validate Power Points Total Balance
    (E) Enforce Power Level Limits
        (S) System --> Enforce Attack and Effect Cap
        (S) System --> Enforce Dodge and Toughness Cap
        (S) System --> Enforce Parry and Toughness Cap
        (S) System --> Enforce Fortitude and Will Cap
        (S) System --> Enforce Skill Modifier Cap
        (S) Player --> Apply Trade-Off within Limit Pair
    (E) Define Hero Identity
        (S) Player --> Develop Hero Concept
        opt (S) Player --> Select Hero Archetype as Starting Point
        (S) Player --> Choose Hero Origin
        (S) Player --> Record Hero Background Details
        (S) Player --> Design Hero Costume
    (E) Choose Complications
        (S) Player --> Choose Motivation Complication
        (S) Player --> Choose Complication
        (S) Player --> Specify Weakness Trigger and Effect with GM
        (S) System --> Validate Minimum Complication Requirement
        (S) Player --> Evolve Complication over Series
    (E) Approve and Finalize Hero
        (S) GM --> Review Hero Power Points Allocation
        (S) GM --> Verify Hero Follows Power Level Guidelines
        (S) GM --> Approve Completed Hero for Play

    (E) Advance Hero
        (S) GM --> Award Power Points after Adventure
        (S) Player --> Spend Earned Power Points on Traits
        (S) System --> Enforce Power Level Limits on Earned Spending
        (S) GM --> Raise Series Power Level
        (S) Player --> Reallocate Power Points via Transformation

---

## Consolidation Notes (for AC phase)

### Spend Power Points on X Ranks (Ability, Defense, Skill, Advantages, Powers)
Groups five distinct trait-category spend stories. Each uses the same "allocate PP at stated cost" pattern but has a different cost formula and different rules.
AC must specify per variant:
- Ability Ranks: 2 PP per ability rank; 8 ability scores (STR, STA, AGL, DEX, FGT, INT, AWE, PRE)
- Defense Ranks: 1 PP per rank above the base value provided by the related ability
- Skill Ranks: 1 PP per 2 total skill ranks (rounded down for odd totals)
- Advantages: 1 PP per advantage or per rank in a ranked advantage
- Powers: ((base effect cost + extras minus flaws) x rank) + flat modifiers; cost varies by chosen effect

### Choose Complication
Consolidates enemy, identity, responsibility, relationship, secret, power loss, and any other non-Motivation, non-Weakness complication type. All share the construction-time pattern: Player chooses type, defines narrative detail, GM may overrule.
AC must specify per variant:
- Enemy: define adversary identity and nature of enmity (one-sided or mutual); GM introduces enemy in play when it causes specific harm to earn hero point
- Identity: choose public identity (reveal real name, live in public eye) or secret identity (maintain dual life, protect loved ones from knowledge); dual-identity heroes must track two personas
- Responsibility: define obligations (family, professional, civic) that compete with heroic duties; earning hero point requires responsibility to be visibly neglected or conflicted
- Relationship: define key people in hero's life (loved ones, mentors, rivals); if in the know about hero identity, they are danger targets; if not, hero must manage the dual life
- Secret: specify what is hidden and from whom (true identity, dark past, secret weakness); earning hero point requires active threat of exposure
- Power Loss: define triggering circumstances (specific substance, condition, location, or wavering motivation); earning hero point requires powers to actually fail due to trigger

### Enforce Power Level Limits (Attack & Effect, Dodge & Toughness, Parry & Toughness, Fortitude & Will)
Groups four PL cap pairs that share the same rule shape: sum of both traits in pair must not exceed 2 x series power level. Each pair governs different traits.
AC must specify per pair:
- Attack & Effect: attack bonus + effect rank of that attack <= 2xPL; if effect allows resistance check but no attack check, effect rank alone <= PL
- Dodge & Toughness: Dodge + Toughness <= 2xPL; Dodge is active defense (purchased), Toughness is passive
- Parry & Toughness: Parry + Toughness <= 2xPL; Parry is close-combat active defense; Toughness shared with Dodge pair
- Fortitude & Will: Fortitude + Will <= 2xPL; both are resistance defenses, not active defenses

### Raise Series Power Level
Consolidates the two outcomes of a PL increase: heroes gain cap headroom to spend PP on previously-maxed traits; GM reevaluates NPC challenge ratings.
AC must specify:
- Trigger: heroes have accumulated approximately 15 additional PP since series start or last PL increase
- Effect on heroes: PL raises by +1; heroes may now spend accumulated PP on traits that exceeded the old cap
- Effect on NPCs: GM reviews villain traits and may increase some to maintain challenge; no PP accounting required for NPCs

---

## Context Gaps

- Complication activation during play (GM introduces complication, player goes along, earns hero point) is a runtime behavior owned by the Check Resolution module — not represented in this construction map.
- Online tool persistence and versioning of hero sheets is outside the source scope; no stories mapped.
- Team/party construction coordination (ensuring heroes complement each other) is addressed informally in source ("consult fellow players") with no formal construction steps — not mapped.
- Quickstart Character Generator (page 54 reference) is mentioned in source as an alternative to full hero design; scope and mechanic not described in available chunks — flagged as context gap.
