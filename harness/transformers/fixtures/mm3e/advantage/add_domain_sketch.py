"""
Add Domain Sketch sections to advantage.md.
Rules:
- #### term sections: flush before next ####/###/##/--- boundary
- ## boundary sections: flush only before next ## or end-of-file (#### content headings don't flush)
- Never flush inside a source block
"""
import re

DOMAIN_SKETCHES = {
    "advantage": (
        "#### Domain Sketch\n"
        "Advantage is the foundational purchasable capability unit — the named ability a hero buys with power points to exceed ordinary character limits.\n"
        "\n"
        "- accepts cost of exactly 1 power point per rank during character creation or advancement\n"
        "- belongs to exactly one of the four categories (Combat, Fortune, General, Skill) fixed at definition time\n"
        "- allows the holder to do something most characters cannot do, or to do something ordinary significantly better\n"
        "- scales through rank when the advantage is Ranked; a non-ranked advantage is acquired once at effective rank 1\n"
        "- publishes its benefit description and whether additional ranks are available\n"
        "\n"
        "Invariant: cost is always exactly 1 power point per rank; a non-ranked advantage is always at effective rank 1; "
        "category membership is fixed and always exactly one of the four categories; "
        "the benefit must never grant an effect equivalent to a power costing more than 1 point.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- advantage and advantage rank are kept as two separate terms because rank governs a distinct set of rules (notation, caps, scaling) described independently from what an advantage is.\n"
        "- Specific named advantages (Accurate Attack, Luck, etc.) are instances of advantage, not separate top-level concepts.\n"
    ),
    "advantage rank": (
        "#### Domain Sketch\n"
        "Advantage rank is the scalar multiplier that makes a Ranked advantage stronger with each additional purchase.\n"
        "\n"
        "- records itself as a number after the advantage name (e.g., \"Defensive Roll 2\" for two ranks)\n"
        "- scales the advantage's effect upward with each rank purchased\n"
        "- enforces a published maximum rank when the advantage heading specifies one (e.g., \"Ranked (2)\")\n"
        "- prevents purchase of additional ranks beyond the stated maximum\n"
        "- for non-ranked advantages, holds fixed at effective rank 1 and cannot increase\n"
        "\n"
        "Invariant: rank cannot exceed the maximum stated in the advantage's heading when a cap is listed; a non-ranked advantage is always rank 1.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Kept as a property under the Advantage KA rather than a standalone concept: rank has no identity or behavior outside the advantage it belongs to.\n"
    ),
    "combat advantage": (
        "#### Domain Sketch\n"
        "Combat advantage is the category label that groups advantages whose primary effect modifies combat maneuver terms, attack checks, defenses, or critical threat ranges.\n"
        "\n"
        "- classifies each member advantage as affecting combat — establishing the domain boundary for this category\n"
        "- modifies maneuver terms (attack bonus, active defenses, effect modifier, critical range) rather than skill use or hero point spending\n"
        "- combines with other combat advantages at the character level to form coherent fighting styles (e.g., martial arts disciplines)\n"
        "\n"
        "Invariant: a combat advantage always modifies a combat maneuver mechanic; it never requires a hero point to activate.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Favored Environment is classified here (COMBAT), not under Skill Advantage, matching the source's explicit category label.\n"
        "- Improved Initiative is classified here despite primarily affecting turn order — the source explicitly labels it COMBAT.\n"
    ),
    "fortune advantage": (
        "#### Domain Sketch\n"
        "Fortune advantage is the category label for advantages whose activation consumes a hero point, translating luck, inspiration, and leadership into mechanical effects.\n"
        "\n"
        "- classifies each member advantage as requiring a hero point spend to activate its effect\n"
        "- defines the specific outcome that the hero point purchase achieves (re-roll, group bonus, condition removal, or temporary skill ranks)\n"
        "- Luck is an exception: it functions like a hero point re-roll but draws from a separate per-session pool rather than consuming an actual hero point\n"
        "\n"
        "Invariant: each fortune advantage defines a hero-point-activated effect; hero point benefits in this category ignore power level limits.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Luck is classified here despite not spending a hero point at use time: the re-roll mechanic is identical to a hero point re-roll and the source labels it FORTUNE.\n"
        "- Beginner's Luck is classified here (FORTUNE) per the source's explicit label, even though its effect grants temporary skill ranks.\n"
    ),
    "general advantage": (
        "#### Domain Sketch\n"
        "General advantage is the residual category for advantages that provide passive bonuses, immunity-like effects, or access to additional character resources — anything not covered by Combat, Fortune, or Skill.\n"
        "\n"
        "- classifies each member advantage as falling outside the three more specific categories\n"
        "- grants passive bonuses (e.g., Great Endurance), immunity effects (e.g., Fearless), resource access (Equipment, Minion, Sidekick), or narrative perquisites (Benefit)\n"
        "- takes effect passively, at character creation, or through explicit character management — never through combat maneuver declaration or hero point spending\n"
        "\n"
        "Invariant: a general advantage never requires a combat maneuver declaration or a hero point expenditure to take effect.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Equipment, Minion, and Sidekick are modeled as distinct terms because each governs a distinct resource with its own point budget, scaling formula, and replacement or improvement rules.\n"
    ),
    "skill advantage": (
        "#### Domain Sketch\n"
        "Skill advantage is the category label for advantages that modify the conditions, scope, or quality of skill use — broadening what skills can do, removing restrictions, or granting situational circumstance bonuses.\n"
        "\n"
        "- classifies each member advantage as affecting skill use rather than combat maneuvers, hero points, or general character resources\n"
        "- removes training requirements (Jack-of-all-trades), enables pressure-free routine checks (Skill Mastery), or grants circumstance bonuses against specific targets (Favored Foe)\n"
        "- applies its effect through the skill system — not by modifying attack checks directly or activating through hero point spending\n"
        "\n"
        "Invariant: a skill advantage always affects the application of skill rules and does not directly modify attack check mechanics or activate through hero point spending.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Favored Foe is placed here (Skill Advantage) rather than Combat Enhancement because its bonus applies to four social and perception skill checks; the source classifies it SKILL.\n"
    ),
    "Accurate Attack": (
        "#### Domain Sketch\n"
        "Accurate Attack enables a symmetric trade-off between effect potency and attack accuracy during an accurate attack maneuver.\n"
        "\n"
        "- declares a penalty of up to −5 on the effect modifier before the attack roll is made\n"
        "- applies the same value as a bonus to the attack check for that attack (up to +5)\n"
        "- enforces that penalty and bonus are equal in magnitude and neither exceeds 5\n"
        "- resolves only during an accurate attack maneuver — declaration must happen before the attack roll\n"
        "\n"
        "Invariant: penalty taken must equal bonus gained; neither the penalty nor the bonus may exceed 5; declaration must precede the attack roll.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Grouped with All-out Attack, Defensive Attack, and Power Attack under Attack Trade-off: all four implement the identical symmetric exchange pattern (−N to one stat, +N to another, max 5).\n"
    ),
    "All-out Attack": (
        "#### Domain Sketch\n"
        "All-out Attack enables a symmetric trade-off between defensive capability and attack accuracy during an all-out attack maneuver.\n"
        "\n"
        "- declares a penalty of up to −5 on both active defenses (Dodge and Parry) before the attack roll\n"
        "- applies the same value as a bonus to the attack check for that attack (up to +5)\n"
        "- enforces that penalty and bonus are equal in magnitude and neither exceeds 5\n"
        "- resolves only during an all-out attack maneuver — declaration must happen before the attack roll\n"
        "\n"
        "Invariant: penalty and bonus are equal; neither exceeds 5; both Dodge and Parry take the full penalty together; declaration precedes the attack roll.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Distinct from Defensive Attack (inverse direction: defenses → accuracy) and from Power Attack (trades accuracy for effect, not defense for accuracy).\n"
    ),
    "Defensive Attack": (
        "#### Domain Sketch\n"
        "Defensive Attack enables a symmetric trade-off between attack accuracy and defensive capability during a defensive attack maneuver.\n"
        "\n"
        "- declares a penalty of up to −5 on the attack check before the roll\n"
        "- applies the same value as a bonus to both active defenses (Dodge and Parry) for the round (up to +5)\n"
        "- enforces that penalty and bonus are equal in magnitude and neither exceeds 5\n"
        "- resolves only during a defensive attack maneuver — declaration must happen before the attack roll\n"
        "\n"
        "Invariant: penalty must equal bonus; neither exceeds 5; both Dodge and Parry receive the full bonus as a pair; declaration precedes the attack roll.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Defensive Attack is the inverse of All-out Attack: direction of trade reversed (accuracy → defenses vs. defenses → accuracy); mechanic otherwise structurally identical.\n"
    ),
    "Power Attack": (
        "#### Domain Sketch\n"
        "Power Attack enables a symmetric trade-off between attack accuracy and effect potency during a power attack maneuver.\n"
        "\n"
        "- declares a penalty of up to −5 on the attack check before the roll\n"
        "- applies the same value as a bonus to the effect modifier of the attack (up to +5)\n"
        "- enforces that penalty and bonus are equal in magnitude and neither exceeds 5\n"
        "- resolves only during a power attack maneuver — declaration must happen before the attack roll\n"
        "\n"
        "Invariant: penalty must equal bonus; neither exceeds 5; declaration precedes the attack roll.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Power Attack is the inverse of Accurate Attack: Accurate Attack trades effect for accuracy; Power Attack trades accuracy for effect. Both operate on the same stat pair in opposite directions.\n"
    ),
    "Improved Initiative": (
        "#### Domain Sketch\n"
        "Improved Initiative passively raises the character's position in the initiative order by boosting their initiative check result.\n"
        "\n"
        "- adds +4 per rank to every initiative check without requiring any activation or declaration\n"
        "- stacks cumulatively: Improved Initiative 2 grants +8, rank 3 grants +12, and so on\n"
        "- applies automatically to every initiative check for as long as the advantage is held\n"
        "\n"
        "Invariant: bonus is exactly +4 per rank and applies to all initiative checks without exception; no per-round declaration is needed.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Modeled as a passive bonus (no player action required): the source describes it as a flat bonus, not a situational option.\n"
    ),
    "Improved Critical": (
        "#### Domain Sketch\n"
        "Improved Critical passively extends the range of die rolls that qualify as critical threats for a specified attack type.\n"
        "\n"
        "- records the specified attack type at acquisition time — the advantage is bound to that attack type\n"
        "- extends the critical threat range by 1 per rank: base natural 20; rank 1 = 19–20; rank 4 = 16–20 (maximum)\n"
        "- validates that a roll in the threat range that misses is not treated as a critical hit\n"
        "- applies automatically to every attack of the specified type — no per-attack declaration required\n"
        "\n"
        "Invariant: maximum threat range is 16–20 (4 ranks); only natural 20 is an automatic hit; "
        "an attack that misses is never a critical hit even within the threat range; advantage is bound to one specified attack type per rank.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Each rank can expand the same attack's range or bind to a different attack type — the system must store which attacks have extended ranges and by how much.\n"
    ),
    "Ranged Attack": (
        "#### Domain Sketch\n"
        "Ranged Attack passively raises the character's bonus on all ranged attack checks, making them broadly effective across ranged attack types.\n"
        "\n"
        "- adds +1 per rank to all ranged attack checks without targeting a specific attack type\n"
        "- applies passively to every ranged attack — no declaration or activation required\n"
        "- remains subject to the series power level cap on total attack bonus\n"
        "\n"
        "Invariant: total attack bonus including Ranged Attack is always subject to power level cap; bonus applies to all ranged attacks without exception.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Distinguished from the Ranged Combat skill: Ranged Attack is a broad bonus across all ranged attacks; Ranged Combat skill is for one specific attack type. Both can coexist.\n"
    ),
    "Close Attack": (
        "#### Domain Sketch\n"
        "Close Attack passively raises the character's bonus on all close attack checks — armed and unarmed — making them broadly effective in melee.\n"
        "\n"
        "- adds +1 per rank to all close attack checks (armed and unarmed) without targeting a specific attack type\n"
        "- applies passively to every close attack — no declaration or activation required\n"
        "- remains subject to the series power level cap on total attack bonus\n"
        "\n"
        "Invariant: total attack bonus including Close Attack is always subject to power level cap; bonus applies to all close attacks without exception.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Distinguished from the Close Combat skill: Close Attack is a broad bonus across all close attacks; Close Combat skill is for one specific attack type. Both can coexist.\n"
    ),
    "Favored Environment": (
        "#### Domain Sketch\n"
        "Favored Environment grants a situational +2 circumstance bonus to attack or defense when the character is operating in their designated environment.\n"
        "\n"
        "- recognizes when the character is in their favored environment (air, underwater, space, extreme heat, jungle, etc.)\n"
        "- requires the character to choose at the start of each round whether the +2 applies to attack checks or to both active defenses\n"
        "- holds the chosen allocation fixed until the start of the character's next round\n"
        "- applies passively while in the environment — no action required beyond the round-start allocation choice\n"
        "\n"
        "Invariant: the +2 bonus is not affected by power level limits; the allocation choice must be made at round start and applies for the full round; "
        "the advantage has no effect outside the designated environment.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Whether the system auto-detects the environment or requires a player declaration is an open context gap noted in the story map.\n"
        "- Classified under Combat Advantage (not Skill Advantage) per the source's explicit COMBAT category label.\n"
    ),
    "Luck": (
        "#### Domain Sketch\n"
        "Luck provides a per-session pool of re-roll uses that function identically to hero point re-rolls but draw from a separate, rank-limited resource.\n"
        "\n"
        "- tracks remaining uses for the session; each use consumes one rank from the pool (not a hero point)\n"
        "- re-rolls one die roll once per round, adding 10 to any re-roll result of 10 or less — same mechanic as a hero point re-roll\n"
        "- limits session uses to the character's current Luck rank — when the pool is empty, Luck cannot be used\n"
        "- refreshes the full pool when hero points reset at the start of a new adventure\n"
        "\n"
        "Invariant: maximum rank is half the series power level rounded down; cannot exceed once per round; "
        "pool is empty after rank uses that session; pool refreshes only at adventure start.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Classified under Fortune Advantage despite not spending a hero point at use time: the re-roll mechanic is identical to a hero point re-roll and the source labels it FORTUNE.\n"
        "- Luck's rank cap at half PL is the only power-level-derived rank cap in this module; character construction validation must enforce it.\n"
    ),
    "Inspire": (
        "#### Domain Sketch\n"
        "Inspire translates a hero point and a moment of leadership into a temporary group-wide bonus that benefits all interacting allies.\n"
        "\n"
        "- requires spending a hero point and taking a standard action to activate\n"
        "- grants +1 per Inspire rank on all checks to all allies who can interact with the activating character, until start of that character's next round\n"
        "- excludes the activating character — only allies receive the bonus\n"
        "- enforces a maximum bonus of +5 (Inspire rank is capped at 5)\n"
        "\n"
        "Invariant: bonus ignores power level limits; the activating character does not receive the bonus; "
        "multiple Inspire activations do not stack — only the highest applies; bonus expires at the start of the activating character's next round.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- \"Allies who can interact\" means within normal interaction range — the system determines who qualifies at activation time.\n"
    ),
    "Leadership": (
        "#### Domain Sketch\n"
        "Leadership translates a hero point and a moment of commanding presence into removal of a debilitating condition from one ally.\n"
        "\n"
        "- requires spending a hero point and taking a standard action to activate\n"
        "- selects one ally within interaction range as the target\n"
        "- removes exactly one of three eligible conditions from that ally: dazed, fatigued, or stunned\n"
        "\n"
        "Invariant: only the three eligible conditions (dazed, fatigued, stunned) can be removed; "
        "the ally must be within interaction range; exactly one condition is removed per activation; no other conditions are eligible.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Leadership requires no roll — spending the hero point and taking the standard action removes the condition immediately, per the source text.\n"
    ),
    "Beginner's Luck": (
        "#### Domain Sketch\n"
        "Beginner's Luck converts a hero point into a burst of luck-based proficiency, granting effective skill ranks for one scene.\n"
        "\n"
        "- requires spending a hero point to activate; no additional action cost beyond the hero point spend\n"
        "- selects one skill the character currently has at 4 or fewer ranks (including skills with 0 ranks and normally untrained-restricted skills)\n"
        "- grants effective rank 5 in that skill for the duration of the current scene\n"
        "- expires at the end of the scene — temporary ranks do not carry over\n"
        "\n"
        "Invariant: applies only to skills currently at 4 or fewer ranks; grants exactly effective rank 5 (not +5 to existing rank); "
        "lasts exactly for the scene; expires when the scene ends.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Classified under Fortune Advantage (FORTUNE) per the source's explicit label, not Skill Advantage, despite the effect granting temporary skill ranks.\n"
    ),
    "Equipment": (
        "#### Domain Sketch\n"
        "Equipment converts advantage rank into a budget of equipment points used to purchase physical gear from the Gadgets & Gear chapter.\n"
        "\n"
        "- grants 5 equipment points per rank, accumulating linearly across ranks (rank 3 = 15 equipment points)\n"
        "- allocates those points to weapons, armor, vehicles, headquarters, and other gear as defined by equipment rules\n"
        "- treats all purchased gear as physical objects subject to the rules of the physical world — equipment can be lost, stolen, or destroyed\n"
        "- does not interact with power level limits — equipment is not a power effect\n"
        "\n"
        "Invariant: equipment points are always 5 per rank; equipment is always subject to loss/theft/destruction; Equipment is never treated as a power effect.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Equipment is a resource-granting advantage: it converts rank to points that purchase gear through equipment chapter rules. The gear carries game-mechanical effect, not the advantage directly.\n"
    ),
    "Minion": (
        "#### Domain Sketch\n"
        "Minion grants the character a follower — an independent character built on a power point budget derived from the advantage rank.\n"
        "\n"
        "- builds the minion with a power point total of exactly (rank × 15) subject to normal series power level limits\n"
        "- prevents the minion from having minions of its own\n"
        "- grants the minion an automatically helpful attitude toward its owner when the minion is capable of independent thought\n"
        "- requires the character to spend earned power points to increase Minion rank and improve the minion's point total and traits\n"
        "- replaces a lost minion between adventures at the Gamemaster's discretion — not in-scene\n"
        "\n"
        "Invariant: minion point total is always exactly rank × 15; minion never has hero points; minion cannot have its own minions; "
        "lost minions are replaced between adventures only.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Kept distinct from Sidekick: Minion grants rank × 15 points, follows minion rules, has no hero points. Sidekick grants rank × 5 points, is a full character, can receive hero points from owner.\n"
    ),
    "Sidekick": (
        "#### Domain Sketch\n"
        "Sidekick grants the character a loyal partner built on a smaller power point budget, treated as a full-fledged character rather than a minion.\n"
        "\n"
        "- builds the sidekick with a power point total of exactly (rank × 5), subject to series power level\n"
        "- requires the sidekick's total power points to always remain less than the character's own total\n"
        "- allows the character to spend hero points on the sidekick's behalf with normal hero point benefits\n"
        "- requires the character to spend earned power points to increase Sidekick rank, adding 5 power points per rank increase\n"
        "- does not apply minion rules to the sidekick — the sidekick is a full character under shared GM/player control\n"
        "\n"
        "Invariant: sidekick total must always be less than owner's total; sidekick has no hero points of its own; "
        "sidekick is never subject to minion rules; hero points spent on the sidekick's behalf come from the owner's pool.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Distinct from Minion: Sidekick costs fewer points per rank (5 vs. 15) but the sidekick is a full character, not a minion-rule follower. Owner can proxy hero points to the sidekick.\n"
    ),
    "Benefit": (
        "#### Domain Sketch\n"
        "Benefit defines a narrative perquisite or fringe benefit cooperatively agreed between the player and GM, purchased with power points.\n"
        "\n"
        "- negotiates the specific benefit with the GM before finalizing — both sides must agree on what the benefit represents\n"
        "- validates that the benefit does not exceed the value of any other advantage or a 1-point power effect\n"
        "- validates that the benefit is significant enough to justify at least 1 power point cost\n"
        "- allows multiple ranks for escalating versions of the same benefit\n"
        "- rejects routine professional credentials — a law or medicine license has no significant game effect and never qualifies\n"
        "\n"
        "Invariant: GM has final approval authority; benefit value ceiling is any other advantage or a 1-point power effect; routine credentials never qualify.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Benefit is intentionally open-ended: the source delegates definition to GM/player negotiation. The system must provide a free-text field for benefit description and track GM approval status.\n"
    ),
    "Skill Mastery": (
        "#### Domain Sketch\n"
        "Skill Mastery removes the pressure restriction for one designated skill, allowing routine checks even under stressful conditions.\n"
        "\n"
        "- removes the restriction that routine checks cannot be made under pressure, but only for the designated skill\n"
        "- records the chosen skill at acquisition — each instance applies to a different skill\n"
        "- does not enable routine checks for skills that categorically prohibit routine checks regardless of conditions\n"
        "- can be acquired multiple times, each time selecting a different qualifying skill\n"
        "\n"
        "Invariant: applies only to the specifically designated skill; does not override categorical prohibitions on routine checks; designated skill is fixed at acquisition.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Skill Mastery is an advantage (not a skill upgrade) because it modifies the conditions under which a skill operates rather than increasing its rank.\n"
    ),
    "Jack of all Trades": (
        "#### Domain Sketch\n"
        "Jack-of-all-trades removes the trained restriction for all skills simultaneously, making the character a universal generalist without eliminating tool requirements.\n"
        "\n"
        "- removes the restriction that certain skills or skill aspects require training before they can be used\n"
        "- maintains tool requirements — if a skill requires tools, those tools are still needed even with this advantage\n"
        "- applies passively and globally — no per-skill or per-check activation required\n"
        "\n"
        "Invariant: tool requirements still apply and are never waived by this advantage; training restriction is fully removed for all skills; no activation is required.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Distinct from Skill Mastery: Jack-of-all-trades removes training barriers globally; Skill Mastery removes pressure restrictions for one specific skill.\n"
    ),
    "Favored Foe": (
        "#### Domain Sketch\n"
        "Favored Foe grants a targeted circumstance bonus across four interaction and perception skills specifically when dealing with a designated opponent type.\n"
        "\n"
        "- records the favored foe type at acquisition: a creature type (aliens, animals, constructs, mutants, undead) or a profession (soldiers, police, Yakuza) approved by the GM\n"
        "- enforces that the type is not excessively broad — categories like \"humans\" or \"villains\" are not permitted\n"
        "- grants +2 circumstance bonus to Deception, Intimidation, Insight, and Perception checks when those checks involve the favored foe\n"
        "- does not apply to checks against targets that are not of the favored foe type\n"
        "\n"
        "Invariant: +2 bonus is not subject to power level limits; foe type must be specific enough to receive GM approval; "
        "bonus applies to exactly the four listed skills; does not apply outside qualifying interactions with the favored foe.\n"
        "\n"
        "#### Decisions made (term level)\n"
        "- Classified under Skill Advantage (not Combat Enhancement) because its bonus applies across four social and perception skill checks; the source labels it SKILL.\n"
    ),
}

BOUNDARY_SKETCHES = {
    "hero point": (
        "#### Domain Sketch\n"
        "Hero point is the meta-currency owned by Character Construction that fortune advantages consume to activate their effects. "
        "This module defines only the spend effects — it does not own hero point generation, refresh, or storage.\n"
        "\n"
        "- consumed by fortune advantages (Inspire, Leadership, Beginner's Luck) as the activation cost for their effects\n"
        "- proxied by Luck for re-roll effects — Luck draws from its own per-session pool rather than consuming an actual hero point\n"
        "- bypasses power level limits when funding Inspire's bonus — a property of hero point benefits generally\n"
        "\n"
        "Invariant: hero points are owned by Character Construction; this module consumes them but never generates or refreshes them.\n"
    ),
    "power point": (
        "#### Domain Sketch\n"
        "Power point is the acquisition currency owned by Character Construction that funds advantage purchases. "
        "This module consumes power points at 1 per advantage rank — it does not own their generation or budget.\n"
        "\n"
        "- funds advantage acquisition at 1 power point per rank for all advantages in this module\n"
        "- funds rank increases for Minion and Sidekick out of the character's earned power points pool\n"
        "\n"
        "Invariant: power points are owned by Character Construction; this module spends them but never generates them.\n"
    ),
    "power level": (
        "#### Domain Sketch\n"
        "Power level is the series cap owned by Character Construction that enforces upper bounds on attack bonuses and Luck's maximum rank. "
        "This module depends on it for cap enforcement but does not own it.\n"
        "\n"
        "- caps total attack bonus (including bonuses from Ranged Attack and Close Attack advantages) at the series power level\n"
        "- limits Luck's maximum rank to half the series power level (rounded down)\n"
        "- does not cap circumstance bonuses from Favored Environment or Favored Foe — those explicitly ignore power level limits\n"
        "\n"
        "Invariant: power level cap applies to attack bonuses from ranked attack advantages; Luck rank cap is always half PL rounded down; "
        "circumstance bonuses from Favored Environment and Favored Foe are always exempt from the cap.\n"
    ),
    "attack check": (
        "#### Domain Sketch\n"
        "Attack check is the combat roll owned by the Combat module that combat advantages modify. "
        "This module adjusts attack check bonuses and penalties but does not own attack resolution.\n"
        "\n"
        "- receives bonus adjustments from Ranged Attack (+1/rank) and Close Attack (+1/rank), both subject to power level cap\n"
        "- receives penalty or bonus adjustments during trade-off maneuvers: Accurate Attack, All-out Attack, Defensive Attack, Power Attack each apply −N or +N to the attack check\n"
        "- receives optional +2 circumstance bonus from Favored Environment when the player chooses attack allocation at round start\n"
        "\n"
        "Invariant: attack checks are owned by Combat; this module modifies their bonus values through advantage rules but does not resolve the check.\n"
    ),
    "active defense": (
        "#### Domain Sketch\n"
        "Active defense is the combat defense value (Dodge and Parry) owned by the Combat module that combat advantages modify. "
        "This module adjusts active defense values through trade-off maneuvers and circumstance bonuses.\n"
        "\n"
        "- receives penalty adjustments from All-out Attack (−N to both Dodge and Parry, symmetric with attack bonus)\n"
        "- receives bonus adjustments from Defensive Attack (+N to both Dodge and Parry, symmetric with attack penalty)\n"
        "- receives optional +2 circumstance bonus from Favored Environment when the player chooses defense allocation at round start\n"
        "\n"
        "Invariant: active defenses are owned by Combat; this module modifies them through advantage rules but does not resolve defense checks.\n"
    ),
    "extra effort": (
        "#### Domain Sketch\n"
        "Extra effort is the general mechanic owned by the Combat module. "
        "Extraordinary Effort modifies it: granting two benefits instead of one at doubled fatigue cost.\n"
        "\n"
        "- doubles the normal benefits of extra effort (two benefits instead of one, including stacking the same type twice)\n"
        "- doubles the fatigue cost (character becomes exhausted instead of fatigued, starting the turn after)\n"
        "- prevents use when already exhausted\n"
        "- allows reduction of the doubled fatigue cost back to normal (fatigued) by spending a hero point at the start of the following turn\n"
        "\n"
        "Invariant: extra effort mechanics are owned by Combat; Extraordinary Effort modifies benefit count and fatigue cost but not what benefits are available.\n"
    ),
}


def process_file(input_path, output_path):
    with open(input_path, encoding='utf-8', newline='') as f:
        content = f.read()

    lines = content.split('\r\n')
    result = []
    in_source_block = False
    pending_sketch = None      # text to insert before next section boundary
    pending_from_boundary = False  # True if pending is from a ## boundary term

    def flush_pending():
        nonlocal pending_sketch, pending_from_boundary
        if pending_sketch:
            result.append('')
            for sketch_line in pending_sketch.rstrip('\n').split('\n'):
                result.append(sketch_line)
            pending_sketch = None
            pending_from_boundary = False

    for line in lines:
        stripped = line.strip()

        # Toggle source block
        if stripped == '```source':
            in_source_block = True
            result.append(line)
            continue
        if stripped == '```' and in_source_block:
            in_source_block = False
            result.append(line)
            continue

        if not in_source_block:
            is_any_heading = re.match(r'^#{1,6} ', line) is not None
            is_separator = stripped == '---'

            if is_any_heading or is_separator:
                if pending_sketch is not None:
                    if pending_from_boundary:
                        # Boundary sketches only flush on ## heading or ---
                        is_2hash = re.match(r'^## ', line) is not None
                        if is_2hash or is_separator:
                            flush_pending()
                    else:
                        # Term sketches flush on any heading or ---
                        flush_pending()

            # Check for #### term heading
            m4 = re.match(r'^#### (.+)$', line)
            if m4:
                term = m4.group(1).strip()
                # Only set pending for known domain terms (not content headings like "Domain Language")
                if term in DOMAIN_SKETCHES:
                    # Flush any current pending first (already handled above for the boundary)
                    pending_sketch = DOMAIN_SKETCHES[term]
                    pending_from_boundary = False
                # (Do NOT clear pending if term is unknown — let existing pending survive)

            # Check for ## boundary term heading
            m2 = re.match(r'^## (.+)$', line)
            if m2:
                bterm = m2.group(1).strip()
                if bterm in BOUNDARY_SKETCHES:
                    pending_sketch = BOUNDARY_SKETCHES[bterm]
                    pending_from_boundary = True

        result.append(line)

    # Flush any remaining pending sketch at end of file
    if pending_sketch:
        flush_pending()

    output = '\r\n'.join(result)
    output = output.replace('state: key-abstractions', 'state: domain-sketch', 1)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(output)

    count = sum(1 for ln in output.split('\r\n') if ln.strip() == '#### Domain Sketch')
    print(f"Done. Domain Sketch sections: {count}")
    return count


if __name__ == '__main__':
    inp = r'c:\dev\mm3e-online-holistic\docs\advantage\advantage.md'
    out = r'c:\dev\mm3e-online-holistic\docs\advantage\advantage.md'
    process_file(inp, out)
