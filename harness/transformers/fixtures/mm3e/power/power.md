---
state: domain-sketch
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



#### Domain Sketch

- is the *atomic rules-defined unit* of superhuman capability — the named, typed, mechanically complete building block
- carries five fixed properties: type, action, range, duration, and cost per rank — all set at acquisition
- is acquired in ranks; higher rank means greater scale, intensity, reach, or effect magnitude
- exposes its default stat block to the modifier system; extras and flaws alter those defaults
- Invariant: every effect has exactly one type, one action, one range, one duration, and one cost per rank at any point in time
- Collaborates with: Modifier (extras/flaws change its properties and cost), Effect Cost (calculates its price), Power (groups one or more effects into a named capability)

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



#### Domain Sketch

- is the *player-facing named capability* that appears on a character sheet — the fiction label wrapping one or more effects
- acquires one or more effects, each paying its own cost; total power cost = sum of all effect costs
- carries at least one descriptor; the descriptor is not optional
- is approved by the GM before play; the GM may veto or modify powers for series appropriateness
- Invariant: every power must contain at least one effect and at least one descriptor
- Collaborates with: effect (its mechanical content), descriptor (its thematic identity), power point (its economic cost in Character Construction)

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

#### Domain Sketch

- is the *category label* on every effect that governs which general rules apply
- classifies each effect into exactly one of six categories: Attack, Control, Defense, General, Movement, Sensory
- determines whether an effect requires an attack check, allows a resistance check, is activated as free action, or is permanent
- Invariant: every effect belongs to exactly one power type; a power type cannot be changed by modifiers
- Collaborates with: effect (carries the type label), modifier (extras can sometimes change apparent type behavior but not the official type)

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



#### Domain Sketch

- is a free *thematic label* on a power that connects it to the game fiction and mechanical interaction systems
- costs no power points — it is purely a label attached at acquisition
- governs what Nullify can counter and what Immunity can block
- supports GM rulings on descriptor interactions in play
- Invariant: every power must have at least one descriptor; descriptors may not be changed without GM approval
- Collaborates with: Nullify (uses descriptor to target), Immunity (uses descriptor to define coverage), GM (final arbitrator of descriptor interactions)

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


#### Domain Sketch

- is a *descriptor subtype* that identifies how the character came to have their powers
- covers origin categories: Accidental, Bestowed, Invented, Mutant, Training
- typically applies to the character's entire power set rather than individual powers
- Invariant: origin descriptor rarely has direct mechanical effects; it is primarily a narrative and GM-ruling tool
- Collaborates with: descriptor (its parent concept), power set (the scope it typically covers)
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


#### Domain Sketch

- is a *descriptor subtype* that identifies the energy or force a power draws upon to function
- covers source categories: Biological, Cosmic, Divine, Extradimensional, Magical, Moral, Psionic, Technological
- has direct mechanical significance — Nullify targeting 'magical effects' counters all powers with Magical source
- a power can have multiple source descriptors if it draws on more than one source
- Invariant: source descriptor determines Nullify and Immunity interactions more directly than origin descriptor
- Collaborates with: descriptor (its parent concept), Nullify (primary mechanical consumer), Immunity (secondary consumer)
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


#### Domain Sketch

- is the *unmodified power-point cost per rank* as printed in the rules for a specific effect
- is immutable — set at effect design time and cannot be changed by play or by modifiers
- seeds the modifier math: cost per rank = base cost + extras − flaws
- Invariant: base cost is always a positive integer ≥ 1 for every defined effect
- Collaborates with: effect (carries its base cost), modifier (adjusts from this baseline), cost per rank (derived value)
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


#### Domain Sketch

- is the *final modified cost per rank* paid for each rank of an effect after all modifier math is complete
- is computed as: base cost + (sum of per-rank extras) − (sum of per-rank flaws)
- drives the bulk of total power cost: effect cost = (cost per rank × ranks) + flat modifiers
- Invariant: cost per rank cannot drop below 1 pp/rank regardless of flaws applied
- Collaborates with: base cost (starting value), extra/flaw (modifiers applied), flat modifier (post-multiplication), rank (the multiplier)
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


#### Domain Sketch

- is a *fixed-point price adjustment* applied to the final total cost after per-rank cost × rank is computed
- adds (flat extra) or subtracts (flat flaw) a set number of points from the total, regardless of rank
- is applied last in the cost formula: (cost per rank × rank) + flat extras − flat flaws
- Invariant: flat modifiers cannot reduce total power cost below 1 power point
- Collaborates with: extra (flat extras add to total), flaw (flat flaws subtract), cost per rank (applied after multiplication)
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



#### Domain Sketch

- is a *modifier that enhances an effect* — it broadens, extends, or improves the effect beyond its defaults
- is either per-rank (adds to cost per rank) or flat (adds to the final total cost)
- must grant a genuine improvement; cosmetic changes are descriptors, not extras
- Invariant: an effect cannot receive an extra for a property it already has (e.g., cannot apply Ranged extra to an already-Ranged effect)
- Collaborates with: effect (is applied to an effect), base cost (raises it to produce cost per rank), flat modifier (for flat-value extras)

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



#### Domain Sketch

- is a *modifier that limits an effect* — it restricts, narrows, or conditions the effect below its defaults
- is either per-rank (reduces cost per rank) or flat (reduces the final total cost)
- must represent a genuine limitation reducing utility by approximately half or more; cosmetic restrictions are descriptors
- Invariant: flaws cannot reduce cost per rank below 1 pp/rank; total cost cannot drop below 1 pp
- Collaborates with: effect (is applied to an effect), base cost (reduces it to produce cost per rank), flat modifier (for flat-value flaws)

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



#### Domain Sketch

- is a *flat extra* that adds +2 per rank to attack checks made with the specific effect
- costs 1 flat point per rank of accuracy bonus (i.e., 1 pp for +2, 2 pp for +4, etc.)
- applies only to the specific effect it is purchased for
- Invariant: the attack bonus from Accurate cannot push total attack bonus beyond PL × 2
- Collaborates with: attack check (the thing improved), PL limits (the cap), flat modifier (the cost mechanism)

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



#### Domain Sketch

- is a *per-rank extra* that removes the attack check requirement and instead affects all targets in a defined area
- allows targets a Dodge resistance check (DC 10 + effect rank) to avoid the effect (success = half rank effect)
- offers shapes: Burst, Cloud, Cone, Cylinder, Line, Perception, Shapeable
- costs +1 per rank; each additional rank of Area increases the area dimensions
- Invariant: Area effects cannot exclude specific targets within the area without the Selective extra
- Collaborates with: Dodge (the resistance check), area shape (the dimension of coverage), effect rank (sets DC and area size), Selective extra (for target exclusion)

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



#### Domain Sketch

- is a *per-rank extra* that allows an effect to hit multiple targets or strike a single target multiple times
- against a single target: +2 to effect DC at 2 degrees of attack success; +5 at 3+ degrees
- against multiple targets: one attack roll with penalty equal to number of targets; each target whose Dodge is exceeded is hit
- costs +1 per rank
- Invariant: Multiattack has two distinct modes (single-target boost vs. multi-target spray); the character chooses each time they use the effect
- Collaborates with: attack check (the roll used for both modes), Dodge (the defense of each target in spray mode), DC (increased in single-target mode)

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



#### Domain Sketch

- is a *flat extra* that allows an effect to bypass Impervious resistance
- costs 1 flat point per rank of Penetrating; overcomes Impervious to degree equal to Penetrating rank
- forces targets with Impervious Toughness to resist damage rank equal to the Penetrating rank
- Invariant: Penetrating only bypasses Impervious; it does not increase the attack's DC or rank
- Collaborates with: Impervious extra (what it bypasses), Toughness (the resistance still applied), flat modifier (the cost mechanism)

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



#### Domain Sketch

- is a *flat flaw* that requires the character to spend an action activating the power before any effects become available
- costs −1 (move action) or −2 (standard action) from the power's total cost
- applies to the entire power — all effects within the power require the activation
- requires reactivation after being Nullified or deactivated
- Invariant: Activation applies to the whole power, not individual effects within it
- Collaborates with: flat modifier (the cost mechanism), Nullify (the deactivation trigger), the entire power (all effects affected)

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



#### Domain Sketch

- is a *per-rank flaw* that restricts an effect to function only under certain circumstances, against certain targets, or in certain conditions
- costs −1 per rank
- requires the limitation to genuinely reduce utility to approximately half or less; GM determines qualification
- is distinct from complications — complications trigger narrative events with hero point rewards; Limited reduces mechanical cost
- Invariant: Limited must be a genuine mechanical restriction, not a cosmetic or flavor restriction
- Collaborates with: per-rank flaw (the cost mechanism), GM approval (required to qualify), circumstance (the limiting condition)

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



#### Domain Sketch

- is a *flat flaw* that represents a power built into an item that can be physically taken from the character
- costs −1 per 5 points of final power cost (or −2 if easily removable)
- allows the item to be taken when the character is both stunned and defenseless, or via a disarm/grab
- applies to the entire power — all effects are unavailable if the item is taken
- allows the item itself to be damaged using object damage rules; Toughness = character's PL
- Invariant: Removable applies to the whole power, not individual effects
- Collaborates with: flat modifier (the cost mechanism), stunned+defenseless conditions (the vulnerability window), item Toughness (= PL), object damage rules

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



#### Domain Sketch

- is an *Attack effect* that imposes progressively worsening conditions on a target who fails a resistance check
- requires an attack check before the target makes a resistance check (Fortitude or Will — chosen at acquisition)
- applies conditions based on degree of failure: first degree applies condition 1, second adds condition 2, third adds condition 3
- allows the target to make a resistance check at end of each of their turns; success removes one degree (from worst)
- enforces special recovery for third degree: full minute (or outside aid) after the Affliction ends
- Invariant: exactly three conditions must be specified at acquisition, in degree order; each must be progressively worse
- Collaborates with: resistance check (Fort or Will), condition (the output applied), attack check (prerequisite)

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



#### Domain Sketch

- is the *foundational Attack effect* for direct physical harm at close range
- sets resistance check DC = 15 + effect rank against target's Toughness
- applies damage conditions in four degrees: minor penalty → dazed and penalized → staggered and penalized → incapacitated
- stacks with character's Strength for unarmed attacks
- Invariant: Damage has Close range by default; it requires the Ranged extra to become Blast
- Collaborates with: Toughness (the resistance), DC (15 + rank), Strength (stacks for unarmed), damage condition (the output)

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



#### Domain Sketch

- is a *Defense effect* that intercepts incoming ranged attacks for the user or nearby allies
- substitutes its rank (plus modifiers) for the normal active defense value of the protected target
- applies range penalties for medium and long range interceptions
- Invariant: Deflect intercepts attacks; it does not prevent the attack from being made — it substitutes the defense roll
- Collaborates with: active defense (Dodge/Parry — replaced by Deflect rank), range penalties (medium/long apply), attack check (what it is countering)

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



#### Domain Sketch

- is an *Attack effect* that suppresses other power effects matching a chosen descriptor
- requires a ranged attack check, then an opposed check: Nullify rank vs. target effect rank (or Will, whichever is higher)
- on success, the targeted effect is countered (turned off); the target can reactivate on their next action
- targets effects by descriptor; Broad and Simultaneous extras expand targeting scope
- Invariant: Nullify suppresses; it does not destroy or permanently remove effects
- Collaborates with: descriptor (the targeting criterion), ranged attack check, opposed check, Will (alternate resistance), sustained vs permanent effects (reactivation rules differ)

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



#### Domain Sketch

- is an *Attack effect* that temporarily reduces a specific trait of the target
- applies reduction equal to degree of failure on the resistance check, up to the Weaken rank maximum
- is cumulative — multiple Weaken applications on the same trait stack up to the rank maximum
- allows targets to recover at 1 point of the reduced trait per round (automatic, no action)
- Invariant: Weaken is cumulative to rank maximum; beyond rank maximum, additional Weaken has no further effect
- Collaborates with: resistance check (Fort or Will), degree of failure (determines reduction amount), target trait (chosen at acquisition), recovery (1 per round automatic)

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



#### Domain Sketch

- is a *Defense effect* that allows the character to return from death after a time period determined by rank
- calculates recovery time as time rank (19 − Immortality rank); at rank 20, recovers each action round
- does not prevent death — it only enables post-death return
- is permanent and always active; cannot be turned off
- Invariant: Immortality only triggers after death; it has no effect before death occurs
- Collaborates with: death (the trigger), time rank (the recovery schedule), permanent duration

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



#### Domain Sketch

- is a *Defense effect* that grants automatic success on resistance checks against a specified effect set
- scales cost by scope: 1 rank for narrow immunity, up to 80 ranks for all Toughness effects
- provides complete protection against the covered set with no check required
- offers partial immunity (half effect) for half the full rank cost
- is permanent and always active; cannot be deactivated
- Invariant: Immunity works against the specified descriptor/effect set only; it has no effect outside that set
- Collaborates with: descriptor (the matching criterion), resistance check (bypassed), partial immunity (the half-cost variant)

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



#### Domain Sketch

- is a *Defense effect* that adds directly to the character's Toughness defense
- provides +1 Toughness per rank; stacks with Stamina-derived Toughness and Impervious
- is permanent and always active — cannot be deactivated and cannot benefit from extra effort
- Invariant: Protection is always on; there is no version that can be turned off without a flaw
- Collaborates with: Toughness (the defense it enhances), Stamina (stacks with), Impervious extra (can be combined with)

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



#### Domain Sketch

- is a *Defense effect* that progressively removes damage conditions over time
- recovers in two phases: first removes Toughness penalties at rank per minute, then removes damage conditions at rank per minute from most severe
- is permanent and always active — cannot be deactivated
- Invariant: Regeneration cannot affect conditions that have not occurred naturally — it only repairs existing damage
- Collaborates with: damage conditions (the target of recovery), Toughness penalty (the first-phase target), permanent duration

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



#### Domain Sketch

- is a *Movement effect* that grants the ability to move through earth, soil, clay, or rock
- calculates speed rank as Burrowing rank − 5; applies terrain penalties (clay −1, solid rock −2)
- lets the character choose on each use whether the tunnel is permanent or collapses behind them
- Invariant: Burrowing does not grant underwater breathing or any other survival capability
- Collaborates with: Movement (its type), speed rank (the output), terrain type (penalty input)

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



#### Domain Sketch

- is a *Movement effect* that grants the ability to fly at a speed rank equal to the effect rank
- provides hovering capability by default — the character can remain stationary in midair
- activates as a free action; moving while airborne requires a move action as normal
- is sustained — the character falls if they cannot maintain it
- Invariant: Flight does not grant additional protection from the fall if the effect ends mid-air
- Collaborates with: speed rank (the output), sustained duration (the maintenance requirement), move action (required for actual movement)

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



#### Domain Sketch

- is a *Movement effect* that extends jumping distance to superhuman scales
- calculates jump distance rank = Leaping rank − 2 on the distance table
- prevents fall damage when landing within maximum jump distance
- follows a ballistic arc — the character cannot change direction mid-air
- Invariant: Leaping has Instant duration — it does not sustain; each jump is a discrete action
- Collaborates with: distance rank (the jump reach), Instant duration (discrete per-jump activation)

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



#### Domain Sketch

- is a *Movement effect* that grants one special movement mode per rank from a defined list
- offers modes: Dimension Travel, Environmental Adaptation, Permeate, Safe Fall, Slithering, Space Travel, Sure-Footed, Swinging, Time Travel, Trackless, Wall-Crawling, Water-Walking
- activates as free action; requires a move action for actual movement (as all movement effects)
- is sustained; losing it ends the movement mode until reactivated
- Invariant: each rank grants exactly one mode; modes are independent — multiple modes require multiple ranks
- Collaborates with: movement mode (the specific capability acquired), sustained duration, GM (for Dimension/Time Travel interactions with setting)

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



#### Domain Sketch

- is a *Movement effect* that increases ground movement speed
- sets ground speed rank = effect rank; improves all speed-based ground movement actions
- does not grant flight, aquatic movement, or any non-ground mode
- Invariant: Speed only enhances ground movement; each other movement mode requires its own effect
- Collaborates with: speed rank (the output), ground movement (the only context it improves), move action (required for actual movement)

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



#### Domain Sketch

- is a *Movement effect* that grants enhanced aquatic movement speed
- sets water speed rank = effect rank − 2 on the speed table
- makes routine Athletics (Swimming) checks automatic — no roll required
- does not grant underwater breathing capability
- Invariant: Swimming does not prevent suffocation underwater; Immunity (Suffocation) must be purchased separately
- Collaborates with: speed rank (the aquatic output), Athletics (Swimming) check (made automatic), Immunity (for breathing)

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



#### Domain Sketch

- is a *Movement effect* that provides instantaneous point-to-point relocation
- requires the destination to be either well-known or accurately sensed; unperceived destinations risk teleport error
- preserves the character's velocity from before the teleport (momentum is conserved)
- carries mass rank 0 additional mass by default (Mass extra extends this)
- Invariant: Teleport is Instant — there is no transit, no passage through intervening space
- Collaborates with: perception (for destination targeting), mass rank (for carrying capacity), Instant duration

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



#### Domain Sketch

- is a *Sensory effect* that sends and receives information over distance via a chosen sense type medium
- determines range by effect rank on the distance table; operates as point-to-point by default
- requires a shared language between sender and receiver; language-dependent unless modified
- Invariant: Communication requires a chosen sense type medium at acquisition; this cannot be changed without GM approval
- Collaborates with: sense type (the medium), range (determined by rank), language (a prerequisite for exchange)

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



#### Domain Sketch

- is a *Sensory effect* that grants understanding of and ability to communicate with otherwise inaccessible beings or languages
- allocates each rank to exactly one communication type at acquisition: Animals, Languages, Machines, Objects, Plants, Spirits
- is permanent — always active, requires no action to invoke
- Invariant: each rank covers exactly one communication type; types do not stack within one rank
- Collaborates with: sense type (implicit), communication type (the chosen category per rank)

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



#### Domain Sketch

- is a *Sensory effect* that makes the character undetectable to one specific sense type
- grants total concealment — characters relying on that sense cannot perceive the character at all
- costs 2 ranks per visual sense type; costs 1 rank for most other sense types
- is activated as a free action; must be sustained — lapses if concentration is broken
- Invariant: concealment from tactile (touch) sense is not possible
- Collaborates with: sense type (the sense being blocked), Senses (a target's sensing capability), attack check (attackers relying on concealed sense are effectively blind)

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



#### Domain Sketch

- is a *Sensory effect* that acts as the catch-all for any sensory enhancement not covered by a dedicated effect
- allocates each rank to one enhancement from a large menu of options
- is permanent — all purchased enhancements are always active
- covers enhancements including Accurate, Acute, Analytical, Awareness, Communication Link, Counters Concealment, Counters Illusion, Danger Sense, Darkvision, Detect, Direction Sense, Distance Sense, Extended, Infravision, Low-Light Vision, Microscopic Vision, Penetrates Concealment, Postcognition, Precognition, Radio, Radius, Ranged, Rapid, Time Sense, Tracking, Ultra-Hearing, Ultravision
- Invariant: each rank of Senses provides exactly one enhancement from the defined list
- Collaborates with: sense type (the sense being enhanced), permanent duration, Concealment (countered by Counters Concealment enhancement)

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



#### Domain Sketch

- is a *Control effect* that forms solid physical objects with Toughness and volume derived from effect rank
- sets created object Toughness = effect rank; sets max volume from effect rank on volume table
- sustains the object — objects vanish when the effect is not maintained; character can spend PP = rank for permanence
- can trap, block, or restrain targets; restraining uses effect rank as effective Strength
- Invariant: created objects are solid and physical — they have Toughness and can be damaged and destroyed
- Collaborates with: rank (sets volume and Toughness), PP spending (for permanence), grab/restrain (combat application)

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



#### Domain Sketch

- is a *General effect* that extends the character's body or limbs to reach distant targets
- sets reach = size rank + effect rank on the distance table
- grants +1 to grab check rolls per rank due to improved leverage
- Invariant: Elongation does not grant enhanced Strength, Toughness, or any other physical enhancement beyond reach
- Collaborates with: size rank (contributes to total reach), grab check (the combat application of reach)

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



#### Domain Sketch

- is a *Control effect* that alters environmental conditions in a radius area
- offers selectable changes: Cold, Heat, Light, Visibility impairment, Movement impede
- determines radius from effect rank on the area table; additional environmental changes cost additional ranks
- Invariant: Environment does not directly damage targets — it creates hazardous or difficult conditions
- Collaborates with: effect rank (sets radius), environmental conditions (the changes made), movement speed (impede reduces it)

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



#### Domain Sketch

- is a *General effect* where each rank purchases one minor, permanently active game capability
- requires each Feature to have a concrete game-mechanical effect approved by the GM
- is distinct from descriptors — descriptors are free flavor; Features cost PP and provide real benefits
- Invariant: each rank equals exactly one Feature with exactly one minor game effect
- Collaborates with: GM approval (required for each Feature definition), descriptor (conceptually adjacent but mechanically distinct)

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



#### Domain Sketch

- is a *General effect* that increases the character's size rank, gaining physical power at the cost of defenses and concealment
- applies per-rank bonuses: +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth
- applies per-2-rank changes: −1 Dodge, −1 Parry, +1 Intimidation
- applies per-8-rank bonus: +1 Speed
- is sustained; returning to normal is a free action
- Invariant: Growth is sustained — if disrupted, the character immediately returns to normal size
- Collaborates with: size rank (the change driver), Strength/Stamina/Dodge/Parry/Stealth (the traits modified), sustained duration

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



#### Domain Sketch

- is a *General effect* that removes damage conditions from a willing target
- makes a check vs. DC 10; each degree of success removes one condition from most severe
- stabilizes a dying character as part of its effect
- cannot be used on the same target more than once per scene
- does not function on targets incapable of natural recovery (constructs, undead — unless modified)
- Invariant: Healing removes conditions in order from most severe to least; it cannot skip conditions
- Collaborates with: damage conditions (the output), stabilize (dying target special case), scene (the reuse boundary)

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



#### Domain Sketch

- is a *Control effect* that creates false sensory impressions for targets in perception range
- costs 1–5 pp/rank depending on number of sense types covered; each additional sense type adds 1 pp/rank
- allows an Insight check (DC 10 + rank) to detect the illusion — success reveals falsehood but does not remove it
- has no physical substance — cannot block movement, cause damage, or provide cover
- is maintained and altered as a free action each turn
- Invariant: Illusions cannot cause actual harm or provide real physical barriers
- Collaborates with: sense type (the dimension of the illusion), Insight check (the detection mechanism), sustained duration

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



#### Domain Sketch

- is a *General effect* with 4 progressive forms representing decreasing physicality
- form 1 (Fluid): liquid-like; form 2 (Gaseous): gas-like; form 3 (Energy): energy-like; form 4 (Incorporeal): immaterial
- allows switching between available forms as a free action
- form 4 (Incorporeal) allows passing through solid matter and ignoring most physical effects
- is sustained; returning to normal is a free action
- Invariant: higher rank forms include all lower rank capabilities; you must purchase ranks in order
- Collaborates with: descriptor (defines the fiction of each form), sustained duration, Affects Insubstantial extra (for others to affect an Insubstantial character)

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



#### Domain Sketch

- is a *General effect* that accelerates completion of routine tasks
- reduces the time rank of routine tasks by 1 per rank; at high ranks, hours become minutes, minutes become seconds
- does not affect non-routine tasks (those requiring checks) or movement speed
- Invariant: Quickness only applies to routine tasks; any task requiring a roll is not affected
- Collaborates with: time rank (the reduction target), routine check (the scope of tasks affected)

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



#### Domain Sketch

- is a *General effect* that decreases the character's size rank, improving defenses and stealth at cost of Strength and reach
- applies per-4-rank size category reduction
- applies per-rank bonuses: +1 Stealth; per-2-rank changes: +1 Dodge, +1 Parry, −1 Speed, −1 Intimidation
- reduces Strength for size-based purposes per size category reduction
- Invariant: Shrinking is sustained — returning to normal is a free action
- Collaborates with: size rank (the change driver), Dodge/Parry/Stealth/Speed (the traits modified), sustained duration

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



#### Domain Sketch

- is a *Control effect* that calls an independently acting minion
- defines minion as having power points = effect rank × 15 and power level ≤ effect rank
- applies dazed condition to the minion on arrival (standard action only on first turn)
- directs the minion with a move action each turn; minion otherwise follows last instructions
- dismisses the minion if it is incapacitated; the summoner can re-summon later
- Invariant: minion PL cannot exceed the Summon effect rank; minion PP is fixed at rank × 15
- Collaborates with: effect rank (sets minion PP and PL cap), dazed condition (on arrival), move action (directing cost), incapacitated condition (dismissal trigger)

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



#### Domain Sketch

- is a *Control effect* that changes one type of object into another type at close range
- scales cost by scope: 2 pp/rank (narrow: one substance to one), up to 5 pp/rank (broad: anything to anything)
- determines transformable mass from effect rank on the mass table (rank − 6)
- allows inanimate objects to be transformed without resistance; living targets make Fortitude checks
- is sustained — transformation reverts when the effect ends unless the Continuous extra is applied
- Invariant: Transform requires a defined target type and result type at acquisition (or defined scope for broad transforms)
- Collaborates with: effect rank (sets mass limit), Fortitude (living target resistance), sustained duration (reversibility), Continuous extra (permanence)

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



#### Domain Sketch

- is a *General effect* that provides a pool of power points the character can allocate to any effects of a defined type or descriptor
- sets pool size = effect rank × 5 power points; any effects of the defined type can be built from this pool
- reallocates the pool as a standard action; all effects built from the pool are subject to PL limits
- resets the pool if the effect is not maintained (all active allocated effects end)
- Invariant: the pool size is exactly rank × 5; Variable-built effects cannot exceed PL limits
- Collaborates with: effect rank (sets pool size), PP pool (the allocatable resource), PL limits (the constraint on built effects), sustained duration

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



#### Domain Sketch

- is the *container concept* for a collection of Alternate Effects that share a cost pool under mutual exclusivity
- enforces the rule: only one effect in the Array can be active at a time (for non-Dynamic effects)
- propagates disable state: if any effect in the Array is Nullified or disabled, all are equally affected
- allows switching between effects as a free action once per turn
- Invariant: an Array requires at least one base effect and at least one Alternate Effect to be meaningful
- Collaborates with: Alternate Effect (the variants it contains), Dynamic Alternate Effect (the simultaneous variant), Nullify (the propagation trigger), free action (the switch mechanism)

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


#### Domain Sketch

- is a *variant effect in a Power Array* that can substitute for the primary effect at flat cost
- costs 1 flat point per Alternate Effect added to the Array
- must have a total cost (all extras, flaws, ranks included) ≤ the primary effect's total cost
- cannot be a permanent effect — permanent effects cannot be switched in/out
- Invariant: only one Alternate Effect (or the primary) can be active at a time
- Collaborates with: Array (the container), flat modifier (the cost mechanism), primary effect (the cost ceiling), mutual exclusivity rule
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


#### Domain Sketch

- is a *variant of Alternate Effect* that can share power points with other Dynamic effects and operate simultaneously at reduced effectiveness
- costs 2 flat points per Dynamic Alternate Effect (the base effect costs 1 extra point to become dynamic)
- allows point reallocation among Dynamic effects once per turn as a free action
- operates at reduced effectiveness when sharing — combined allocation cannot exceed the Array pool total
- Invariant: Dynamic effects CAN operate simultaneously; standard Alternate Effects cannot
- Collaborates with: Array (the container), power points (shared resource), free action (reallocation mechanism), pool size (upper limit)
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
