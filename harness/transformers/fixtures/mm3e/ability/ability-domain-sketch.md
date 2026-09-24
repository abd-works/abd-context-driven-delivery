---
state: domain-sketch
---

## Module: [Ability]

Scope: The eight ability scores (Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence), absent abilities, debilitated abilities, and derived defense values.

**Core terms**:
- ability
- ability rank
- absent ability
- Strength (STR)
- Stamina (STA)
- Agility (AGL)
- Dexterity (DEX)
- Fighting (FGT)
- Intellect (INT)
- Awareness (AWE)
- Presence (PRE)
- Dodge
- Parry
- Fortitude
- Toughness
- Will
- defense
- debilitated

---

## Domain logic

- An ability rank of 0 is the baseline average adult; positive ranks provide bonuses on related rolls and negative ranks apply penalties.
- Whenever an ability rank changes, all traits derived from that ability — associated skills, defense values, and attack modifiers — change with it in the same operation.
- An absent ability is not the same as rank −5; absence has its own per-ability capability-loss rules and cannot be weakened or debilitated.
- An ability rank that drops below −5 triggers the debilitated state immediately; further rank reduction is blocked once the floor is reached.
- The five defenses (Dodge, Parry, Fortitude, Toughness, Will) each have a base equal to the rank of a specific ability; the base updates automatically whenever the source ability changes.
- Toughness is the only defense that cannot be raised above its Stamina base by direct power point spending.
- Active defenses (Dodge and Parry) degrade under the vulnerable condition (halved, round up) and the defenseless condition (reduced to 0); passive defenses (Fortitude, Toughness, Will) are unaffected by those conditions.

---

# Core Domain

## Ability Score

The Ability Score is the foundational quantitative expression of a character's inherent capabilities and the single source of truth for all trait-based interactions in the game system. It owns the rank-purchase economy (2 power points per rank, with a refund on reduction), the benchmark scale from −5 to 20 and beyond for cosmic entities, the physical/mental categorization, the cascade rule that propagates rank changes to all dependent traits, and the distinction between natural and enhanced rank portions. Eight named ability scores divide into physical (Strength, Stamina, Agility, Dexterity) and mental (Fighting, Intellect, Awareness, Presence), each contributing specific die roll bonuses and serving as the base for particular derived values. The ability score enforces the cost and refund formula locally but does not own the currency it consumes (power points) or the upper bound on increases (power level), both of which belong to the Character Construction module.

A critical cascade rule governs this KA: whenever an ability rank changes — through power point spending, a power effect, or any mechanism — every trait derived from that ability changes proportionally, including skills, defense values, and attack modifiers. The player also designates whether any portion of a rank is an Enhanced Trait (power); that designation carries downstream consequences for nullification, power modifier application, and power stunt eligibility that the system must track separately from the base rank.

#### Decisions made
- The eight named abilities are kept as distinct `### term` headings (not collapsed into one) because each has a different set of associated rolls, skills, and derived values — they are not instances with identical behavior.
- Fighting is classified as "mental" per the source text alongside INT, AWE, PRE — preserved even though it governs a physical combat mechanic.
- `enhanced ability` is included here as a found term under Ability Score (independence test: it is a variant rank designation, not an independent KA; module-fit test: its rules for nullification and power modifiers are part of how ability ranks work).
- power point and power level moved to Boundary Domain — this module depends on them but does not define them.

### ability

#### Domain language
- One of eight fundamental numeric traits that characterize a hero's physical or mental capabilities.
- Partitioned into physical abilities (STR, STA, AGL, DEX) and mental abilities (FGT, INT, AWE, PRE).
- Each above-average ability rank provides a bonus on related die rolls; below-average rank applies a penalty.
- The ability rank is added to (or subtracted from) die rolls for tasks related to that ability and to calculate derived values.
- Ability ranks can be bought up using power points, reduced below 0 for bonus power points, or altered by power effects during play.
- Some ability ranks — or portions of them — can be designated as Enhanced Traits (powers), which behave differently from natural ranks.

#### Domain Sketch
- Stores a signed integer rank that modifies related die rolls as a direct numeric bonus or penalty.
- Determines which skills and derived defense values it feeds into based on which of the eight named types it is.
- Changes value when the player spends power points (at creation or advancement) or when a power effect alters it.
- Propagates the rank change to all dependent traits in the same operation — skills update, defenses update, attack modifiers update.
- Invariant: rank can never drop below −5 through voluntary player adjustment; values below −5 indicate a debilitated state triggered only by external game effects.
- Invariant: if a rank changes, all dependent traits must update to reflect the new value in the same operation.

#### References

**Ref — Ch3 Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_035.md
Locator: lines 2298-2362
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch3 Abilities"
topic: "Ch3 Abilities"
chunk_index: 35
line_range: "2298-2362"
---

## CHAPTER 3: ABILITIES
Everyone has certain basic abilities: how strong, fast, smart, and clever they are. These abilities influence most things
your character does. Stronger characters can lift greater weights, more agile characters have better balance, tougher
characters can soak up more damage, and so forth.
MUTANTS & MASTERMINDS characters have eight basic abilities: Strength (Str), Stamina (Sta), Dexterity (Dex), Agility (Agl),
Fighting (Ftg), Intellect (Int), Awareness (Awe), and Presence (Pre). Strength, Dexterity, Agility and Stamina are physical
abilities, whereas Fighting, Intellect, Awareness, and Presence are mental abilities. Each above-average ability pro-
vides a bonus on certain die rolls; while below average abilities apply a penalty.

### Ability Ranks
Each ability has a rank associated with it, based on how above or below average it is. Abilities start at rank 0, the baseline
average for an adult human being. They can go as low as â€"5 (truly terrible) and as high as 20, with higher values reserved
for truly cosmic beings and forces.
The ability rank is added to, or subtracted from, die rolls when your character does something related to that ability. For
example, your Strength rank affects the amount of damage you do when punching someone. Your Intellect rank comes
into play when you roll skills based on Intellect, and so forth. Sometimes your rank is used to calculate another value, such
as when you use your Agility to determine how good you are at avoiding harm with your reflexes (your Dodge defense).

### Buying Ability Ranks
You choose your heroâ€™s ability ranks by spending power
points on them. Increasing an ability rank by 1 costs 2
power points, so putting two points into Strength, for ex-
ample, raises it from 0 to 1. Remember a rank of 0 is av-
erage, 2 is a fair amount of talent or natural ability, 3 is
exceptional, 4 extraordinary, and so forth. (See the Ability
Benchmarks table for guidelines.)

### Reducing Abilities
You can also lower one or more of your characterâ€™s ability
ranks from the starting value of 0. Each rank you lower an
ability gives you an additional two power points to spend
elsewhere. You cannot lower an ability rank below â€"5,
which is itself a serious deficiency.
Ability Cost = 2 power points
per +1 to an ability rank.
Gain 2 bonus power points
per -1 to an ability rank.

### Ability Benchmarks
RANK
DESCRIPTION
â€"5
Completely inept or disabled
â€"4
Weak; infant
â€"3
Younger child
â€"2
Child, elderly, impaired
â€"1
Below average; teenager
Average adult
Above average
Well above average
Gifted
Highly gifted
Best in a nation
One of the best in the world
Best ever; peak of human achievement
Low superhuman
Moderate superhuman
High superhuman
Very high superhuman
Cosmic
```

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch3 Abilities"
topic: "Beyond Human"
chunk_index: 36
line_range: "2363-2464"
---

### Beyond Human
Although a rank of 7 is defined as â€œthe peak of human achievementâ€ in an ability on the Ability Benchmarks table, a character
with an ability rank greater than 7 isnâ€™t necessarily â€œnon-human,â€ merely superhuman in comparison to ordinary people. Many
â€œnormal humanâ€ characters in the comics have truly superhuman abilities, particularly mental abilities. A character can have
a superhuman ability rank without necessarily being anything other than an amazingly talented, well-trained human being.
The limits of what â€œnormalâ€ people can accomplish is up to the Gamemaster and depends very much on the style of the game.

STRENGTH (STR)
Strength measures sheer muscle power and the ability to
apply it. Your Strength rank applies to:
â€¢
Damage dealt by your unarmed and strength-based
attacks.
â€¢
How far you can jump (based on an Athletics skill check).
â€¢
The amount of weight you can lift, carry, and throw.
â€¢
Athletics skill checks.
STAMINA (STA)
Stamina is health, endurance, and overall physical resil-
ience. Stamina is important because it affects a charac-
terâ€™s ability to resist most forms of damage. Your Stamina
modifier applies to:
â€¢
Toughness defense, for resisting damage.
â€¢
Fortitude defense, for resisting effects targeting your
characterâ€™s health.
â€¢
Stamina checks to resist or recover from things af-
fecting your characterâ€™s health when a specific de-
fense doesnâ€™t apply.
AGILITY (AGL)
Agility is balance, grace, speed, and overall physical coor-
dination. Your Agility rank applies to:
â€¢
Dodge defense, for avoiding ranged attacks and oth-
er hazards.
â€¢
Initiative bonus, for acting first in combat.
â€¢
Acrobatics and Stealth skill checks.
â€¢
Agility checks for feats of coordination, gross move-
ment, and quickness when a specific skill doesnâ€™t apply.
DEXTERITY (DEX)
Dexterity is a measure of hand-eye coordination, preci-
sion, and manual dexterity. Your Dexterity rank applies to:
â€¢
Attack checks for ranged attacks.
â€¢
Sleight of Hand and Vehicles skill checks.
â€¢
Dexterity checks for feats of fine control and preci-
sion when a specific skill doesnâ€™t apply.
FIGHTING (FGT)
Fighting measures your characterâ€™s ability in close com-
bat, from hitting a target to ducking and weaving around
any counter-attacks. Your Fighting rank applies to:
â€¢
Attack checks for close attacks.
â€¢
Parry defense, for avoiding close attacks.
INTELLECT (INT)
Intellect covers reasoning ability and learning. A character
with a high Intellect rank tends to be knowledgeable and
well-educated. Your Intellect modifier applies to:
â€¢
Expertise, Investigation, Technology, and Treatment
skill checks.
â€¢
Intellect checks to solve problems using sheer brain-
power when a specific skill doesnâ€™t apply.
AWARENESS (AWE)
While Intellect covers reasoning, Awareness describes
common sense and intuition, what some might call â€œwis-
dom.â€ A character with a high Intellect and a low Aware-
ness may be an â€œabsent-minded professorâ€ type, smart but
not always aware of whatâ€™s going on. On the other hand,
a not so bright (low Intellect) character may have great
deal of common sense (high Awareness). Your Awareness
modifier applies to:
â€¢
Will defense, for resisting attacks on your mind.
â€¢
Insight and Perception skill checks.
â€¢
Awareness checks to resolve matters of intuition
when a specific skill doesnâ€™t apply.
PRESENCE (PRE)
Presence is force of personality, persuasiveness, leader-
ship ability and (to a lesser degree) attractiveness. Pres-
ence is useful for heroes who intend to be leaders as well
as those who strike fear into the hearts of criminals with
their presence. Your Presence modifier applies to:
â€¢
Deception, Intimidation, and Persuasion skill checks.
â€¢
Presence checks to influence others through force of
personality when a specific skill doesnâ€™t apply.
```

---

### ability rank

#### Domain language
- Numeric value expressing the degree of an ability; starts at 0 (the baseline average for an adult human).
- Can go as low as −5 (truly terrible) and as high as 20 or beyond for cosmic beings and forces.
- Costs 2 power points per +1 rank when purchased; yields 2 bonus power points per −1 rank when reduced.
- Cannot be voluntarily lowered below −5; dropping below −5 due to an external effect triggers the debilitated state.
- Used directly as a modifier on die rolls and as the base for calculating derived defense values.

#### Domain Sketch
- Represents the current signed integer value of a specific ability, serving as both a direct modifier and a base for derived calculations.
- Tracks whether a rank is normal, enhanced, or a combination — each portion with distinct properties under the rules.
- Resolves the cost/refund formula when the player adjusts it: positive delta costs 2 pp per +1, negative delta refunds 2 pp per −1.
- Invariant: rank must remain in the range [−5, ∞) after voluntary player adjustments; the floor is enforced at purchase time.
- Invariant: the enhanced portion of a rank is tracked separately from the base portion so it can be selectively nullified without affecting the natural portion.

#### References

**Ref — Ch3 Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_035.md
Locator: lines 2298-2362
Extract: partial
Part: "Ability Ranks", "Buying Ability Ranks", "Reducing Abilities", and "Ability Benchmarks" sections.

```source
### Ability Ranks
Each ability has a rank associated with it, based on how above or below average it is. Abilities start at rank 0, the baseline
average for an adult human being. They can go as low as â€"5 (truly terrible) and as high as 20, with higher values reserved
for truly cosmic beings and forces.
The ability rank is added to, or subtracted from, die rolls when your character does something related to that ability.

### Buying Ability Ranks
You choose your heroâ€™s ability ranks by spending power
points on them. Increasing an ability rank by 1 costs 2
power points, so putting two points into Strength, for ex-
ample, raises it from 0 to 1.

### Reducing Abilities
You can also lower one or more of your characterâ€™s ability
ranks from the starting value of 0. Each rank you lower an
ability gives you an additional two power points to spend
elsewhere. You cannot lower an ability rank below â€"5,
which is itself a serious deficiency.
Ability Cost = 2 power points per +1 to an ability rank.
Gain 2 bonus power points per -1 to an ability rank.
```

---

### Strength (STR)

#### Domain language
- Measures sheer muscle power and the ability to apply physical force.
- Applies to: unarmed and strength-based attack damage; jump distance (Athletics check); weight lifting, carrying, and throwing; Athletics skill checks.
- Physical ability.

#### Domain Sketch
- Contributes its rank directly as damage bonus on unarmed and strength-based attacks.
- Feeds into jump-distance calculation as part of Athletics checks and into all Athletics skill checks for physical tasks.
- Invariant: when STR is debilitated, the hero collapses (defenseless, immobilized, stunned) — STR no longer contributes meaningful attack damage or Athletics bonuses while in the collapsed state.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: STRENGTH (STR) section.

```source
STRENGTH (STR)
Strength measures sheer muscle power and the ability to
apply it. Your Strength rank applies to:
â€¢
Damage dealt by your unarmed and strength-based
attacks.
â€¢
How far you can jump (based on an Athletics skill check).
â€¢
The amount of weight you can lift, carry, and throw.
â€¢
Athletics skill checks.
```

---

### Stamina (STA)

#### Domain language
- Measures health, endurance, and overall physical resilience.
- Applies to: Toughness defense (resisting damage); Fortitude defense (resisting effects on health); Stamina checks for health-related resistance and recovery when no specific defense applies.
- Physical ability.

#### Domain Sketch
- Contributes its rank as the base value for both Toughness and Fortitude defenses simultaneously — two derivations from one source.
- Provides the resistance modifier for any health-based check when a specific defense is not named.
- Invariant: when STA is debilitated, the hero enters the dying state with a −5 Fortitude penalty stacked on top of any existing penalties.
- Invariant: a creature with no Stamina has no Fortitude defense; the derivation has no source.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: STAMINA (STA) section.

```source
STAMINA (STA)
Stamina is health, endurance, and overall physical resil-
ience. Stamina is important because it affects a charac-
terâ€™s ability to resist most forms of damage. Your Stamina
modifier applies to:
â€¢
Toughness defense, for resisting damage.
â€¢
Fortitude defense, for resisting effects targeting your
characterâ€™s health.
â€¢
Stamina checks to resist or recover from things af-
fecting your characterâ€™s health when a specific de-
fense doesnâ€™t apply.
```

---

### Agility (AGL)

#### Domain language
- Measures balance, grace, speed, and overall physical coordination.
- Applies to: Dodge defense (avoiding ranged attacks and hazards); initiative bonus (acting first in combat); Acrobatics and Stealth skill checks; Agility checks for coordination feats.
- Physical ability.

#### Domain Sketch
- Contributes its rank as the base value for Dodge defense and as the base component of the initiative modifier.
- Feeds into Acrobatics and Stealth skill checks as the primary modifier.
- Invariant: when AGL is debilitated, the hero collapses (defenseless, immobilized, stunned) — Dodge defense and initiative modifier both become non-functional.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: AGILITY (AGL) section.

```source
AGILITY (AGL)
Agility is balance, grace, speed, and overall physical coor-
dination. Your Agility rank applies to:
â€¢
Dodge defense, for avoiding ranged attacks and oth-
er hazards.
â€¢
Initiative bonus, for acting first in combat.
â€¢
Acrobatics and Stealth skill checks.
â€¢
Agility checks for feats of coordination, gross move-
ment, and quickness when a specific skill doesnâ€™t apply.
```

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: DODGE and initiative sections (Agility's contribution to both).

```source
DODGE
Dodge defense is based on Agility rank. It includes reac-
tion time, quickness, nimbleness, and overall coordina-
tion, used to avoid ranged attacks or other hazards where
reflexes and speed are important.

Initiative Modifier = Agility + Advantages
(Improved Initiative) + Power Modifiers
```

---

### Dexterity (DEX)

#### Domain language
- Measures hand-eye coordination, precision, and manual dexterity.
- Applies to: ranged attack checks; Sleight of Hand and Vehicles skill checks; Dexterity checks for fine control and precision tasks.
- Physical ability.

#### Domain Sketch
- Contributes its rank as the modifier for all ranged attack checks.
- Feeds into Sleight of Hand and Vehicles skill checks as the primary modifier.
- Invariant: when DEX is debilitated, the hero collapses (defenseless, immobilized, stunned) — ranged attack checks become impossible.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: DEXTERITY (DEX) section.

```source
DEXTERITY (DEX)
Dexterity is a measure of hand-eye coordination, preci-
sion, and manual dexterity. Your Dexterity rank applies to:
â€¢
Attack checks for ranged attacks.
â€¢
Sleight of Hand and Vehicles skill checks.
â€¢
Dexterity checks for feats of fine control and preci-
sion when a specific skill doesnâ€™t apply.
```

---

### Fighting (FGT)

#### Domain language
- Measures close combat ability — hitting targets and evading counter-attacks in melee.
- Applies to: close attack checks; Parry defense (avoiding close attacks).
- Mental ability (grouped with INT, AWE, PRE as a mental ability in the core rules).

#### Domain Sketch
- Contributes its rank as the modifier for all close attack checks.
- Contributes its rank as the base value for Parry defense.
- Invariant: when FGT is debilitated, the hero is dazed and defenseless and cannot make close attacks.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: FIGHTING (FGT) section.

```source
FIGHTING (FGT)
Fighting measures your characterâ€™s ability in close com-
bat, from hitting a target to ducking and weaving around
any counter-attacks. Your Fighting rank applies to:
â€¢
Attack checks for close attacks.
â€¢
Parry defense, for avoiding close attacks.
```

---

### Intellect (INT)

#### Domain language
- Covers reasoning ability and learning; a high rank correlates with knowledge and education.
- Applies to: Expertise, Investigation, Technology, and Treatment skill checks; Intellect checks for pure reasoning when no specific skill applies.
- Mental ability.

#### Domain Sketch
- Contributes its rank as the modifier for Expertise, Investigation, Technology, and Treatment skill checks.
- Provides the general reasoning modifier when no specific skill applies to a problem.
- Invariant: when INT is debilitated, the hero is unaware and remains so until the ability rank is restored to at least −5.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: INTELLECT (INT) section.

```source
INTELLECT (INT)
Intellect covers reasoning ability and learning. A character
with a high Intellect rank tends to be knowledgeable and
well-educated. Your Intellect modifier applies to:
â€¢
Expertise, Investigation, Technology, and Treatment
skill checks.
â€¢
Intellect checks to solve problems using sheer brain-
power when a specific skill doesnâ€™t apply.
```

---

### Awareness (AWE)

#### Domain language
- Covers common sense and intuition ("wisdom"), distinct from Intellect (reasoning).
- Applies to: Will defense (resisting mental attacks); Insight and Perception skill checks; Awareness checks for intuition when no specific skill applies.
- Mental ability.
- A creature with no Awareness is also treated as having no Presence; awareness and presence absence are linked.

#### Domain Sketch
- Contributes its rank as the base value for Will defense.
- Contributes its rank as the modifier for Insight and Perception skill checks.
- Invariant: when AWE is debilitated, the hero is unaware and remains so until the rank is restored to at least −5.
- Invariant: if AWE is absent, Presence is automatically absent too — the two abilities share an absence linkage defined in Ch3.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: AWARENESS (AWE) section.

```source
AWARENESS (AWE)
While Intellect covers reasoning, Awareness describes
common sense and intuition, what some might call â€œwis-
dom.â€ A character with a high Intellect and a low Aware-
ness may be an â€œabsent-minded professorâ€ type, smart but
not always aware of whatâ€™s going on. On the other hand,
a not so bright (low Intellect) character may have great
deal of common sense (high Awareness). Your Awareness
modifier applies to:
â€¢
Will defense, for resisting attacks on your mind.
â€¢
Insight and Perception skill checks.
â€¢
Awareness checks to resolve matters of intuition
when a specific skill doesnâ€™t apply.
```

**Ref — Absent Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_038.md
Locator: lines 2525-2595
Extract: partial
Part: Awareness absence entry — "completely unaware and also has no Presence."

```source
â€¢
Awareness: Anything with no Awareness is com-
pletely unaware and also has no Presence. It is an in-
animate object, not a creature. Objects are immune
to mental effects and interaction skills, and have no
defenses apart from Toughness (and Fortitude, if
they are alive).
```

---

### Presence (PRE)

#### Domain language
- Measures force of personality, persuasiveness, leadership ability, and attractiveness.
- Applies to: Deception, Intimidation, and Persuasion skill checks; Presence checks to influence others through force of personality.
- Mental ability.

#### Domain Sketch
- Contributes its rank as the modifier for Deception, Intimidation, and Persuasion skill checks.
- Provides the general force-of-personality modifier when no specific interaction skill applies.
- Invariant: when PRE is debilitated, the hero is unaware and remains so until the rank is restored to at least −5.

#### References

**Ref — Beyond Human**
Source: context/rules/HeroesHandbook-rules__chunk_036.md
Locator: lines 2363-2464
Extract: partial
Part: PRESENCE (PRE) section.

```source
PRESENCE (PRE)
Presence is force of personality, persuasiveness, leader-
ship ability and (to a lesser degree) attractiveness. Pres-
ence is useful for heroes who intend to be leaders as well
as those who strike fear into the hearts of criminals with
their presence. Your Presence modifier applies to:
â€¢
Deception, Intimidation, and Persuasion skill checks.
â€¢
Presence checks to influence others through force of
personality when a specific skill doesnâ€™t apply.
```

---

### enhanced ability

*(Found term — discovered in source material; not in original Core terms list.)*

#### Domain language
- An ability rank (or portion thereof) acquired as an Enhanced Trait (power) rather than as a natural rank.
- Can be nullified by the Nullify effect — normal (natural) ability ranks cannot be nullified.
- Can have power modifiers and be used for power stunts with extra effort — normal ranks cannot.
- Same cost as normal ability ranks: 2 power points per +1 rank.
- The player decides whether a rank is normal, enhanced, or a combination; both apply as modifier simultaneously.

#### Domain Sketch
- Tracks a subset of the total ability rank that is designated as power-based rather than natural.
- Contributes its rank to the total modifier in the same way as the natural portion (the sum applies to all die rolls and derivations).
- Can be temporarily removed by the Nullify effect, reducing the total ability modifier by the enhanced portion during nullification.
- Can receive power modifiers (extras and flaws) that alter its behavior, cost, or power stunt eligibility.
- Invariant: nullifying the enhanced portion does not affect the natural portion — each tracks its own rank independently.
- Invariant: the total ability modifier is always the sum of natural + enhanced rank; the two portions are additive.

#### References

**Ref — Enhanced Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_037.md
Locator: lines 2465-2524
Extract: partial
Part: "Enhanced Abilities" section.

```source
### Enhanced Abilities
Some ability ranksâ€"or portions of themâ€"may be ac-
quired as Enhanced Traits, as described in the Powers
chapter. Enhanced Abilities are superhuman powers rath-
er than natural. The key differences between Enhanced
Abilities and normal ability ranks are Enhanced Abilities
can be nullified (normal abilities cannot, see Nullify, page
173) and Enhanced Abilities can have power modifiers
and be used for power stunts with extra effort (normal
abilities cannot, see Extra Effort, page 19).
Enhanced Abilities and normal abilities have the same
cost (2 power points per +1 ability rank). The player de-
cides if a characterâ€™s ability rank is normal or enhanced
and, if it is enhanced, how much of it is enhanced.
```

---

### Enhanced Ability *is a type of* ability

An Enhanced Ability is an ability rank (or portion of one) that is acquired as a power rather than through natural training or inherent capability. It shares the same cost formula and total-modifier contribution as a natural ability rank but adds three distinct behaviors: it can be nullified (suppressed by the Nullify power effect), it can have power modifiers attached to it, and it can be used for power stunts with extra effort. The natural portion of the same ability is unaffected when the enhanced portion is nullified.

#### Domain Sketch
- Can be nullified by the Nullify effect; the total ability modifier drops by the enhanced portion's rank during nullification.
- Can have power modifiers (extras and flaws) applied to it, altering its cost or adding special conditions to its use.
- Can be used for power stunts with extra effort — enabling improvised uses beyond its normal scope.
- Invariant: nullification of the enhanced portion does not change the natural portion of the same ability.
- Invariant: power stunt eligibility and power modifier application apply only to the designated enhanced portion, not to the natural portion.

#### Decisions made
- Enhanced Ability is modeled as a subtype of ability (not a separate KA) because its core mechanic — buying and tracking a rank — is identical to a natural ability rank; it only adds three delta behaviors.
- The natural/enhanced split within a single ability is an open question for the object-model phase: whether the two portions are properties on one object or two separate objects with a shared aggregation.

#### References

**Ref — Enhanced Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_037.md
Locator: lines 2465-2524
Extract: partial
Part: "Enhanced Abilities" section (same source as parent term; delta behaviors identified here).

```source
### Enhanced Abilities
Some ability ranksâ€"or portions of themâ€"may be ac-
quired as Enhanced Traits, as described in the Powers
chapter. Enhanced Abilities are superhuman powers rath-
er than natural. The key differences between Enhanced
Abilities and normal ability ranks are Enhanced Abilities
can be nullified (normal abilities cannot, see Nullify, page
173) and Enhanced Abilities can have power modifiers
and be used for power stunts with extra effort (normal
abilities cannot, see Extra Effort, page 19).
Enhanced Abilities and normal abilities have the same
cost (2 power points per +1 ability rank). The player de-
cides if a characterâ€™s ability rank is normal or enhanced
and, if it is enhanced, how much of it is enhanced.
```

---

## Absent Ability

Absent Ability is the exceptional creature-design state in which a being entirely lacks one of the eight ability scores — a condition distinct from having rank −5 and carrying its own specific capability-loss rules per ability. This KA owns the per-ability absence effects (no Strength means no physical force; no Stamina means no living-body mechanics and no Fortitude defense; no Dexterity means no object manipulation or physical attacks; no Agility means no self-propelled movement or Dodge defense; no Fighting means no close attacks; no Intellect means automaton status with no Will defense; no Awareness means total unawareness and also no Presence; no Presence means no interaction and no Will defense), the −10 power point benefit (richer than the −5 floor on normal ranks), the automatic-fail rule on related checks, and the rule that absent abilities cannot be further weakened or debilitated. Heroes require GM permission to lack an ability; constructs and non-living entities naturally have absent abilities as part of their creature-type definition.

#### Decisions made
- Absent Ability passes the independence test: it has distinct identity, distinct rules (−10 pp, auto-fail, per-ability capability loss), and distinct interactions (cannot be weakened or debilitated) that set it apart from simply having a rank of −5.
- Absent Ability passes the module-fit test: it is defined in Ch3 Abilities, directly within this module's scope.
- Absent Ability is its own KA rather than a sub-concept under Ability Score because the absence rules are fundamentally different from rank mechanics — there is no rank, no modifier, no purchasing, and different recovery/vulnerability behavior.
- Construct and inanimate object rules (which abilities they have) appear here as evidence for absence but the Construct type itself is boundary to the Equipment/Power module.

### absent ability

#### Domain language
- A creature entirely lacking an ability has no rank for it, a state distinct from having rank −5.
- Automatically fails any check requiring the absent ability.
- Lacking an ability grants an additional 10 power points to spend elsewhere — more generous than the −5 floor.
- Heroes cannot lack an ability without Gamemaster permission, as absence has significant game effects.
- An absent ability cannot be weakened or debilitated — it simply is not present.
- Per-ability absence effects:
  - No Strength: incapable of exerting any physical force (incorporeal or immobile creature).
  - No Stamina: no physical body; suffers and recovers from damage as an inanimate object; immune to fatigue; no Fortitude defense.
  - No Dexterity: cannot manipulate objects; cannot make physical attacks.
  - No Agility: unable to move under own power; no Dodge defense.
  - No Fighting: incapable of any close attack.
  - No Intellect: automaton; immune to mental effects and interaction skills; no Will defense.
  - No Awareness: completely unaware; also has no Presence; immune to mental effects and interaction skills; treated as inanimate object.
  - No Presence: unable to interact; immune to interaction skills; no Will defense.

#### Domain Sketch
- Represents the complete non-existence of an ability — no rank to apply, no modifier to add, no defense to derive.
- Applies per-ability capability restrictions as permanent characteristics of the creature.
- Grants −10 power points at character-creation time as compensation, recorded at creation, not recalculated at runtime.
- Enforces automatic failure on all checks that would use the absent ability's modifier.
- Invariant: an absent ability cannot be weakened by the Weaken effect (no rank to weaken) or debilitated (no rank to drop below −5).
- Invariant: a hero character cannot have an absent ability without explicit GM authorization.
- Invariant: when Awareness is absent, Presence is automatically absent — the two are linked and cannot be independently absent.

#### References

**Ref — Absent Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_038.md
Locator: lines 2525-2595
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch3 Abilities"
topic: "Absent Abilities"
chunk_index: 38
line_range: "2525-2595"
---

### Absent Abilities
Rather than having a rank of â€"5 in a given ability, some
things or creatures actually lack an ability altogether.
These beings automatically fail any check requiring the
absent ability. The additional effects of an absent ability
are as follows:
â€¢
Strength: A creature with no Strength is incapable
of exerting any physical force, either because it has
no physical form (like an incorporeal ghost) or simply
canâ€™t move (like a tree).
â€¢
Stamina: A creature with no Stamina has no physical
body (like a ghost) or is not a living being (such as a
robot or other construct). Creatures with no Stamina
suffer and recover from damage like inanimate ob-
jects (see Damaging Objects under the Damage

defenses apart from Toughness (and Fortitude, if
they are alive).
â€¢
Presence: Creatures without Presence are unable to
interact and immune to interaction skills. They have
no Will defense.
Lacking an ability is â€"10 power points; that is, it gives the
character an additional 10 power points to spend else-
where, similar to having a â€"5 rank in an ability, but with
different effects. MUTANTS & MASTERMINDS heroes cannot be
absent an ability without Gamemaster permission, as it can
have significant effects on the character and the game.
Absent abilities cannot be weakened (see the Weaken ef-
fect in the Powers chapter) or debilitated, since they are
not present at all in the first place!
Inanimate objects have no abilities other than their
Toughness. Animate, but nonliving, constructs such as ro-
bots or zombies have Strength, Agility, and Dexterity, and
may have ranks of Awareness and Presence (if aware of
their environment or capable of interaction), and Fighting
(if able to make close attacks). They may have Intellect (if
capable of independent thought), but have no Stamina
(since they are not living things). See Constructs in the
Gadgets & Gear chapter for more information.
effect). They are immune to fatigued and exhausted
conditions, but cannot exert extra effort. Creatures
with no Stamina are oftenâ€"but not necessarilyâ€"im-
mune to many of the other things affecting living be-
ings as well (see the Immunity effect in the Powers
chapter). They have no Fortitude defense.
â€¢
Dexterity: A creature with no Dexterity cannot manip-
ulate objects and hence cannot make physical attacks.
â€¢
Agility: A creature with no Agility is unable to move
its body under its own power and has no Dodge de-
fense.
â€¢
Fighting: A creature with no Fighting is incapable of
making any sort of close attack (but may still be able
to launch ranged attacks, if it has Dexterity).
â€¢
Intellect: A creature with no Intellect is an automa-
ton, lacking free will and operating entirely on simple
instinct or pre-programmed instructions. Anything
with no Intellect is immune to mental effects and in-
teraction skills and has no Will defense.
â€¢
Awareness: Anything with no Awareness is com-
pletely unaware and also has no Presence. It is an in-
animate object, not a creature. Objects are immune
to mental effects and interaction skills, and have no
```

---

## Derived Defense

Derived Defense is the family of five defensive values — Dodge, Parry, Fortitude, Toughness, and Will — each computed from a specific ability rank, plus the initiative modifier derived from Agility. This KA owns the base derivation formula (base defense = ability rank), the investment economy for raising defenses above base (1 power point per rank, subject to power level limits), the single exception to that economy (Toughness cannot be raised by direct power point spending — only through advantages and powers), the active-defense category (Dodge and Parry degrade under the vulnerable and defenseless conditions), the defense class formula (defense + 10 = DC to affect a target with an attack), and the resistance check usage (defense + d20 vs. effect DC). Initiative (Agility + Advantages + Power Modifiers) is defined here because it is derived from AGL; its Advantage and Power components are boundary inputs from other modules.

#### Decisions made
- The five named defenses are kept as distinct `### term` headings because each is based on a different ability, used in different check types, and has different investment rules (Toughness especially).
- `active defense` and `defense class` are included as found terms under this KA since they are defense-specific concepts defined in Ch3.
- `initiative` is placed here rather than in a separate KA because the initiative modifier is defined in the Defenses & Initiative section of Ch3 and is derived directly from AGL, making it part of the same derivation concern as defenses.
- Resistance checks as a mechanic are boundary to the Check Resolution module; this module defines the defense values used in those checks but does not own the resistance check mechanic itself.
- Ref deduplication applied: chunk_040 partial "Active Defenses section" appears first under `### Dodge` and is removed from `### Parry` and `### active defense` within this KA block.

### Dodge

#### Domain language
- Defense value based on Agility rank; covers reaction time, quickness, nimbleness, and coordination.
- Used to avoid ranged attacks and other hazards where reflexes and speed are important.
- Active defense: requires mobility and focus; halved (round up) when vulnerable; reduced to 0 when defenseless.
- Used as defense class (Dodge + 10) against ranged attacks.
- Used in Dodge resistance checks (e.g., reflexively avoid a triggered trap).
- Can be increased above the Agility base by spending 1 power point per rank, subject to power level limits.

#### Domain Sketch
- Derives its base value from the character's Agility rank at creation and recalculates whenever AGL changes.
- Acts as the primary defense against ranged attacks by supplying the Dodge defense class (Dodge + 10).
- Participates in Dodge resistance checks (defense + d20 vs effect DC) when the check is triggered.
- Degrades under condition effects: halved when vulnerable, zeroed when defenseless.
- Can be increased above the AGL base through power point investment, up to the power level cap.
- Invariant: Dodge cannot be negative; if AGL is absent, there is no Dodge defense.

#### References

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: DODGE section and Defense Rank paragraph.

```source
### Defenses & Initiative
Heroes face many hazards in their line of work, from attacks by villainous foes to traps and fiendish mind control. A
heroâ€™s defenses are abilities used to avoid such things, determining the difficulty to affect a hero with an attack, or to
make resistance checks against them. Each defense is based on a particular ability, modified by the heroâ€™s advantages
and powers. For more on defenses in general and how you use them, see Chapter 8.
DODGE
Dodge defense is based on Agility rank. It includes reac-
tion time, quickness, nimbleness, and overall coordina-
tion, used to avoid ranged attacks or other hazards where
reflexes and speed are important.

### Defense Rank
Your base defense ranks are equal to your ranks in their
associated abilities. You can increase your defenses above
the values granted by your ability ranks by spending pow-
er points: 1 power point grants you an additional rank in
a defense, up to the limits imposed by power level (see
Power Level on page 24).
Defense Cost =
1 power point per +1 rank
```

**Ref — Toughness Rank**
Source: context/rules/HeroesHandbook-rules__chunk_040.md
Locator: lines 2638-2688
Extract: partial
Part: Active Defenses section (vulnerable/defenseless effects on Dodge and Parry).

```source
### Active Defenses
Dodge and Parry defenses require a measure of action to
be fully effective. Limits on your mobility, focus, and reac-
tion time adversely affect them. If you are vulnerable, your
Dodge and Parry defense ranks are halved (divide their
normal values by 2 and round up), and if you are defense-
less, they are both reduced to 0!
```

---

### Parry

#### Domain language
- Defense value based on Fighting rank; represents countering, ducking, or evading close attacks.
- Active defense: halved (round up) when vulnerable; reduced to 0 when defenseless.
- Used as defense class (Parry + 10) for close attacks.
- Can be increased above the Fighting base by spending 1 power point per rank, subject to power level limits.

#### Domain Sketch
- Derives its base value from the character's Fighting rank and recalculates whenever FGT changes.
- Acts as the primary defense against close attacks by supplying the Parry defense class (Parry + 10).
- Degrades under condition effects: halved when vulnerable, zeroed when defenseless (same degradation rule as Dodge).
- Can be increased above the FGT base through power point investment, up to the power level cap.
- Invariant: Parry cannot be negative; the minimum after any degradation is 0.

#### References

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: PARRY section and Defense Rank paragraph.

```source
PARRY
Parry defense is based on Fighting. It is the ability to coun-
ter, duck, or otherwise evade a foeâ€™s attempts to strike you
in close combat through superior fighting ability.

### Defense Rank
Your base defense ranks are equal to your ranks in their
associated abilities. You can increase your defenses above
the values granted by your ability ranks by spending pow-
er points: 1 power point grants you an additional rank in
a defense, up to the limits imposed by power level.
```

*(Active Defenses ref deduplicated — first cited under `### Dodge` above.)*

---

### Fortitude

#### Domain language
- Defense value based on Stamina rank; measures health and resistance to threats like poison or disease.
- Incorporates constitution, ruggedness, metabolism, and immunity.
- Passive defense: always effective regardless of mobility restrictions.
- Used in Fortitude resistance checks against health-affecting effects (toxins, disease, dying).
- Can be increased above the Stamina base by spending 1 power point per rank.
- Creatures with no Stamina have no Fortitude defense.

#### Domain Sketch
- Derives its base value from the character's Stamina rank.
- Participates in resistance checks against health-affecting effects; used for the dying stabilization check (DC 15 per round).
- Passive defense: does not degrade under vulnerable or defenseless conditions.
- Can be increased above the STA base through power point investment.
- Invariant: creatures with no Stamina have no Fortitude defense — the derivation has no source.

#### References

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: FORTITUDE section and Defense Rank paragraph.

```source
FORTITUDE
Fortitude defense is based on Stamina and measures
health and resistance to threats like poison or disease. It
incorporates constitution, ruggedness, metabolism, and
immunity.

### Defense Rank
Your base defense ranks are equal to your ranks in their
associated abilities. You can increase your defenses above
the values granted by your ability ranks by spending pow-
er points: 1 power point grants you an additional rank in
a defense, up to the limits imposed by power level.
```

---

### Toughness

#### Domain language
- Defense value based on Stamina rank; measures resistance to direct damage and overall physical durability.
- Cannot be increased above the base Stamina rank by direct power point spending — only through advantages (e.g., Defensive Roll) and powers (e.g., Protection effect).
- This restriction reflects that greater-than-normal Toughness is virtually always a special ability.
- Used in Toughness resistance checks against damage.

#### Domain Sketch
- Derives its base value from the character's Stamina rank.
- Participates in resistance checks against damage — every attack that deals damage triggers a Toughness resistance check.
- Passive defense: does not degrade under vulnerable or defenseless conditions.
- Invariant: Toughness cannot be raised above the base Stamina rank through direct power point spending; only advantages and powers can exceed this base.

#### References

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: TOUGHNESS section.

```source
TOUGHNESS
Toughness defense is based on Stamina and is resistance
to direct damage or harm, and overall durability.
```

**Ref — Toughness Rank**
Source: context/rules/HeroesHandbook-rules__chunk_040.md
Locator: lines 2638-2688
Extract: partial
Part: Toughness Rank section (purchase restriction rule).

```source
### Toughness Rank
The exception is Toughness, which can only be increased
above your base Stamina rank using advantages and pow-
ers, not by direct spending of power points. This reflects that
greater-than-normal Toughness is virtually always some sort
of special ability. See the Advantages and Powers chapters
for various options for improving Toughness, notably the De-
fensive Roll advantage and the Protection effect.
```

---

### Will

#### Domain language
- Defense value based on Awareness rank; measures mental stability, level-headedness, determination, self-confidence, and willpower.
- Used to resist mental or spiritual attacks.
- Used as defense class (Will + 10) when an attack targets Will.
- Can be increased above the Awareness base by spending 1 power point per rank.
- Creatures with no Intellect or no Awareness/Presence have no Will defense.

#### Domain Sketch
- Derives its base value from the character's Awareness rank.
- Acts as both defense class (Will + 10) for mental attacks and resistance check base for effects that target mental stability.
- Passive defense: does not degrade under vulnerable or defenseless conditions.
- Can be increased above the AWE base through power point investment.
- Invariant: creatures with no Intellect or no Awareness/Presence have no Will defense.

#### References

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: WILL section and Defense Rank paragraph.

```source
WILL
Will defense is based on Awareness rank. It measures
mental stability, level-headedness, determination, self-
confidence, self-awareness, and willpower, used to resist
mental or spiritual attacks.

### Defense Rank
Your base defense ranks are equal to your ranks in their
associated abilities. You can increase your defenses above
the values granted by your ability ranks by spending pow-
er points: 1 power point grants you an additional rank in
a defense, up to the limits imposed by power level.
```

---

### defense

#### Domain language
- General term for the five defensive values (Dodge, Parry, Fortitude, Toughness, Will) used to resist or avoid effects.
- Each defense is based on a specific ability rank, modified by advantages and powers.
- Base defense rank equals the rank of the associated ability.
- Can be increased above base by spending 1 power point per rank, subject to power level limits (except Toughness).
- Serves two purposes: (1) defense class (defense + 10 = DC to affect a target with an attack); (2) resistance check (defense + d20 vs effect's DC).
- Active defenses (Dodge, Parry) require mobility and focus to be fully effective; passive defenses (Fortitude, Toughness, Will) are unaffected by mobility.

#### Domain Sketch
- Owns the base derivation rule: each defense's starting rank equals the associated ability rank, updated automatically when the ability changes.
- Applies the investment economy: player may spend 1 pp per +1 defense rank above base (except Toughness).
- Enforces the two-role contract for all five defenses: defense class for attack targeting (defense + 10 = DC) AND resistance check base (defense + d20 vs effect DC).
- Separates active (Dodge, Parry) from passive (Fortitude, Toughness, Will) for condition-effect interactions.
- Invariant: base defense rank always reflects the current ability rank; it updates in the same operation as the ability rank change.

#### References

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch3 Abilities"
topic: "Defenses & Initiative"
chunk_index: 39
line_range: "2596-2637"
---

### Defenses & Initiative
Heroes face many hazards in their line of work, from attacks by villainous foes to traps and fiendish mind control. A
heroâ€™s defenses are abilities used to avoid such things, determining the difficulty to affect a hero with an attack, or to
make resistance checks against them. Each defense is based on a particular ability, modified by the heroâ€™s advantages
and powers. For more on defenses in general and how you use them, see Chapter 8.
DODGE
Dodge defense is based on Agility rank. It includes reac-
tion time, quickness, nimbleness, and overall coordina-
tion, used to avoid ranged attacks or other hazards where
reflexes and speed are important.
FORTITUDE
Fortitude defense is based on Stamina and measures
health and resistance to threats like poison or disease. It
incorporates constitution, ruggedness, metabolism, and
immunity.
PARRY
Parry defense is based on Fighting. It is the ability to coun-
ter, duck, or otherwise evade a foeâ€™s attempts to strike you
in close combat through superior fighting ability.
TOUGHNESS
Toughness defense is based on Stamina and is resistance
to direct damage or harm, and overall durability.
WILL
Will defense is based on Awareness rank. It measures
mental stability, level-headedness, determination, self-
confidence, self-awareness, and willpower, used to resist
mental or spiritual attacks.

### Defense Rank
Your base defense ranks are equal to your ranks in their
associated abilities. You can increase your defenses above
the values granted by your ability ranks by spending pow-
er points: 1 power point grants you an additional rank in
a defense, up to the limits imposed by power level (see
Power Level on page 24).
Defense Cost =
1 power point per +1 rank
With the Enhanced Trait effect (see the Powers chapter)
you can also improve your defenses with powers at the
same cost, 1 point per rank.
```

**Ref — Toughness Rank**
Source: context/rules/HeroesHandbook-rules__chunk_040.md
Locator: lines 2638-2688
Extract: whole

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch3 Abilities"
topic: "Toughness Rank"
chunk_index: 40
line_range: "2638-2688"
---

### Toughness Rank
The exception is Toughness, which can only be increased
above your base Stamina rank using advantages and pow-
ers, not by direct spending of power points. This reflects that
greater-than-normal Toughness is virtually always some sort
of special ability. See the Advantages and Powers chapters
for various options for improving Toughness, notably the De-
fensive Roll advantage and the Protection effect.

### Active Defenses
Dodge and Parry defenses require a measure of action to
be fully effective. Limits on your mobility, focus, and reac-
tion time adversely affect them. If you are vulnerable, your
Dodge and Parry defense ranks are halved (divide their
normal values by 2 and round up), and if you are defense-
less, they are both reduced to 0!

### Defense Class
One use of defenses is determining a defense class, or
the difficulty class to affect a target with a particular at-
tack. This is the appropriate defense, plus 10, just like a
routine check (indeed, it is essentially a measure of the
characterâ€™s â€œroutineâ€ defense). So hitting a character with
a ranged attack goes against Dodge defense, giving the
attack a DC of (Dodge + 10). Similarly, affecting someone
with a mental power goes against Will defense, with a DC
of (Will + 10), and so forth. This is referred to as â€œtargetingâ€
a defense, such as â€œtargets Dodgeâ€ or â€œtargets Willâ€.
The main defense class traits are Dodge, Parry, and Will.

### Resistance Checks
Defenses are also used to measure the ability to over-
come certain effects, involving a resistance check of the
defense plus a die roll against a difficulty class determined
by the effect or hazard. So you might make a Fortitude re-
sistance check for your hero to overcome a toxin, for ex-
ample, or a Dodge resistance check to avoid a trap just as
it is triggered, and so on. This is referred to as â€œresisting,â€
such as â€œresisted by Fortitudeâ€ or â€œresisted by Dodgeâ€.
The main resistance check traits are Dodge, Fortitude,
Toughness, and Will.
INITIATIVE
When things start happening quickly, MUTANTS & MASTER-
MINDS characters use their initiative bonuses to determine
who goes first. Each character involved in a conflict makes
a check of d20 + initiative modifier, which is:
Initiative Modifier = Agility + Advantages
(Improved Initiative) + Power Modifiers
Characters then act in initiative order, from highest to low-
est. For details see the Action & Adventure chapter.
```

---

### active defense

*(Found term — discovered in source material; not in original Core terms list.)*

#### Domain language
- Category of defense that requires mobility, focus, and reaction time to be fully effective.
- Comprises Dodge and Parry — the two ability-derived defenses that degrade under condition effects.
- When vulnerable: active defense ranks are halved (divide normal value by 2, round up).
- When defenseless: active defense ranks are reduced to 0.
- Contrasts with passive defenses (Fortitude, Toughness, Will), which are unaffected by mobility restrictions.

#### Domain Sketch
- Classifies Dodge and Parry as the defenses requiring ongoing engagement to be fully effective.
- Applies the halving rule (round up) to both Dodge and Parry simultaneously when the character is vulnerable.
- Applies the zeroing rule to both simultaneously when the character is defenseless.
- Invariant: active defense rank can never fall below 0 regardless of condition effects.

*(Active Defenses ref deduplicated — first cited under `### Dodge` above.)*

---

### defense class

*(Found term — discovered in source material; not in original Core terms list.)*

#### Domain language
- The difficulty class for a given attack to affect a target: defense rank + 10.
- Represents the target's "routine defense" (equivalent to a routine check).
- Primary defense class traits: Dodge (for ranged attacks), Parry (for close attacks), and Will (for mental attacks).
- An attack "targets" a defense when it uses that defense's class as its DC.

#### Domain Sketch
- Computes the attack's DC by adding 10 to the appropriate defense rank.
- Applied to Dodge (ranged attacks), Parry (close attacks), and Will (mental attacks) as the primary targeting defenses.
- Changes whenever the underlying defense rank changes — it is always current with the current ability rank.
- Invariant: defense class is always defense rank + 10; there are no other modifiers to the base formula at this level.

#### References

**Ref — Toughness Rank**
Source: context/rules/HeroesHandbook-rules__chunk_040.md
Locator: lines 2638-2688
Extract: partial
Part: Defense Class section.

```source
### Defense Class
One use of defenses is determining a defense class, or
the difficulty class to affect a target with a particular at-
tack. This is the appropriate defense, plus 10, just like a
routine check (indeed, it is essentially a measure of the
characterâ€™s â€œroutineâ€ defense). So hitting a character with
a ranged attack goes against Dodge defense, giving the
attack a DC of (Dodge + 10). Similarly, affecting someone
with a mental power goes against Will defense, with a DC
of (Will + 10), and so forth. This is referred to as â€œtargetingâ€
a defense, such as â€œtargets Dodgeâ€ or â€œtargets Willâ€.
The main defense class traits are Dodge, Parry, and Will.
```

---

### initiative

*(Found term — discovered in source material; not in original Core terms list.)*

#### Domain language
- Derived combat-readiness value computed as: Agility rank + Advantages (Improved Initiative) + Power Modifiers.
- Determines action order at the start of a conflict: characters act from highest to lowest initiative modifier.
- Defined in Ch3 Abilities alongside the five defenses, grounding it in the ability module.
- Depends on the Agility ability rank for its base value; the Advantage and Power components are boundary contributions.

#### Domain Sketch
- Computes as the sum of AGL rank plus any Improved Initiative advantage bonus plus any power modifier.
- Updates automatically whenever the AGL rank changes, since AGL is the only ability-module-owned component.
- Invariant: if AGL is absent, the Agility component is 0; the initiative modifier equals only Advantage and Power contributions.

#### References

**Ref — Toughness Rank**
Source: context/rules/HeroesHandbook-rules__chunk_040.md
Locator: lines 2638-2688
Extract: partial
Part: INITIATIVE section.

```source
INITIATIVE
When things start happening quickly, MUTANTS & MASTER-
MINDS characters use their initiative bonuses to determine
who goes first. Each character involved in a conflict makes
a check of d20 + initiative modifier, which is:
Initiative Modifier = Agility + Advantages
(Improved Initiative) + Power Modifiers
Characters then act in initiative order, from highest to low-
est. For details see the Action & Adventure chapter.
```

---

## Debilitated Ability

Debilitated Ability is the severe-degradation state triggered when any ability rank drops below −5 through game effects, almost always a power effect targeting the character's abilities. It owns the floor enforcement rule (no further rank reduction once debilitated — the debilitated threshold cannot be crossed again), and the four distinct condition sets applied per ability group: physical-movement abilities (STR, AGL, DEX) cause collapse — defenseless, immobilized, and stunned while remaining conscious; Stamina causes the dying condition with an additional −5 Fortitude penalty; Fighting causes the dazed and defenseless state with loss of close attack capability; mental abilities (INT, AWE, PRE) cause the unaware condition that persists until the rank is restored to at least −5. Recovery from debilitation is not owned by this KA — it depends on the power or healing effect that reduced the rank restoring it.

#### Decisions made
- Debilitated Ability passes the independence test: it has distinct rules (floor enforcement, four different condition sets, recovery dependency) separate from the normal rank mechanic.
- Debilitated Ability passes the module-fit test: its rules are defined in Ch3 Abilities within this module's scope.
- Kept as its own KA rather than a sub-concept under Ability Score because debilitation triggers a fundamentally different game state (conditions applied, floor enforced) with its own per-ability effect table.
- STR, AGL, and DEX debilitation share the same collapse outcome (defenseless + immobilized + stunned) — grouped together in the domain language because the source treats them identically.
- INT, AWE, and PRE debilitation share the same unaware outcome — grouped similarly.
- STA and FGT have unique debilitation effects and are described individually.

### debilitated

#### Domain language
- State reached when an ability rank drops below −5 for any reason (typically caused by a power effect).
- Ability ranks cannot be lowered any further once debilitated; this threshold is the floor for each ability.
- Per-ability debilitation effects:
  - STR, AGL, or DEX debilitated: hero collapses — defenseless, immobilized, and stunned (but still conscious and aware).
  - STA debilitated: hero is dying, with an additional −5 modifier on Fortitude checks to avoid death.
  - FGT debilitated: hero is dazed and defenseless; cannot make close attacks.
  - INT, AWE, or PRE debilitated: hero is unaware and remains so until the ability is restored to at least −5.

#### Domain Sketch
- Triggers when an ability rank is reduced below −5 by a game effect, applying the appropriate per-ability condition set immediately.
- Enforces the floor: blocks any further rank reduction once the debilitated threshold is reached for that ability.
- Tracks recovery: when the ability rank rises back to −5 or above (typically when the effect causing the reduction ends), the debilitated state clears and conditions are removed.
- Invariant: ability ranks cannot go lower than the debilitated threshold; the floor is absolute and cannot be overridden.
- Invariant: the specific conditions applied depend on which ability is debilitated — they are not interchangeable across the four groups.
- Invariant: recovery from debilitation requires the rank to reach at least −5; a rank of −6 or lower maintains the debilitated state.

#### References

**Ref — Enhanced Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_037.md
Locator: lines 2465-2524
Extract: partial
Part: "Debilitated Abilities" section.

```source
---
source: HeroesHandbook-rules.md
chapter: "Ch3 Abilities"
topic: "Enhanced Abilities"
chunk_index: 37
line_range: "2465-2524"
---

### Enhanced Abilities
Some ability ranksâ€"or portions of themâ€"may be ac-
quired as Enhanced Traits, as described in the Powers
chapter. Enhanced Abilities are superhuman powers rath-
er than natural. The key differences between Enhanced
Abilities and normal ability ranks are Enhanced Abilities
can be nullified (normal abilities cannot, see Nullify, page
173) and Enhanced Abilities can have power modifiers
and be used for power stunts with extra effort (normal
abilities cannot, see Extra Effort, page 19).
Enhanced Abilities and normal abilities have the same
cost (2 power points per +1 ability rank). The player de-
cides if a characterâ€™s ability rank is normal or enhanced
and, if it is enhanced, how much of it is enhanced.

### The Abilities
Here are descriptions of the eight abilities and what they represent.

### Altering Abilities
Over the course of play, your heroâ€™s ability ranks may
change for the following reasons:
â€¢
Some power effects raise or lower ability ranks (see
the Powers chapter).
â€¢
You can improve ability ranks permanently by spend-
ing earned power points on them, but you cannot
increase an ability rank above the limits set by the
seriesâ€™ power level (see Power Level, page 24).
Whenever an ability rank changes, all traits associated
with the ability change as well. So if you increase your
characterâ€™s Agility, his Agility-based skills and Dodge de-
fense also increase. Likewise, if the heroâ€™s Agility bonus
decreases, his Agility-based skills and Dodge suffer.

### Debilitated Abilities
If one of your heroâ€™s ability ranks drops below â€"5 for any
reason, that ability is said to be debilitated and the char-
acter suffers more serious effects than just a penalty to
certain traits and rolls, as follows:
â€¢
Debilitated Strength, Agility, or Dexterity means
the hero collapses: defenseless, immobilized, and
stunned (although still conscious and aware).
â€¢
Debilitated Stamina means the hero is dying, and
suffers a â€"5 modifier on Fortitude checks to avoid
death on top of it.
â€¢
Debilitated Fighting means the hero is dazed and
defenseless, and cannot make close attacks.
â€¢
Debilitated Intellect, Awareness, or Presence
means the hero is unaware and remains so until re-
stored to at least a â€"5 rank in the ability.
Debilitated ability ranks usually result from a power af-
fecting your character. Ability ranks cannot be lowered
any further once they are debilitated.
```

---

# Boundary Domain

## power point

Owned by: Character Construction

#### Domain language
- Currency used to purchase ability ranks (2 pp per +1 rank) and defense ranks above base (1 pp per +1 rank).
- Gained by reducing ability ranks below 0 (2 pp per −1 rank) or by lacking an ability entirely (10 pp).

#### References

**Ref — Ch3 Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_035.md
Locator: lines 2298-2362
Extract: partial
Part: "Buying Ability Ranks" and "Reducing Abilities" sections.

```source
### Buying Ability Ranks
You choose your heroâ€™s ability ranks by spending power
points on them. Increasing an ability rank by 1 costs 2
power points, so putting two points into Strength, for ex-
ample, raises it from 0 to 1.

### Reducing Abilities
You can also lower one or more of your characterâ€™s ability
ranks from the starting value of 0. Each rank you lower an
ability gives you an additional two power points to spend
elsewhere. You cannot lower an ability rank below â€"5,
which is itself a serious deficiency.
Ability Cost = 2 power points per +1 to an ability rank.
Gain 2 bonus power points per -1 to an ability rank.
```

---

## power level

Owned by: Character Construction

#### Domain language
- Sets the upper limit on ability rank improvements via earned power points (rank cannot be raised above the series' power level).
- Also constrains the maximum defense rank purchasable above the ability base.

#### References

**Ref — Enhanced Abilities**
Source: context/rules/HeroesHandbook-rules__chunk_037.md
Locator: lines 2465-2524
Extract: partial
Part: "Altering Abilities" section — power level cap on ability rank increases.

```source
### Altering Abilities
Over the course of play, your heroâ€™s ability ranks may
change for the following reasons:
â€¢
Some power effects raise or lower ability ranks (see
the Powers chapter).
â€¢
You can improve ability ranks permanently by spend-
ing earned power points on them, but you cannot
increase an ability rank above the limits set by the
seriesâ€™ power level (see Power Level, page 24).
Whenever an ability rank changes, all traits associated
with the ability change as well.
```

**Ref — Defenses & Initiative**
Source: context/rules/HeroesHandbook-rules__chunk_039.md
Locator: lines 2596-2637
Extract: partial
Part: Defense Rank section — power level cap on defense rank increases.

```source
### Defense Rank
Your base defense ranks are equal to your ranks in their
associated abilities. You can increase your defenses above
the values granted by your ability ranks by spending pow-
er points: 1 power point grants you an additional rank in
a defense, up to the limits imposed by power level (see
Power Level on page 24).
Defense Cost =
1 power point per +1 rank
```
