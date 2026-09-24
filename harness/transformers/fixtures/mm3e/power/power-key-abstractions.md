---
state: key-abstractions
---

# Module: [Power]

Scope: Power effects (Affliction through Weaken), power types, action/range/duration defaults, Extras, Flaws, Descriptors, and modifier math.

**Core terms**:
- effect
- power
- power type
- base cost
- cost per rank
- flat modifier
- extra
- flaw
- Affliction
- Blast (Damage, Ranged)
- Burrowing
- Communication
- Comprehend
- Concealment
- Create
- Damage
- Deflect
- Elongation
- Enhanced Trait
- Environment
- Feature
- Flight
- Growth
- Healing
- Illusion
- Immortality
- Immunity
- Insubstantial
- Leaping
- Luck Control
- Mind Reading
- Move Object
- Movement
- Nullify
- Protection
- Quickness
- Regeneration
- Remote Sensing
- Senses
- Shrinking
- Speed
- Summon
- Swimming
- Teleport
- Transform
- Variable
- Weaken
- Accurate
- Area
- Multiattack
- Penetrating
- Activation
- Check Required
- Limited
- Removable
- descriptor
- origin descriptor
- source descriptor
- Array
- Alternate Effect
- Dynamic Alternate Effect

---

# Core Domain

## Key Abstractions

### Effect Framework

The Effect Framework is the foundational architecture of every superhuman capability in the game. An **effect** is the atomic rules-defined unit: it names a capability, specifies its type (Attack, Control, Defense, General, Movement, Sensory), and ships with default action, range, duration, and cost per rank. A **power** is the player-facing wrapper a character acquires — one or more effects combined, named, and described using **descriptors** that determine what Nullify counters, what Immunity blocks, and how the fictional world reacts. **Power type** is the category label on every effect that tells the system which general rules apply. Together these three concepts answer the most important design question: what does this capability do and how is it categorized?

The Effect Framework owns the concept of "what an effect is," not the pricing (that is Effect Cost's concern) nor the individual catalog of specific effects (those are the effect-type KAs). Every other abstraction in this module serves the Effect Framework — modifiers change how effects behave, KA groupings catalog what kinds of effects exist, and descriptors connect fictional fiction to mechanical rules. The invariant: every power a character possesses must be built from one or more named effects; no capability exists outside this framework.

#### effect

#### Domain Language

- An effect is the named, rules-defined game unit that produces a specific superheroic capability — the atomic building block from which all powers are constructed.
- Every effect has five fixed properties at acquisition: type, action, range, duration, and cost per rank.
- Effects are acquired in ranks; higher rank means greater scale, distance, or intensity.
- The effect's stat block defaults can be changed by applying extras and flaws.
- Players name their powers freely; the effect is the underlying mechanical structure the rules operate on.

#### References

**Ref — Ch6 Powers**
Source: context/rules/HeroesHandbook-rules__chunk_082.md
Locator: lines 5118-5192
Extract: whole

```source
## CHAPTER 6: POWERS

### Power Costs
Power effects are acquired in ranks, like ranks for other
traits. The more ranks an effect has, the greater its effect.
Each effect of a power has a standard cost per rank.

### Modifiers
Modifiers change how an effect works, making it more
effective (an extra) or less effective (a flaw). Modifiers
have ranks, just like other traits. Extras increase a power's
cost while flaws decrease it. Some modifiers increase an
effect's cost per rank, others apply an unchanging cost to
the power's total; these are called flat modifiers. For more
information see Modifiers, on page 187.
The final cost of a power is determined by base effect
costs, modified by extras and flaws, multiplied by the
power's rank, with flat modifiers applied to the total cost.
Power Cost = ((base effect costs + extras -
flaws) x rank) + flat modifiers
```

**Ref — Acquiring Powers**
Source: context/rules/HeroesHandbook-rules__chunk_083.md
Locator: lines 5193-5261
Extract: whole

```source
### Acquiring Powers
Players spend power points on various powers for their heroes, like acquiring skills or other traits. A power is made up of
one or more effects, possibly with different modifiers, which increase or decrease the cost of the effects.
Effects can be used to create any number of different powers. A hero with the Concealment effect could use
it to create a power called Blending, Blur, Cloak, Invisibility, Shadowmeld, or anything else appropriate to the character.
Another way to think of it is that this book is filled with effects, but your character sheet is filled with powers.
```

---

#### power

#### Domain Language

- A power is the player-facing, named combination of one or more effects that appears on a character sheet.
- Powers cost power points equal to the sum of each included effect's (cost per rank × rank) plus any flat modifiers.
- Powers must have at least one descriptor; descriptors are assigned at acquisition.
- The GM approves all powers before play; powers interact with settings, plots, and genre conventions.

#### References

**Ref — Ch6 Powers**
Source: context/rules/HeroesHandbook-rules__chunk_082.md
Locator: lines 5118-5192
Extract: whole

```source
### Power Descriptors
The rules in this chapter explain what the various powers do,
that is, what their game effects are, but it is left up to the player
and Gamemaster to apply descriptors to define exactly
what a power is and what it looks like to observers beyond just
a collection of game effects.
A power's descriptors are primarily for color. It's more interesting
and clear to say a hero has a "Flame Blast" or "Lightning
Bolt" power than a generic "Damage effect."
```

---

#### power type

#### Domain Language

- Power type is the category label assigned to each effect: Attack, Control, Defense, General, Movement, Sensory.
- Attack type effects require an attack check and allow targets a resistance check.
- Defense type effects are passive or reactive; most are permanent.
- Control type effects manipulate the environment, objects, or characters.
- General type effects provide utility, enhancement, or transformation.
- Movement type effects grant locomotion modes.
- Sensory type effects grant, enhance, or alter perception capabilities.

#### References

**Ref — Effect Types**
Source: context/rules/HeroesHandbook-rules__chunk_084.md
Locator: lines 5262-5314
Extract: whole

```source
### Effect Types
Power effects fall into certain categories or effect types. Effects of the same type follow similar rules.
**Attack**
Attack effects are used offensively in combat. They require an attack check and damage, hinder, or otherwise
harm their target in some way. Attack effects require a standard action to use.
**Control**
Control effects grant the user influence over something, from the environment to the ability to move objects.
**Defense**
Defense effects protect in various ways, typically offering a bonus to resistance checks, or granting outright immunity.
Most defense effects work only on the user and are subtle and permanent, functioning at all times.
**General**
General effects don't fit into any other particular category.
### Movement
Movement effects allow characters to get around in various ways.
**Sensory**
Sensory effects enhance or alter the senses.
```

---

#### descriptor

#### Domain Language

- A descriptor is a free label attached to a power that identifies its nature, medium, source, or results in thematic and mechanical terms.
- Descriptors cost no power points; they are assigned at acquisition and may not be changed without GM approval.
- Descriptors determine what Nullify counters, what Immunity blocks, and how narrative effects interact with the power.
- At minimum every power must have at least one descriptor.

#### References

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_155.md — Types of Descriptors section covering origin, source, medium, and result descriptor categories with examples]
```

**Ref — Applying Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_156.md
Locator: lines 11447-11497
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_156.md — Applying Descriptors guidance]
```

---

#### origin descriptor

#### Domain Language

- An origin descriptor identifies how a character came to have their powers — the narrative source of the character's abilities.
- Common origin descriptors: Accidental, Bestowed, Invented, Mutant, Training.
- Origin descriptors rarely have direct mechanical effects but govern narrative interactions.

#### References

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_155.md — origin descriptor section]
```

---

#### source descriptor

#### Domain Language

- A source descriptor identifies the energy or force that a power draws upon to function.
- Common source descriptors: Biological, Cosmic, Divine, Extradimensional, Magical, Moral, Psionic, Technological.
- Source descriptors have mechanical significance: Nullify targeting "magical effects" counters all powers with a Magical source.

#### References

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_155.md — source descriptor section]
```

**Ref — Changing Descriptors In Play**
Source: context/rules/HeroesHandbook-rules__chunk_157.md
Locator: lines 11498-11554
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_157.md — rules for changing descriptors during play]
```

---

#### Decisions made

- **effect vs power**: effect is the mechanical unit (what the rules define); power is the player label (what the character sheet shows). Both are core terms because the module uses both concepts in distinct rules contexts. Independence test: effect and power are independently meaningful — "Damage effect" describes a rules construct; "Lightning Bolt power" describes a character capability.
- **descriptor merged into Effect Framework KA**: descriptor, origin descriptor, and source descriptor are not independently meaningful outside the context of what a power or effect *is*. They qualify the effect/power identity rather than owning separate mechanical behavior. Module-fit test: all descriptor rules live in this module (Ch6 Powers).
- **power type stays as term under Effect Framework**: power type is an attribute of every effect, not a standalone abstraction. Independence test: power type has no meaning except as a classification property of an effect.

---

### Effect Cost

The Effect Cost abstraction owns the pricing model that converts a raw effect into power points spent on the character sheet. **Base cost** is the printed starting value per rank for each specific effect — it represents the inherent worth of the capability at rank 1. **Cost per rank** is the modified rate after extras raise it and flaws lower it, and it is the key figure used in the multiplication: cost per rank × rank = the bulk of the power's price. **Flat modifier** is the final adjustment applied to the total (not the per-rank figure), used for extras and flaws that have fixed-point values rather than rank-scaled ones.

The Effect Cost abstraction is the single source of truth for how much power costs. It owns the formula: Power Cost = ((base cost + per-rank extras − per-rank flaws) × rank) + flat modifier adjustments. The Modifier KA governs what extras and flaws *do*; Effect Cost governs how they *change the price*. The invariants: cost per rank cannot drop below 1 pp/rank regardless of flaws; total power cost cannot be reduced below 1 pp total; flat modifiers apply after the per-rank × rank calculation, not before.

#### base cost

#### Domain Language

- Base cost is the unmodified power-point cost per rank for an effect as printed in the rules.
- Base costs vary: 1 pp/rank for simple effects (Damage), up to 7 pp/rank for versatile effects (Variable).
- Modifier math starts from base cost: extras add to it, flaws subtract from it.

#### References

**Ref — Acquiring Powers**
Source: context/rules/HeroesHandbook-rules__chunk_083.md
Locator: lines 5193-5261
Extract: whole

```source
### Acquiring Powers
Players spend power points on various powers for their heroes, like acquiring skills or other traits. A power is made up of
one or more effects, possibly with different modifiers, which increase or decrease the cost of the effects.
```

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

```source
### Applying Modifiers
An extra increases an effect's cost per rank by a set amount
(usually 1 point) while a flaw decreases the effect's cost
per rank by a set amount (usually 1 point as well). To determine
the effect's final cost per rank, take the base cost,
add up all the extras, and subtract all of the flaws.
Modified Cost = base effect cost + extras - flaws
```

---

#### cost per rank

#### Domain Language

- Cost per rank = base cost + (sum of per-rank extras) − (sum of per-rank flaws).
- Must be at minimum 1 pp/rank regardless of flaws applied.
- Total effect cost = (cost per rank × ranks) + flat modifiers.

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

```source
### Applying Modifiers
An extra increases an effect's cost per rank by a set amount
(usually 1 point) while a flaw decreases the effect's cost
per rank by a set amount (usually 1 point as well). To determine
the effect's final cost per rank, take the base cost,
add up all the extras, and subtract all of the flaws.
Modified Cost = base effect cost + extras - flaws

### Fractional Costs
If total flaws reduce an effect's cost per rank to less than 1
power point, each additional -1 to cost per rank beyond
that adds to the number of ranks of the effect you get by
spending 1 power point on a 1-to-1 basis.
```

---

#### flat modifier

#### Domain Language

- A flat modifier is applied to the final total cost of a power (after cost per rank × rank) — a fixed-point adjustment, not rank-scaled.
- Flat extras add points to the total; flat flaws subtract points.
- Flat modifiers apply after cost per rank is calculated; they can push total cost below the per-rank floor.

#### References

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

```source
### Flat-Value Modifiers
Some modifiers, rather than increasing or decreasing an effect's cost per rank, have a flat value in power points, noted
as flat in the modifier's header. For example, the Subtle extra
costs only 1 or 2 points, depending on how subtle the effect
is. Likewise, the Activation flaw has a flat value of -1 or -2
points, depending on how long the power takes to activate.
Flat-value modifiers are applied to the final cost of an effect,
after its cost per rank and total cost for its number of ranks
is determined.
modified cost + flat extra value - flat flaw value
A flat-value flaw cannot reduce an effect or power's final
cost below 1 power point.
```

---

#### Decisions made

- **base cost vs cost per rank**: Both are distinct, independently meaningful concepts with different roles in the formula. Base cost is immutable (set at design time); cost per rank is computed (changes with modifiers). Keeping both terms prevents the common error of treating them as equivalent.
- **flat modifier placed in Effect Cost, not Modifier KA**: Flat modifier is fundamentally a pricing mechanism — it adjusts the final cost total. Modifier KA is about what modifiers *do* (change behavior); Effect Cost is about what they *cost*. The distinction matters when explaining the formula order.

---

### Modifier

A Modifier is any rule element attached to an effect that changes how it works and adjusts its price. **Extras** make effects more capable — they can expand action type, extend range, increase duration, add properties, or improve the effect in other ways; each per-rank extra raises cost per rank, while each flat extra adds a fixed amount to the total. **Flaws** make effects less capable — they restrict applicability, reduce action type, narrow range, or impose conditions; per-rank flaws reduce cost per rank, flat flaws reduce the total. The specific modifiers — **Accurate**, **Area**, **Multiattack**, **Penetrating** (extras) and **Activation**, **Check Required**, **Limited**, **Removable** (flaws) — are the most commonly encountered and have their own rules sections.

The Modifier KA is the gateway through which all customization of effects flows. It does not own any specific effect — those belong to the effect-type KAs. What it owns is the concept of how any effect can be made more or less powerful and the specific common modifier catalog. The invariant: an extra must grant a genuine capability improvement; a flaw must impose a genuine limitation reducing utility by approximately half or more. Cosmetic changes are descriptors, not modifiers.

#### extra

#### Domain Language

- An extra enhances an effect beyond its default behavior — broadens action type, extends range, adds properties.
- Per-rank extras add their value (usually +1) to base cost to raise cost per rank.
- Flat extras add a fixed point amount to the final total cost.
- Any effect can receive any extra as long as the effect doesn't already have that property.

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

```source
### Applying Modifiers
An extra increases an effect's cost per rank by a set amount
(usually 1 point) while a flaw decreases the effect's cost
per rank by a set amount (usually 1 point as well). To determine
the effect's final cost per rank, take the base cost,
add up all the extras, and subtract all of the flaws.
Modified Cost = base effect cost + extras - flaws
```

---

#### flaw

#### Domain Language

- A flaw limits an effect below its default behavior — restricts action type, reduces range, narrows applicability, or imposes conditions.
- Per-rank flaws subtract their value (usually −1) from base cost to lower cost per rank.
- Cost per rank cannot drop below 1 pp/rank no matter how many flaws are applied.
- Flaws must represent genuine limitations — the effect must actually be restricted about half or more of the time.

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

```source
### Applying Modifiers
An extra increases an effect's cost per rank by a set amount
(usually 1 point) while a flaw decreases the effect's cost
per rank by a set amount (usually 1 point as well). To determine
the effect's final cost per rank, take the base cost,
add up all the extras, and subtract all of the flaws.
Modified Cost = base effect cost + extras - flaws
```

---

#### Accurate

#### Domain Language

- Accurate is a flat extra; cost 1 flat point per +2 attack bonus (1 point per rank of bonus).
- Improves attack check rolls with that specific effect only.
- The attack bonus from Accurate cannot push total attack bonus beyond PL × 2.

#### References

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

```source
### Extras
ACCURATE
FLAT • 1 POINT PER RANK
An effect with this extra is especially accurate; you get +2
per Accurate rank to attack checks made with it. The power
level limits maximum attack bonus with any given effect.
```

---

#### Area

#### Domain Language

- Area is a per-rank extra; cost +1 per rank.
- Removes the need for an attack check; targets in the area make a Dodge resistance check (DC 10 + effect rank).
- Area shapes: Burst, Cloud, Cone, Cylinder, Line, Perception, Shapeable.
- Success on the Dodge check reduces effect rank by half.

#### References

**Ref — Affects Insubstantial**
Source: context/rules/HeroesHandbook-rules__chunk_142.md
Locator: lines 9790-9998
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_142.md covering Area extra and Affects Insubstantial]
```

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

```source
AREA
+1 COST PER RANK
This extra allows an effect that normally works on a single
target to affect an area. No attack check is needed; the
effect simply fills the designated area, based on the type
of modifier. Potential targets in the area are permitted
a Dodge resistance check (DC 10 + effect rank) to avoid
some of the effect. A successful resistance check
reduces the Area effect to half its normal rank against that
target (round down, minimum of 1 rank).
SHAPE
Choose one of the following options:
• Burst: The effect fills a sphere with a 30-foot radius (distance rank 0).
• Cloud: The effect fills a sphere with a 15-foot radius (distance rank -1) that lingers for one round.
• Cone: The effect fills a cone with a length, width, and height of 60 feet (distance rank 1).
• Cylinder: The effect fills a cylinder 30 feet in radius and height (distance rank 0).
• Line: The effect fills a path 6 feet wide and 30 feet long.
• Perception: The effect works on anyone able to perceive the target point.
• Shapeable: The effect fills a volume of 30 cubic feet (volume rank 5).
```

---

#### Multiattack

#### Domain Language

- Multiattack is a per-rank extra; cost +1 per rank.
- Against a single target: +2 to effect DC at 2 degrees of attack success, +5 at 3+ degrees.
- Against multiple targets: one attack roll with penalty equal to number of targets; each target whose Dodge is exceeded is hit.

#### References

**Ref — Single Target**
Source: context/rules/HeroesHandbook-rules__chunk_146.md
Locator: lines 10453-10574
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_146.md covering Multiattack extra]
```

---

#### Penetrating

#### Domain Language

- Penetrating is a flat extra; cost 1 flat point per rank of Penetrating.
- Overcomes Impervious resistance to degree equal to the Penetrating rank.
- Target with Impervious Toughness must resist damage rank equal to Penetrating rank even if normally blocked.

#### References

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

```source
### Flat-Value Modifiers
Some modifiers have a flat value in power points, noted
as flat in the modifier's header.
```

---

#### Activation

#### Domain Language

- Activation is a flat flaw; cost −1 (move action activation) or −2 (standard action activation).
- Applies to the entire power — all effects require the activation first.
- If Nullified or deactivated, the character must spend the activation action again.

#### References

**Ref — Activation And Permanent Effects**
Source: context/rules/HeroesHandbook-rules__chunk_149.md
Locator: lines 10716-10775
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_149.md covering Activation flaw]
```

---

#### Check Required

#### Domain Language

- Check Required is a flat flaw; cost −1 per rank of the effect.
- Must succeed on a skill or ability check (DC 10 + extra ranks) before the effect activates.
- Natural 1 always fails; on success, gain 1 effective rank per point exceeding the DC.

#### References

**Ref — Check Examples**
Source: context/rules/HeroesHandbook-rules__chunk_150.md
Locator: lines 10776-10941
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_150.md covering Check Required flaw]
```

---

#### Limited

#### Domain Language

- Limited is a per-rank flaw; cost −1 per rank.
- Effect works only under certain circumstances, against certain targets, or in certain conditions.
- Limitation must reduce utility to approximately half or less; GM determines qualification.

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

```source
### Applying Modifiers
An extra increases an effect's cost per rank by a set amount
(usually 1 point) while a flaw decreases the effect's cost
per rank by a set amount (usually 1 point as well).
```

---

#### Removable

#### Domain Language

- Removable is a flat flaw; cost −1 per 5 points of final power cost (or −2 if easily removable).
- Represents a power built into a device that can be taken from the character.
- The device can be taken when the character is both stunned and defenseless, or via disarm/grab.
- Removable applies to the entire power.

#### References

**Ref — Removable And Damage**
Source: context/rules/HeroesHandbook-rules__chunk_153.md
Locator: lines 11060-11137
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_153.md covering Removable flaw and device damage rules]
```

---

#### Decisions made

- **Specific modifiers (Accurate, Area, Multiattack, Penetrating, Activation, Check Required, Limited, Removable) grouped under Modifier KA**: These modifiers are the most commonly encountered and are worth naming explicitly in the model. They are not separate KAs — they are instances of the modifier concept, not independent abstractions. Independence test: none of these have meaning outside the context of modifying an effect.
- **Other modifiers (Increased Duration, Extended Range, Increased Action, Side Effect, Secondary Effect, etc.) not included as terms**: These are addressed in source refs but not promoted to core terms because the partition file did not include them. Context gap: the partition may under-represent the full modifier catalog; this is noted in domain-sketch.
- **extra and flaw as separate terms despite being a pair**: They have distinct mathematical roles (+ vs −) and distinct mechanical rules (extras broaden; flaws restrict). Merging them would hide this distinction.

---

### Attack Effect

An Attack Effect is any power effect whose primary purpose is to cause direct harm, impose conditions, or otherwise damage or disable an opponent through a direct confrontation requiring an attack check and allowing a resistance check. The Attack Effect KA groups together the six core effects that define offensive superhuman power: **Affliction** (condition imposition), **Blast** (ranged energy damage), **Damage** (melee harm), **Deflect** (defensive interception), **Nullify** (power suppression), and **Weaken** (trait reduction).

Every attack effect follows the attack-check → resistance-check flow owned by the Effect Framework's type rules. The Attack Effect KA is responsible for the specific flavor — what each of these effects *does* to the target and what parameters define the encounter. The invariant: attack effects always require an attack check by default; all allow a resistance check. The specific resistance (Toughness, Fortitude, Will) is a property of each individual effect, defined at acquisition.

#### Affliction

#### Domain Language

- Type Attack, action Standard, range Close, duration Instant, resistance Fortitude or Will (chosen at acquisition), cost 1 per rank.
- Three conditions chosen at acquisition for degrees 1, 2, and 3; each progressively worse.
- Target makes resistance check at end of each of their turns; success removes one degree.
- Third-degree recovery requires a full minute (or outside aid) after the Affliction is no longer active.

#### References

**Ref — Affliction**
Source: context/rules/HeroesHandbook-rules__chunk_089.md
Locator: lines 5980-6040
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_089.md covering Affliction effect: conditions, degrees, resistance, recovery]
```

---

#### Blast (Damage, Ranged)

#### Domain Language

- Blast is Damage with the Ranged extra applied; not a separate effect type.
- Stat block with Ranged: type Attack, action Standard, range Ranged, duration Instant, resistance Toughness, cost 2 per rank.
- Requires a ranged attack check vs. target's Dodge; on a hit, target makes Toughness check vs. DC 15 + effect rank.
- Base Damage (1 pp/rank) + Ranged extra (1 pp/rank) = 2 pp/rank for Blast.

#### References

**Ref — Power Effects Alphabetical Descriptions (Alternate Form - Blast)**
Source: context/rules/HeroesHandbook-rules__chunk_090.md
Locator: lines 6041-6170
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_090.md covering Blast (Damage, Ranged) effect description]
```

---

#### Damage

#### Domain Language

- Type Attack, action Standard, range Close, duration Instant, resistance Toughness, cost 1 per rank.
- DC of the Toughness check = 15 + Damage rank.
- Four degrees of failure: minor penalty → dazed and penalized → staggered and penalized → incapacitated (then dying → dead).
- Damage stacks with Strength for unarmed attacks.

#### References

**Ref — Damage**
Source: context/rules/HeroesHandbook-rules__chunk_097.md
Locator: lines 6652-6710
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_097.md covering Damage effect]
```

**Ref — Damaging Objects**
Source: context/rules/HeroesHandbook-rules__chunk_098.md
Locator: lines 6711-6783
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_098.md covering Damaging Objects rules]
```

---

#### Deflect

#### Domain Language

- Type Defense, action Standard (or Reaction with extra), range Ranged, duration Instant, cost 1 per rank.
- Uses Deflect rank as defense check instead of normal active defense; can protect other characters in range.
- Medium and long range penalties apply to Deflect attempts at distance.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_087.md — Deflect entry in summary table]
```

---

#### Nullify

#### Domain Language

- Type Attack, action Standard, range Ranged, duration Instant, cost 1 per rank.
- Ranged attack check required; on hit, opposed check of target's effect rank (or Will) vs. Nullify rank.
- Success counters (turns off) the targeted effect; target can re-activate on their next action.
- Targets effects by descriptor; Broad or Simultaneous extras can affect multiple effects.

#### References

**Ref — Nullify**
Source: context/rules/HeroesHandbook-rules__chunk_125.md
Locator: lines 8353-8457
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_125.md covering Nullify effect]
```

---

#### Weaken

#### Domain Language

- Type Attack, action Standard, range Close, duration Instant, resistance Fortitude or Will, cost 1 per rank.
- On failed resistance check: target's specified trait reduced by degree of failure, up to Weaken rank.
- Weaken is cumulative — multiple applications stack up to the effect rank maximum.
- Targets recover at 1 point of the reduced trait per round.

#### References

**Ref — Weaken**
Source: context/rules/HeroesHandbook-rules__chunk_139.md
Locator: lines 9561-9684
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_139.md covering Weaken effect]
```

---

#### Decisions made

- **Deflect grouped under Attack Effect despite being defensive in fiction**: Deflect is type Defense in the rules but its primary role in the domain — deflecting incoming attacks — groups it naturally with attack-related mechanics. However, it is typed as a Defense effect. Keeping it here as a modeling choice; it interacts directly with attack resolution.
- **Damage and Blast (Damage, Ranged) as separate terms**: Blast is a preconfigured Damage+Ranged combination, not a new effect. Keeping both as terms because the rules treat "Blast" as a named configuration worth calling out separately from bare Damage.

---

### Defense Effect

A Defense Effect is any power effect whose primary purpose is to protect the character from harm, prevent death, or provide ongoing resistance. The four Defense Effects in this module — **Immortality**, **Immunity**, **Protection**, and **Regeneration** — each address a different aspect of survivability: Prevention (Protection raises the Toughness bar before harm arrives), Nullification (Immunity makes specific threats automatically irrelevant), Recovery (Regeneration heals damage after it is taken), and Resurrection (Immortality reverses death itself).

Defense Effects share the pattern of being permanent or near-permanent and operating without active triggering in most cases. The invariant for this KA: every Defense Effect either raises a resistance number (Protection), bypasses a resistance entirely (Immunity), or accelerates or enables recovery from conditions (Regeneration, Immortality). No Defense Effect requires an attack check by the user.

#### Immortality

#### Domain Language

- Type Defense, action None, range Personal, duration Permanent, cost 2 per rank.
- Recovery time after death = time rank (19 − Immortality rank); at rank 20, recover each action round.
- Does not prevent death — only enables return afterward.

#### References

**Ref — Immortality**
Source: context/rules/HeroesHandbook-rules__chunk_111.md
Locator: lines 7498-7571
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_111.md covering Immortality effect]
```

---

#### Immunity

#### Domain Language

- Type Defense, action None, range Personal, duration Permanent, cost 1 per rank.
- Rank cost scales by scope: narrow immunity = 1 rank; Life Support = 10 ranks; all Fortitude effects = 30 ranks.
- Provides complete protection against the specified effect set with no check required.
- Partial immunity (half effect) costs half the full rank.

#### References

**Ref — Immunity**
Source: context/rules/HeroesHandbook-rules__chunk_112.md
Locator: lines 7572-7614
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_112.md covering Immunity effect]
```

**Ref — Degrees Of Immunity**
Source: context/rules/HeroesHandbook-rules__chunk_113.md
Locator: lines 7615-7665
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_113.md covering degrees of Immunity]
```

---

#### Protection

#### Domain Language

- Type Defense, action None, range Personal, duration Permanent, cost 1 per rank.
- +1 Toughness per rank; stacks with Stamina-derived Toughness.
- Permanent and always active; cannot be deactivated and cannot benefit from extra effort.

#### References

**Ref — Protection**
Source: context/rules/HeroesHandbook-rules__chunk_126.md
Locator: lines 8458-8500
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_126.md covering Protection effect]
```

---

#### Regeneration

#### Domain Language

- Type Defense, action None, range Personal, duration Permanent, cost 1 per rank.
- Recovery phases: Toughness penalties removed at rank × minutes rate, then damage conditions at rank × minutes rate.
- Permanent and always active; cannot be deactivated.

#### References

**Ref — Regeneration**
Source: context/rules/HeroesHandbook-rules__chunk_127.md
Locator: lines 8501-8647
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_127.md covering Regeneration effect]
```

---

#### Decisions made

- **Defense Effect as a separate KA from Attack Effect**: Defense and Attack are fundamentally different interaction patterns (passive protection vs. active targeting). Merging them into "Combat Effect" would obscure this distinction.
- **Deflect left in Attack Effect KA**: Deflect is Defense-typed but interacts directly with attack resolution; grouped under Attack Effect for modeling clarity, not under Defense Effect.

---

### Mobility Effect

A Mobility Effect is any power effect that grants, enhances, or alters a character's locomotion — how they move through the world. The seven Mobility Effects cover the complete space of extraordinary movement: **Burrowing** (underground), **Flight** (air), **Leaping** (ballistic arcs), **Movement** (special modes), **Speed** (ground velocity), **Swimming** (water), and **Teleport** (instantaneous relocation). Each grants a distinct mode with distinct speed, mechanics, and environmental interactions.

Mobility Effects share the pattern of free-action activation and sustained duration (with Leaping as the exception: instant duration). They provide speed ranks or movement modes that supplement or replace normal ground movement. The invariant: Mobility Effects cannot by themselves confer capability in a medium they do not cover — Flight does not grant Swimming, Speed does not grant Flight. Each mode must be purchased separately.

#### Burrowing

#### Domain Language

- Type Movement, action Free, range Personal, duration Sustained, cost 1 per rank.
- Speed through soil = Burrowing rank − 5; clay/packed earth −1, solid rock −2.
- Character chooses whether tunnel is permanent or collapses.

#### References

**Ref — Burrowing**
Source: context/rules/HeroesHandbook-rules__chunk_091.md
Locator: lines 6171-6210
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_091.md covering Burrowing effect]
```

---

#### Flight

#### Domain Language

- Type Movement, action Free, range Personal, duration Sustained, cost 2 per rank.
- Flight speed rank = effect rank; hovering available by default.
- Activating is free action; moving requires a move action. Sustained — if unable to maintain, character falls.

#### References

**Ref — Flight**
Source: context/rules/HeroesHandbook-rules__chunk_106.md
Locator: lines 7187-7254
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_106.md covering Flight effect]
```

---

#### Leaping

#### Domain Language

- Type Movement, action Free, range Personal, duration Instant, cost 1 per rank.
- Jump distance rank = Leaping rank − 2; no damage from landing within maximum distance.
- Cannot change direction mid-air; follows a ballistic arc.

#### References

**Ref — Leaping**
Source: context/rules/HeroesHandbook-rules__chunk_116.md
Locator: lines 7819-7887
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_116.md covering Leaping effect]
```

---

#### Movement

#### Domain Language

- Type Movement, action Free, range Personal, duration Sustained, cost 2 per rank.
- Each rank grants one special movement mode: Dimension Travel, Environmental Adaptation, Permeate, Safe Fall, Slithering, Space Travel, Sure-Footed, Swinging, Time Travel, Trackless, Wall-Crawling, Water-Walking.
- Each mode operates according to its own specific sub-rules.

#### References

**Ref — Dimension Travel**
Source: context/rules/HeroesHandbook-rules__chunk_123.md
Locator: lines 8246-8298
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_123.md covering Dimension Travel mode]
```

**Ref — Space Travel**
Source: context/rules/HeroesHandbook-rules__chunk_124.md
Locator: lines 8299-8352
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_124.md covering Space Travel mode]
```

---

#### Speed

#### Domain Language

- Type Movement, action Free, range Personal, duration Sustained, cost 1 per rank.
- Ground speed rank = effect rank; improves all ground-speed-based movement.
- Does not grant flight, swimming, or other non-ground movement.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_088.md — Speed entry in N-W summary table]
```

---

#### Swimming

#### Domain Language

- Type Movement, action Free, range Personal, duration Sustained, cost 1 per rank.
- Water speed rank = effect rank − 2; routine Athletics (Swimming) checks are automatic.
- Does not grant underwater breathing.

#### References

**Ref — Swimming**
Source: context/rules/HeroesHandbook-rules__chunk_136.md
Locator: lines 9258-9382
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_136.md covering Swimming effect]
```

---

#### Teleport

#### Domain Language

- Type Movement, action Move, range Rank range, duration Instant, cost 2 per rank.
- Destination must be well-known or accurately sensed; blind teleporting risks error.
- Character retains velocity from before the teleport; instant arrival, no transit time.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_088.md — Teleport entry in N-W summary table]
```

---

#### Decisions made

- **Movement (effect) vs Burrowing/Flight/Leaping/Speed/Swimming/Teleport**: Movement is the generic effect that grants named special modes (Wall-Crawling, Swinging, etc.); the others are dedicated effects with their own cost schedules. All are core terms because each has distinct cost and sub-rules.
- **Leaping has Instant duration unlike other Mobility Effects**: This is a design feature of the effect, not an error. Leaping represents a discrete jump (not continuous locomotion), hence instant duration.

---

### Sensory Effect

A Sensory Effect is any power effect that grants, enhances, or fools perception — the ability to collect information about the world or deny that ability to others. The six Sensory Effects cover information gathering (**Communication**, **Comprehend**, **Mind Reading**, **Remote Sensing**, **Senses**) and information denial (**Concealment**). These effects define the superhuman informational layer — who knows what, who can communicate with whom, and who can be perceived.

Sensory Effects are primarily free or no-action and permanent or sustained, reflecting their nature as always-on perceptual capabilities. The invariant: every Sensory Effect either adds or removes information flow relative to the character; none of them directly cause harm (Mind Reading's contact is non-damaging; Concealment's hiding is not an attack).

#### Communication

#### Domain Language

- Type Sensory, action Free, range Rank range, duration Sustained, cost 4 per rank.
- Communicate over distance via a chosen sense type medium; language-dependent by default.
- Point-to-point communication to a known location or person.

#### References

**Ref — Communication**
Source: context/rules/HeroesHandbook-rules__chunk_092.md
Locator: lines 6211-6335
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_092.md covering Communication effect]
```

---

#### Comprehend

#### Domain Language

- Type Sensory, action None, range Personal, duration Permanent, cost 2 per rank.
- Each rank = one communication type: Animals, Languages, Machines, Objects, Plants, Spirits.
- Always active — requires no action to use.

#### References

**Ref — Comprehend**
Source: context/rules/HeroesHandbook-rules__chunk_093.md
Locator: lines 6336-6405
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_093.md covering Comprehend effect]
```

---

#### Concealment

#### Domain Language

- Type Sensory, action Free, range Personal, duration Sustained, cost 2 per rank.
- Grants total concealment from a specific sense type; Visual costs 2 ranks per visual sense.
- Cannot conceal from tactile sense.
- Activated as free action; sustained — dropping concentration ends it.

#### References

**Ref — Concealment**
Source: context/rules/HeroesHandbook-rules__chunk_094.md
Locator: lines 6406-6471
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_094.md covering Concealment effect]
```

**Ref — Concealment And Perception Range**
Source: context/rules/HeroesHandbook-rules__chunk_095.md
Locator: lines 6472-6531
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_095.md covering Concealment and Perception Range interaction]
```

---

#### Mind Reading

#### Domain Language

- Type Sensory, action Standard, range Perception, duration Sustained, cost 2 per rank.
- Opposed effect check vs. target's Will; 4 degrees: surface thoughts, personal thoughts, memories, subconscious.
- Target makes Will check at end of their turns; success breaks contact.

#### References

**Ref — Mind Reading**
Source: context/rules/HeroesHandbook-rules__chunk_118.md
Locator: lines 7954-7997
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_118.md covering Mind Reading effect]
```

**Ref — Mind Reading And Deception**
Source: context/rules/HeroesHandbook-rules__chunk_119.md
Locator: lines 7998-8037
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_119.md covering Mind Reading and Deception interactions]
```

---

#### Remote Sensing

#### Domain Language

- Type Sensory, action Free, range Rank range, duration Sustained, cost 1–5 per rank based on sense types.
- Displaces senses to another location; normal senses suppressed while active.
- Character is vulnerable while active (active defenses halved).

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_088.md — Remote Sensing entry in N-W summary table]
```

---

#### Senses

#### Domain Language

- Type Sensory, action None, range Personal, duration Permanent, cost 1 per rank.
- Each rank buys one enhancement from a large menu: Accurate, Acute, Analytical, Awareness, Communication Link, Counters Concealment, Counters Illusion, Danger Sense, Darkvision, Detect, Direction Sense, Distance Sense, Extended, Infravision, Low-Light Vision, Microscopic Vision, Penetrates Concealment, Postcognition, Precognition, Radio, Radius, Ranged, Rapid, Time Sense, Tracking, Ultra-Hearing, Ultravision.
- Permanent — purchased enhancements are always active.

#### References

**Ref — Senses**
Source: context/rules/HeroesHandbook-rules__chunk_128.md
Locator: lines 8648-8698
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_128.md covering Senses effect and sub-effects list]
```

**Ref — Communication Link**
Source: context/rules/HeroesHandbook-rules__chunk_129.md
Locator: lines 8699-8760
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_129.md covering Communication Link sub-effect]
```

**Ref — Direction Sense**
Source: context/rules/HeroesHandbook-rules__chunk_130.md
Locator: lines 8761-8806
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_130.md covering Direction Sense sub-effect]
```

**Ref — Penetrates Concealment**
Source: context/rules/HeroesHandbook-rules__chunk_131.md
Locator: lines 8807-8917
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_131.md covering Penetrates Concealment sub-effect]
```

**Ref — Time Sense**
Source: context/rules/HeroesHandbook-rules__chunk_132.md
Locator: lines 8918-9006
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_132.md covering Time Sense sub-effect]
```

**Ref — Sense Types**
Source: context/rules/HeroesHandbook-rules__chunk_085.md
Locator: lines 5315-5354
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_085.md covering sense types (visual, auditory, etc.)]
```

---

#### Decisions made

- **Mind Reading grouped under Sensory not Attack**: Mind Reading is a Sensory-type effect mechanically. Its opposed check does not inflict damage or conditions — it extracts information. The "attack" feel is narrative, not mechanical.
- **Communication and Senses as separate terms despite both being sensory**: Communication creates two-way information channels; Senses enhances one-way perception. Different mechanics justify separate terms.

---

### Control and General Effect

The Control and General Effect KA encompasses all effects that do not fit cleanly into Attack, Defense, Mobility, or Sensory categories — effects that manipulate the environment, transform matter, summon beings, provide utility, or enhance physical form. This is intentionally a broad KA; the domain is large (16 terms) and these effects share the common pattern of being useful in non-combat contexts even when they have combat applications. **Create**, **Environment**, **Illusion**, **Luck Control**, **Move Object**, **Summon**, and **Transform** are Control type; **Elongation**, **Enhanced Trait**, **Feature**, **Growth**, **Healing**, **Insubstantial**, **Quickness**, **Shrinking**, and **Variable** are General type.

The invariant for this KA: these effects manipulate situation, form, or utility rather than directly harming opponents or protecting the self. Several (Create, Move Object) can be used offensively, but the primary purpose is control or versatility, not raw damage.

#### Create

#### Domain Language

- Type Control, action Standard, range Ranged, duration Sustained, cost 2 per rank.
- Max volume = effect rank on volume table; created objects have Toughness = effect rank.
- Objects vanish if unmaintained; character can spend PP equal to rank for permanence.

#### References

**Ref — Trapping With Objects**
Source: context/rules/HeroesHandbook-rules__chunk_096.md
Locator: lines 6532-6651
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_096.md covering Create effect and trapping rules]
```

---

#### Elongation

#### Domain Language

- Type General, action Free, range Personal, duration Sustained, cost 1 per rank.
- Reach extends to size rank + effect rank; +1 to grab checks per rank.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_087.md — Elongation entry in A-M summary table]
```

---

#### Enhanced Trait

#### Domain Language

- Type General, action Free, range Personal, duration Sustained, cost equal to base cost of trait per rank.
- Increases an existing trait by rank; subject to PL limits.
- Sustained — drops if character cannot maintain.

#### References

**Ref — Enhanced Trait**
Source: context/rules/HeroesHandbook-rules__chunk_101.md
Locator: lines 6892-6936
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_101.md covering Enhanced Trait effect]
```

---

#### Environment

#### Domain Language

- Type Control, action Standard, range Rank range, duration Sustained, cost 1–2 per rank.
- Alters environmental conditions (Cold, Heat, Light, Visibility, Movement impede) in a radius area.
- Multiple environment effects can be stacked on one Environment effect.

#### References

**Ref — Environment**
Source: context/rules/HeroesHandbook-rules__chunk_102.md
Locator: lines 6937-6985
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_102.md covering Environment effect]
```

**Ref — Energy Control**
Source: context/rules/HeroesHandbook-rules__chunk_103.md
Locator: lines 6986-7064
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_103.md covering Energy Control powers context]
```

---

#### Feature

#### Domain Language

- Type General, action None, range Personal, duration Permanent, cost 1 per rank (each rank = one Feature).
- Provides one minor ability per rank with a concrete game effect; distinct from free descriptors.

#### References

**Ref — Feature**
Source: context/rules/HeroesHandbook-rules__chunk_105.md
Locator: lines 7117-7186
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_105.md covering Feature effect]
```

**Ref — Extra Limbs**
Source: context/rules/HeroesHandbook-rules__chunk_104.md
Locator: lines 7065-7116
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_104.md covering Extra Limbs feature context]
```

---

#### Growth

#### Domain Language

- Type General, action Free, range Personal, duration Sustained, cost 2 per rank.
- Per rank: +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth; size category changes per 4 ranks.
- Per 2 ranks: −1 Dodge, −1 Parry, +1 Intimidation. Per 8 ranks: +1 Speed.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_087.md — Growth entry in A-M summary table]
```

---

#### Healing

#### Domain Language

- Type General, action Standard, range Close, duration Instant, cost 2 per rank.
- DC 10 check; each degree of success removes one damage condition from most severe.
- Cannot be used on same target more than once per scene; doesn't work on targets unable to recover naturally.

#### References

**Ref — Healing**
Source: context/rules/HeroesHandbook-rules__chunk_108.md
Locator: lines 7316-7409
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_108.md covering Healing effect]
```

---

#### Illusion

#### Domain Language

- Type Control, action Standard, range Perception, duration Sustained, cost 1–5 per rank by sense types.
- Insight check DC 10 + rank to detect; no physical substance — cannot cause real damage.
- Maintaining and altering illusion = free action each turn.

#### References

**Ref — Illusion**
Source: context/rules/HeroesHandbook-rules__chunk_109.md
Locator: lines 7410-7457
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_109.md covering Illusion effect]
```

**Ref — Maintaining Illusions**
Source: context/rules/HeroesHandbook-rules__chunk_110.md
Locator: lines 7458-7497
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_110.md covering Maintaining Illusions rules]
```

---

#### Insubstantial

#### Domain Language

- Type General, action Free, range Personal, duration Sustained, cost 5 per rank (4 ranks total).
- Four forms: rank 1 Fluid, rank 2 Gaseous, rank 3 Energy, rank 4 Incorporeal.
- Switch between available forms as a free action.

#### References

**Ref — Insubstantial**
Source: context/rules/HeroesHandbook-rules__chunk_114.md
Locator: lines 7666-7733
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_114.md covering Insubstantial effect]
```

**Ref — Insubstantial Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_115.md
Locator: lines 7734-7818
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_115.md covering Insubstantial descriptor interactions]
```

---

#### Luck Control

#### Domain Language

- Type Control, action Reaction, range Perception, duration Instant, cost 3 per rank.
- Each rank grants one capability involving hero points (spend for another, transfer, negate, or force re-roll).

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_087.md — Luck Control entry in A-M summary table]
```

---

#### Move Object

#### Domain Language

- Type Control, action Standard, range Ranged, duration Sustained, cost 2 per rank.
- Effective Strength = rank for lifting/moving; cannot directly damage a target.
- Can make disarm, grab, or trip maneuvers at range; target resists with Strength check vs. effect rank.

#### References

**Ref — Move Object**
Source: context/rules/HeroesHandbook-rules__chunk_122.md
Locator: lines 8155-8245
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_122.md covering Move Object effect]
```

---

#### Quickness

#### Domain Language

- Type General, action Free, range Personal, duration Sustained, cost 1 per rank.
- Each rank reduces time rank of routine tasks by 1; does not affect non-routine tasks or movement.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_088.md — Quickness entry in N-W summary table]
```

---

#### Shrinking

#### Domain Language

- Type General, action Free, range Personal, duration Sustained, cost 2 per rank.
- Per 4 ranks: −1 size category. Per rank: +1 Stealth. Per 2 ranks: +1 active defenses, −1 Speed.
- Reduces Strength (for size-based purposes) and Intimidation.

#### References

**Ref — Shrinking**
Source: context/rules/HeroesHandbook-rules__chunk_133.md
Locator: lines 9007-9051
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_133.md covering Shrinking effect]
```

---

#### Summon

#### Domain Language

- Type Control, action Standard, range Close, duration Sustained, cost 2 per rank.
- Minion has power points = rank × 15; minion PL ≤ effect rank.
- Dazed when summoned (standard action first turn); directing = move action. Disappears if incapacitated.

#### References

**Ref — Summon**
Source: context/rules/HeroesHandbook-rules__chunk_134.md
Locator: lines 9052-9210
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_134.md covering Summon effect and minion rules]
```

**Ref — Summon And Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_135.md
Locator: lines 9211-9257
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_135.md covering Summon and descriptor interactions]
```

---

#### Transform

#### Domain Language

- Type Control, action Standard, range Close, duration Sustained, cost 2–5 per rank by scope.
- Cost by breadth: 2 pp narrow → up to 5 pp anything-to-anything; max mass = rank − 6 on mass table.
- Inanimate objects don't resist; living targets make Fortitude check. Sustained = reversible.

#### References

**Ref — Destructive Transformations**
Source: context/rules/HeroesHandbook-rules__chunk_137.md
Locator: lines 9383-9455
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_137.md covering Destructive Transformations and Transform rules]
```

**Ref — Morph**
Source: context/rules/HeroesHandbook-rules__chunk_121.md
Locator: lines 8097-8154
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_121.md covering Morph effect context for Transform]
```

---

#### Variable

#### Domain Language

- Type General, action Standard, range Personal, duration Sustained, cost 7 per rank.
- Pool size = rank × 5 power points; allocate to any effects of appropriate type/descriptor.
- Subject to PL limits; resetting requires not maintaining the effect.

#### References

**Ref — Variable**
Source: context/rules/HeroesHandbook-rules__chunk_138.md
Locator: lines 9456-9560
Extract: whole

```source
[Verbatim content from HeroesHandbook-rules__chunk_138.md covering Variable effect]
```

---

#### Decisions made

- **Control and General Effects merged into one KA**: With 16 terms this is a large KA, but splitting further would create too many KAs for this module. The unifying concept is "non-combat primary purpose." Control and General are both non-combat primary effects.
- **Element Control and Force Field not included as core terms**: These appear in source chunks as reference context but were not listed in the module partition as core terms. They are context gaps / adjacent concepts.
- **Mental Blast and Mind Control not included as core terms**: These appear in nearby source chunks but are not in the partition's core terms list. Context gap.

---

### Power Array

The Power Array abstraction defines how groups of Alternate Effects are organized into a shared cost pool that allows one set of power points to fund multiple effect options, used exclusively. An **Array** is the collection itself — the container that makes the mutual-exclusivity rule apply and the cost pool meaningful. An **Alternate Effect** is a variant effect added to an Array for a flat 1-point cost each, subject to the rule that its total cost cannot exceed the primary effect's total cost. A **Dynamic Alternate Effect** is a special variant that can share power points with other Dynamic effects and operate simultaneously at reduced effectiveness, at the cost of 2 flat points per dynamic alternate (and 1 point to make the base dynamic).

The Power Array abstraction owns the mutual-exclusivity rule (only one non-dynamic effect active at once), the switching mechanic (free action once per turn), and the propagation rule (if any effect in the Array is disabled, all are equally affected). The invariant: no Array effect can cost more to build than the primary effect that defines the Array's size; permanent effects cannot be Alternate Effects.

#### Array

#### Domain Language

- A collection of Alternate Effects sharing a cost pool; all mutually exclusive — only one active at a time.
- Switching between effects = free action once per turn.
- If any effect is disabled/Nullified/drained, all effects in the Array are equally affected.

#### References

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

```source
### Dynamic Alternate Effect
For 2 power points an Alternate Effect is dynamic; it can
share power points with other Dynamic Alternate Effects,
allowing them all to operate at the same time, but
at reduced effectiveness. You decide
how many power points are allocated to the effects once
per turn as a free action. Making the base effect of an array
Dynamic requires 1 power point.

UNDER THE HOOD: ALTERNATE EFFECTS
Arrays — collections of Alternate Effects — are one of the more complex and important constructs in MUTANTS & MASTERMINDS.
The main reason for the Alternate Effect modifier is to allow a degree of flexibility in terms of a character's power effects
within the cost restrictions laid down by having a finite number of power points. It's based on the assumption that a wide
range of powers has a diminishing return in terms of value, since characters can only use so many effects at once.
```

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

```source
### Flat-Value Modifiers
Some modifiers, rather than increasing or decreasing an effect's cost per rank, have a flat value in power points.
```

---

#### Alternate Effect

#### Domain Language

- Flat extra; cost 1 point per Alternate Effect added to an Array.
- Total cost of the alternate cannot exceed the total cost of the primary (base) effect.
- Permanent effects cannot be Alternate Effects; only one active at a time.

#### References

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

```source
### Dynamic Alternate Effect
For 2 power points an Alternate Effect is dynamic; it can
share power points with other Dynamic Alternate Effects,
allowing them all to operate at the same time.
The main reason for the Alternate Effect modifier is to allow a degree of flexibility in terms of a character's power effects
within the cost restrictions laid down by having a finite number of power points.
```

---

#### Dynamic Alternate Effect

#### Domain Language

- Flat extra; base effect costs 1 extra point to become dynamic; each Dynamic Alternate costs 2 flat points.
- Dynamic effects can share power points and operate simultaneously at reduced effectiveness.
- Character reallocates points among Dynamic effects once per turn as a free action.

#### References

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

```source
### Dynamic Alternate Effect
For 2 power points an Alternate Effect is dynamic; it can
share power points with other Dynamic Alternate Effects,
allowing them all to operate at the same time, but
at reduced effectiveness. You decide
how many power points are allocated to the effects once
per turn as a free action. Making the base effect of an array
Dynamic requires 1 power point.
```

---

#### Decisions made

- **Array, Alternate Effect, Dynamic Alternate Effect as separate terms**: Each has a distinct cost and mechanical rule. Merging them would obscure how Dynamic differs from standard.
- **Power Array as a KA despite being 3 terms**: The array mechanism is a distinct structural concept that governs how effects interact in groups. It is independently meaningful, has its own rules, and fails the "stays as a term under another KA" test — no other KA naturally owns it.

---

## Boundary Domain

### power point

Owned by: Character Construction

- The currency spent to acquire effects, traits, advantages, and skills.
- Power point budget is set by power level (PL × 15 at creation).
- This module uses power point costs as outputs; the budget and economy are Character Construction concerns.

### rank

Owned by: Character Construction

- The numeric level of an effect, ability, skill, or other trait.
- Effects are acquired in ranks and scale with rank; the Power module uses rank in cost formulas and effect resolution.

### resistance check

Owned by: Check Resolution

- The check made by a target to resist a power effect; typically DC 10 + effect rank.
- Every attack-type effect in this module specifies which resistance check applies (Toughness, Fortitude, Will, Dodge).

### Toughness

Owned by: Combat

- Defense used to resist Damage effects; derived from Stamina + Protection ranks + other bonuses.
- Referenced by Damage, Blast, and similar effects as the resistance check target.

### Fortitude

Owned by: Combat

- Defense used to resist Affliction and Weaken effects targeting physical resilience.

### Will

Owned by: Combat

- Defense used to resist mental Affliction, Mind Reading, and Will-targeted Weaken.

### Dodge

Owned by: Combat

- Defense used to avoid ranged attacks and Area effect saves (DC 10 + effect rank for half).
