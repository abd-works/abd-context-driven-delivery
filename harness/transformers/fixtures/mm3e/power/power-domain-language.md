---
state: domain-language
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

### effect

#### Domain Language

- An effect is the named, rules-defined game unit that produces a specific superheroic capability — it is the atomic building block from which all powers are constructed.
- Every effect has five fixed properties assigned at acquisition: type, action, range, duration, and cost per rank.
- Effects are acquired in ranks; higher rank means greater scale, distance, or intensity of the effect.
- The effect's stat block defaults (type, action, range, duration) can be changed by applying extras and flaws that alter those properties.
- Players name their powers freely; the effect is the underlying mechanical structure the GM and rules operate on.
- Multiple effects can be combined under one named power; each effect pays its own cost regardless of grouping.

#### References

**Ref — Ch6 Powers**
Source: context/rules/HeroesHandbook-rules__chunk_082.md
Locator: lines 5118-5192
Extract: whole

**Ref — Acquiring Powers**
Source: context/rules/HeroesHandbook-rules__chunk_083.md
Locator: lines 5193-5261
Extract: whole

**Ref — Effect Types**
Source: context/rules/HeroesHandbook-rules__chunk_084.md
Locator: lines 5262-5314
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

---

### power

#### Domain Language

- A power is the player-facing, named combination of one or more effects that appears on a character sheet — it is the game fiction label wrapped around the mechanical effect structure.
- Powers cost power points equal to the sum of each included effect's (cost per rank × rank) plus any flat modifiers.
- Powers must have at least one descriptor identifying their nature; descriptors are assigned at acquisition and may not be changed without GM approval or a complication.
- All powers a character possesses are always "on" unless specifically noted as sustained or requiring activation; a character cannot voluntarily turn off a permanent power.
- The GM approves all powers for series appropriateness before play; powers interact with settings, plots, and genre conventions.
- "Power" in common speech often refers to a single effect (e.g., "I have the Flight power"), but mechanically a power may bundle multiple effects under one name.

#### References

**Ref — Ch6 Powers**
Source: context/rules/HeroesHandbook-rules__chunk_082.md
Locator: lines 5118-5192
Extract: whole

**Ref — Acquiring Powers**
Source: context/rules/HeroesHandbook-rules__chunk_083.md
Locator: lines 5193-5261
Extract: whole

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

---

### power type

#### Domain Language

- Power type is the category label assigned to each effect that governs which general rules apply to it; the five types are Attack, Control, Defense, General, Movement, and Sensory.
- Attack type effects require an attack check and allow targets a resistance check; they interact with combat rules (range, modifiers, defenses).
- Defense type effects are passive or reactive; most are permanent and always active, protecting the character without action.
- Control type effects manipulate the environment, objects, or other characters through non-direct means.
- General type effects provide utility, enhancement, or transformation not fitting another category.
- Movement type effects grant locomotion modes or alter how a character moves through the world.
- Sensory type effects grant, enhance, or alter perception capabilities.

#### References

**Ref — Effect Types**
Source: context/rules/HeroesHandbook-rules__chunk_084.md
Locator: lines 5262-5314
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### base cost

#### Domain Language

- Base cost is the unmodified power-point cost per rank for an effect as printed in the rules — the starting value before any extras or flaws are applied.
- Base costs vary widely by effect scope: 1 pp/rank for simple effects (Damage, Protection), up to 7 pp/rank for versatile effects (Variable).
- Base cost is set at effect design time and cannot be changed; it reflects the inherent power of the effect at rank 1.
- Modifier math starts from base cost: extras add to it, flaws subtract from it, to produce cost per rank.

#### References

**Ref — Acquiring Powers**
Source: context/rules/HeroesHandbook-rules__chunk_083.md
Locator: lines 5193-5261
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

---

### cost per rank

#### Domain Language

- Cost per rank is the final power-point cost paid for each rank of an effect after all per-rank extras and per-rank flaws have been applied to the base cost.
- Formula: cost per rank = base cost + (sum of per-rank extras) − (sum of per-rank flaws).
- Cost per rank must be at minimum 1 power point per rank regardless of flaws applied; total power cost can never drop below 1 power point.
- Total effect cost = (cost per rank × ranks) + flat modifiers applied to the total.
- Cost per rank determines the power budget efficiency of an effect — higher cost per rank means the effect is more powerful or versatile at any given rank.

#### References

**Ref — Acquiring Powers**
Source: context/rules/HeroesHandbook-rules__chunk_083.md
Locator: lines 5193-5261
Extract: whole

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

---

### flat modifier

#### Domain Language

- A flat modifier is a modifier applied to the final total cost of a power (after cost per rank × rank) rather than to the per-rank cost — it is a fixed-point adjustment, not rank-scaled.
- Flat extras add points to the total (e.g., Accurate adds +1 pp per rank of bonus; Subtle adds +1 or +2 to total).
- Flat flaws subtract points from the total (e.g., Activation subtracts 1 or 2 points; Removable subtracts 1 point per 5 points of final cost).
- Flat modifiers apply after cost per rank is calculated; they can push total cost below the per-rank floor.
- Flat modifiers are listed in effect stat blocks or modifier entries with "flat" designation; they do not scale with rank.

#### References

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

---

### extra

#### Domain Language

- An extra is a modifier that enhances an effect beyond its default behavior — it broadens the action type, extends range, changes duration, adds properties, or otherwise improves the effect.
- Per-rank extras add their value (usually +1 per rank) to base cost to raise the cost per rank.
- Flat extras add a fixed point amount to the final total cost of the power.
- Any effect can potentially receive any extra as long as the effect doesn't already have that property and the GM approves the combination.
- When an extra changes the action type (e.g., Reaction), range (e.g., Perception), or duration (e.g., Continuous), the extra's cost reflects the degree of improvement.
- Multiple extras can stack on a single effect; the total per-rank value added is the sum of all per-rank extras applied.

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

**Ref — Affects Insubstantial**
Source: context/rules/HeroesHandbook-rules__chunk_142.md
Locator: lines 9790-9998
Extract: whole

**Ref — Extended Range**
Source: context/rules/HeroesHandbook-rules__chunk_144.md
Locator: lines 10223-10290
Extract: whole

**Ref — Increased Duration**
Source: context/rules/HeroesHandbook-rules__chunk_145.md
Locator: lines 10291-10452
Extract: whole

**Ref — Single Target**
Source: context/rules/HeroesHandbook-rules__chunk_146.md
Locator: lines 10453-10574
Extract: whole

**Ref — Secondary Effect**
Source: context/rules/HeroesHandbook-rules__chunk_147.md
Locator: lines 10575-10668
Extract: whole

**Ref — Variable Descriptor**
Source: context/rules/HeroesHandbook-rules__chunk_148.md
Locator: lines 10669-10715
Extract: whole

---

### flaw

#### Domain Language

- A flaw is a modifier that limits an effect below its default behavior — it restricts action type, reduces range, narrows applicability, or imposes conditions that make the effect less useful.
- Per-rank flaws subtract their value (usually −1 per rank) from base cost to lower the cost per rank.
- Flat flaws subtract a fixed point amount from the final total cost.
- Cost per rank cannot drop below 1 pp/rank no matter how many flaws are applied; the total power cost cannot be reduced below 1 pp total.
- Flaws must represent genuine limitations — the effect must actually be restricted about half or more of the time or in scope; cosmetic restrictions are not flaws, they are descriptors.
- Multiple flaws can stack on one effect; the total reduction is the sum of all per-rank flaw values.

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

**Ref — Activation And Permanent Effects**
Source: context/rules/HeroesHandbook-rules__chunk_149.md
Locator: lines 10716-10775
Extract: whole

**Ref — Check Examples**
Source: context/rules/HeroesHandbook-rules__chunk_150.md
Locator: lines 10776-10941
Extract: whole

**Ref — Increased Action**
Source: context/rules/HeroesHandbook-rules__chunk_151.md
Locator: lines 10942-11008
Extract: whole

**Ref — Reduced Range**
Source: context/rules/HeroesHandbook-rules__chunk_152.md
Locator: lines 11009-11059
Extract: whole

**Ref — Removable And Damage**
Source: context/rules/HeroesHandbook-rules__chunk_153.md
Locator: lines 11060-11137
Extract: whole

**Ref — Side Effect**
Source: context/rules/HeroesHandbook-rules__chunk_154.md
Locator: lines 11138-11242
Extract: whole

---

### Affliction

#### Domain Language

- Affliction is an Attack type effect that imposes a set of three progressively worsening conditions on a target who fails a resistance check.
- Default stat block: type Attack, action Standard, range Close, duration Instant, resistance Fortitude or Will (chosen at acquisition), cost 1 per rank.
- Three conditions are chosen at acquisition for degrees 1, 2, and 3 — each degree worse than the last; common sets include Hindered/Vulnerable/Defenseless or Dazed/Stunned/Incapacitated.
- A successful attack check is required before the target makes a resistance check; the degree of failure on the resistance check determines which condition applies.
- The target makes a resistance check at the end of each of their turns; success removes one degree of condition (from worst applied).
- Third-degree recovery requires a full minute (or outside aid) to remove after the Affliction itself is no longer active.
- Affliction is the primary "crowd control" attack effect — disabling rather than damaging.

#### References

**Ref — Affliction**
Source: context/rules/HeroesHandbook-rules__chunk_089.md
Locator: lines 5980-6040
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Blast (Damage, Ranged)

#### Domain Language

- Blast is a shorthand name for a Damage effect with the Ranged extra applied — it is not a separate effect type but a very common preconfigured combination.
- Stat block with Ranged extra: type Attack, action Standard, range Ranged, duration Instant, resistance Toughness, cost 2 per rank.
- A Blast attack requires a ranged attack check vs. the target's Dodge defense; on a hit, the target makes a Toughness resistance check vs. DC 15 + effect rank.
- Blast is the canonical ranged energy attack — fireballs, laser beams, projectile bursts, etc.; the descriptor names the fiction, the Damage+Ranged mechanics handle the rules.
- Because it has the Ranged extra already incorporated, Blast costs 2 per rank (base 1 + Ranged extra 1).

#### References

**Ref — Power Effects Alphabetical Descriptions (Alternate Form - Blast)**
Source: context/rules/HeroesHandbook-rules__chunk_090.md
Locator: lines 6041-6170
Extract: whole

**Ref — Damage**
Source: context/rules/HeroesHandbook-rules__chunk_097.md
Locator: lines 6652-6710
Extract: whole

---

### Burrowing

#### Domain Language

- Burrowing is a Movement type effect that grants the ability to move through earth, soil, clay, or rock.
- Stat block: type Movement, action Free, range Personal, duration Sustained, cost 1 per rank.
- Speed rank through soil = Burrowing rank − 5; clay or packed earth applies −1 penalty; solid rock applies −2 penalty (minimum speed rank 1 if Burrowing rank is high enough).
- The character can choose whether the tunnel they create is permanent or collapses behind them.
- Burrowing does not grant breathing underground; a character still needs air or appropriate Immunity.

#### References

**Ref — Burrowing**
Source: context/rules/HeroesHandbook-rules__chunk_091.md
Locator: lines 6171-6210
Extract: whole

---

### Communication

#### Domain Language

- Communication is a Sensory type effect that allows the user to send and receive information over distance via a chosen sense type medium.
- Stat block: type Sensory, action Free, range Rank range, duration Sustained, cost 4 per rank.
- Range is determined by rank on the distance table; point-to-point communication to a known location or specific person is the default mode.
- The sense type medium (radio, mental, visual, etc.) is chosen at acquisition and defines what can block or intercept the communication.
- Communication is language-dependent by default; the target must share a language with the user to exchange information.
- Communication Link (a Senses sub-effect) is a less costly alternative for two-way contact with a specific individual.

#### References

**Ref — Communication**
Source: context/rules/HeroesHandbook-rules__chunk_092.md
Locator: lines 6211-6335
Extract: whole

---

### Comprehend

#### Domain Language

- Comprehend is a Sensory type effect that grants the ability to understand and communicate in otherwise incomprehensible languages or with beings not normally capable of language exchange.
- Stat block: type Sensory, action None, range Personal, duration Permanent, cost 2 per rank.
- Each rank purchased allocates to one communication type chosen from: Animals, Languages, Machines, Objects, Plants, Spirits.
- Comprehend Languages allows reading and speaking any language; Comprehend Animals allows two-way communication with animals; Comprehend Machines allows communicating with technological devices.
- Comprehend is permanent — it is always active and requires no action to use once acquired.

#### References

**Ref — Comprehend**
Source: context/rules/HeroesHandbook-rules__chunk_093.md
Locator: lines 6336-6405
Extract: whole

---

### Concealment

#### Domain Language

- Concealment is a Sensory type effect that makes the character undetectable to a specific sense type, granting total concealment against that sense.
- Stat block: type Sensory, action Free, range Personal, duration Sustained, cost 2 per rank.
- Each sense type costs a set number of ranks: Visual costs 2 ranks per visual sense (Normal Vision, Infravision, etc.); most other senses cost 1 rank.
- Concealment from tactile (touch) sense is not possible.
- A character with total concealment vs. a given sense type cannot be perceived at all by that sense; attackers relying on that sense treat the character as if not there.
- Concealment is activated as a free action and must be sustained; dropping concentration ends it.

#### References

**Ref — Concealment**
Source: context/rules/HeroesHandbook-rules__chunk_094.md
Locator: lines 6406-6471
Extract: whole

**Ref — Concealment And Perception Range**
Source: context/rules/HeroesHandbook-rules__chunk_095.md
Locator: lines 6472-6531
Extract: whole

---

### Create

#### Domain Language

- Create is a Control type effect that allows the character to form solid, physical objects from nothing (or from a specific medium defined by the descriptor).
- Stat block: type Control, action Standard, range Ranged, duration Sustained, cost 2 per rank.
- The maximum volume of the created object is determined by the effect rank on the mass/volume rank table.
- Created objects have Toughness equal to the effect rank; they can be targeted and damaged like normal objects.
- Created objects vanish if the character does not maintain the effect (sustained duration); the character can make them permanent by expending power points equal to the rank.
- Objects created can be used to restrain, trap, or block targets; the object's Strength for restraining equals the effect rank.

#### References

**Ref — Trapping With Objects**
Source: context/rules/HeroesHandbook-rules__chunk_096.md
Locator: lines 6532-6651
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Damage

#### Domain Language

- Damage is the foundational Attack type effect — the direct, physical harm inflicted on a target through close combat.
- Stat block: type Attack, action Standard, range Close, duration Instant, resistance Toughness, cost 1 per rank.
- DC of the Toughness resistance check = 15 + Damage rank; failure means the target suffers a damage condition.
- Four degrees of failure: first (minor condition penalty), second (dazed and penalized), third (staggered and penalized), fourth (incapacitated — further hits lead to dying then dead).
- Damage by itself is a close-range effect; the Ranged extra creates Blast; the Perception extra creates effects that automatically affect targets in perception range with no attack check.
- Damage stacks with Strength for unarmed attacks; the total Damage rank includes the character's Strength modifier.

#### References

**Ref — Damage**
Source: context/rules/HeroesHandbook-rules__chunk_097.md
Locator: lines 6652-6710
Extract: whole

**Ref — Damaging Objects**
Source: context/rules/HeroesHandbook-rules__chunk_098.md
Locator: lines 6711-6783
Extract: whole

**Ref — Material Toughness**
Source: context/rules/HeroesHandbook-rules__chunk_099.md
Locator: lines 6784-6850
Extract: whole

---

### Deflect

#### Domain Language

- Deflect is a Defense type effect that allows the character to protect themselves or others from ranged attacks at a distance.
- Stat block: type Defense, action Standard (or Reaction with extra), range Ranged, duration Instant, cost 1 per rank.
- The character uses their Deflect rank (plus relevant modifiers) as their defense check instead of the normal active defense; this can protect other characters in range.
- Medium and long range penalties apply to Deflect attempts at distance.
- Deflect can intercept projectiles and energy attacks; the descriptor defines what can be deflected.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

---

### Elongation

#### Domain Language

- Elongation is a General type effect that allows the character to extend their body or limbs to reach targets or objects at a distance.
- Stat block: type General, action Free, range Personal, duration Sustained, cost 1 per rank.
- Reach extends to size rank + effect rank on the distance table; at high ranks this can reach across rooms or streets.
- Elongation grants +1 to grab checks per rank as the extended limbs improve leverage and grip.
- Elongation represents plastic, rubber, or stretching bodies but does not by itself grant increased Strength, Toughness, or other physical enhancements.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Enhanced Trait

#### Domain Language

- Enhanced Trait is a General type effect that temporarily increases an existing trait (ability, skill, defense, or other) beyond its normal value.
- Stat block: type General, action Free, range Personal, duration Sustained, cost equal to the base cost of the trait being enhanced per rank.
- The trait being enhanced must exist on the character sheet already; Enhanced Trait raises it further, subject to PL limits.
- Enhanced Trait is sustained — if the character is unable to maintain it (stunned, nullified), the trait drops back to its base value.
- Enhanced Trait can stack with extra effort for temporary further boosts, but PL limits still cap the resulting totals.

#### References

**Ref — Enhanced Trait**
Source: context/rules/HeroesHandbook-rules__chunk_101.md
Locator: lines 6892-6936
Extract: whole

---

### Environment

#### Domain Language

- Environment is a Control type effect that alters the environmental conditions in a radius area around the character or a designated point.
- Stat block: type Control, action Standard, range Rank range, duration Sustained, cost 1–2 per rank depending on effects.
- Environmental changes possible: Cold (temperature drop), Heat (temperature rise), Light (illuminate darkness), Visibility impairment (fog, darkness), and Movement impede (difficult terrain).
- The radius of the environment effect is determined by the effect rank on the area/distance table.
- Multiple environment effects can be stacked on a single Environment effect; each additional environmental change costs an additional rank.

#### References

**Ref — Environment**
Source: context/rules/HeroesHandbook-rules__chunk_102.md
Locator: lines 6937-6985
Extract: whole

**Ref — Energy Control**
Source: context/rules/HeroesHandbook-rules__chunk_103.md
Locator: lines 6986-7064
Extract: whole

---

### Feature

#### Domain Language

- Feature is a General type effect that represents minor, single-rank capabilities that have an actual game effect but don't fit another effect category.
- Stat block: type General, action None, range Personal, duration Permanent, cost 1 per rank (each rank = one Feature).
- Each Feature provides one minor ability that has a concrete (though usually small) mechanical effect — the ability is defined at acquisition with GM approval.
- Features are distinct from descriptors: descriptors are free flavor labels; Features cost power points and provide actual game benefits.
- Examples: internal clock (always know exact time), photographic memory (+5 bonus on appropriate checks), mimicry of voices.

#### References

**Ref — Feature**
Source: context/rules/HeroesHandbook-rules__chunk_105.md
Locator: lines 7117-7186
Extract: whole

**Ref — Extra Limbs**
Source: context/rules/HeroesHandbook-rules__chunk_104.md
Locator: lines 7065-7116
Extract: whole

---

### Flight

#### Domain Language

- Flight is a Movement type effect that grants the ability to fly through the air.
- Stat block: type Movement, action Free, range Personal, duration Sustained, cost 2 per rank.
- Flight speed rank equals the effect rank on the speed table (e.g., rank 5 = ~60 mph).
- Hovering is available by default; the character can remain stationary in midair.
- Activating Flight is a free action; moving while flying requires a move action as normal.
- Flight is sustained — if the character is unable to maintain it, they begin to fall.

#### References

**Ref — Flight**
Source: context/rules/HeroesHandbook-rules__chunk_106.md
Locator: lines 7187-7254
Extract: whole

**Ref — Force Field**
Source: context/rules/HeroesHandbook-rules__chunk_107.md
Locator: lines 7255-7315
Extract: whole

---

### Growth

#### Domain Language

- Growth is a General type effect that increases the character's physical size, improving physical abilities at the cost of defenses and stealth.
- Stat block: type General, action Free, range Personal, duration Sustained, cost 2 per rank.
- Per rank: +1 Strength, +1 Stamina, +1 mass rank, −1 Stealth, and size category increases every 4 ranks.
- Per 2 ranks: −1 Dodge, −1 Parry, +1 Intimidation.
- Per 8 ranks: +1 Speed rank (larger stride).
- Growth is sustained; returning to normal size is a free action.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Healing

#### Domain Language

- Healing is a General type effect that removes damage conditions from a willing target.
- Stat block: type General, action Standard, range Close, duration Instant, cost 2 per rank.
- A Healing check is made vs. DC 10; each degree of success removes one damage condition starting from the most severe.
- Healing also stabilizes a dying character (removes the dying condition).
- Healing does not work on targets who cannot recover naturally on their own (constructs, undead by default unless modified).
- Healing cannot be used on the same target more than once per scene; repeated attempts have no additional effect until the target takes new damage.

#### References

**Ref — Healing**
Source: context/rules/HeroesHandbook-rules__chunk_108.md
Locator: lines 7316-7409
Extract: whole

---

### Illusion

#### Domain Language

- Illusion is a Control type effect that creates false sensory impressions perceived by those in range.
- Stat block: type Control, action Standard, range Perception, duration Sustained, cost 1–5 per rank depending on sense types covered.
- Cost scales with number of sense types: 1 pp/rank for 1 sense type, up to 5 pp/rank for all sense types simultaneously.
- An Insight check vs. DC 10 + effect rank allows a target to recognize the illusion; success reveals it as false but it remains visible.
- Illusions have no physical substance — they cannot cause real damage, block movement, or provide cover.
- Maintaining an illusion is free action; the character can alter or move the illusion with a free action each turn.

#### References

**Ref — Illusion**
Source: context/rules/HeroesHandbook-rules__chunk_109.md
Locator: lines 7410-7457
Extract: whole

**Ref — Maintaining Illusions**
Source: context/rules/HeroesHandbook-rules__chunk_110.md
Locator: lines 7458-7497
Extract: whole

---

### Immortality

#### Domain Language

- Immortality is a Defense type effect that allows the character to return from death.
- Stat block: type Defense, action None, range Personal, duration Permanent, cost 2 per rank.
- Recovery time after death is a time rank equal to (19 − Immortality rank); at rank 10 recovery takes about an hour; at rank 20 the character recovers at the start of each action round.
- Immortality does not prevent death — the character can still be killed; it only enables return afterward.
- Immortality is permanent and always active; it cannot be deactivated voluntarily.

#### References

**Ref — Immortality**
Source: context/rules/HeroesHandbook-rules__chunk_111.md
Locator: lines 7498-7571
Extract: whole

---

### Immunity

#### Domain Language

- Immunity is a Defense type effect that grants automatic success on resistance checks against a specified set of effects or hazards.
- Stat block: type Defense, action None, range Personal, duration Permanent, cost 1 per rank.
- Rank cost scales by scope: narrow immunity costs 1 rank (e.g., one environmental hazard), broad immunity costs more (e.g., all Fortitude effects = 30 ranks, all Toughness effects = 80 ranks).
- Immunity is always active and provides complete protection against the specified effect set; there is no check required.
- Partial immunity (half effect) can be purchased for half the full rank cost.
- Immunity to Life Support (cold, heat, pressure, radiation, suffocation, starvation, thirst) costs 10 ranks total — a common purchase for alien or energy beings.

#### References

**Ref — Immunity**
Source: context/rules/HeroesHandbook-rules__chunk_112.md
Locator: lines 7572-7614
Extract: whole

**Ref — Degrees Of Immunity**
Source: context/rules/HeroesHandbook-rules__chunk_113.md
Locator: lines 7615-7665
Extract: whole

---

### Insubstantial

#### Domain Language

- Insubstantial is a General type effect that allows the character to become partially or completely non-physical.
- Stat block: type General, action Free, range Personal, duration Sustained, cost 5 per rank (4 ranks total for all forms).
- Four forms in order of progression: rank 1 Fluid (liquid), rank 2 Gaseous, rank 3 Energy (light, electricity, etc.), rank 4 Incorporeal (immaterial, can pass through solid matter).
- Incorporeal (rank 4) allows passing through solid matter and ignoring most physical effects; attack and defense interact with other Insubstantial characters and effects with appropriate descriptors.
- The character can switch between available forms as a free action.
- Insubstantial is sustained; reversion to normal is a free action.

#### References

**Ref — Insubstantial**
Source: context/rules/HeroesHandbook-rules__chunk_114.md
Locator: lines 7666-7733
Extract: whole

**Ref — Insubstantial Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_115.md
Locator: lines 7734-7818
Extract: whole

---

### Leaping

#### Domain Language

- Leaping is a Movement type effect that greatly extends a character's jumping distance and height.
- Stat block: type Movement, action Free, range Personal, duration Instant, cost 1 per rank.
- Jump distance rank = Leaping rank − 2 on the distance table; high ranks enable mile-spanning leaps.
- A character landing within their maximum jump distance takes no damage from the landing.
- Leaping does not grant flight between leaps — the character follows a ballistic arc and cannot change direction mid-air.

#### References

**Ref — Leaping**
Source: context/rules/HeroesHandbook-rules__chunk_116.md
Locator: lines 7819-7887
Extract: whole

---

### Luck Control

#### Domain Language

- Luck Control is a Control type effect that allows the character to manipulate hero points and the Luck system.
- Stat block: type Control, action Reaction, range Perception, duration Instant, cost 3 per rank.
- Each rank grants one capability; options include: spend a hero point on behalf of another character, transfer a hero point, negate a hero point use by another character, or force a target to re-roll (spending a hero point).
- Luck Control operates at perception range — the user must be able to perceive the target.
- Luck Control interacts with the hero point economy and can shift narrative advantage.

#### References

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Mind Reading

#### Domain Language

- Mind Reading is a Sensory type effect that allows the character to access the thoughts of a target.
- Stat block: type Sensory, action Standard, range Perception, duration Sustained, cost 2 per rank.
- Initiating Mind Reading requires an opposed effect check vs. the target's Will defense.
- Degree of success determines depth of access: first degree (surface thoughts), second (personal thoughts), third (memories), fourth (subconscious).
- The target makes a Will resistance check at the end of each of their turns; success breaks the contact.
- Mind Reading is sustained — the character must maintain concentration; if broken, the contact ends.

#### References

**Ref — Mind Reading**
Source: context/rules/HeroesHandbook-rules__chunk_118.md
Locator: lines 7954-7997
Extract: whole

**Ref — Mind Reading And Deception**
Source: context/rules/HeroesHandbook-rules__chunk_119.md
Locator: lines 7998-8037
Extract: whole

**Ref — Mental Blast**
Source: context/rules/HeroesHandbook-rules__chunk_117.md
Locator: lines 7888-7953
Extract: whole

**Ref — Mind Control**
Source: context/rules/HeroesHandbook-rules__chunk_120.md
Locator: lines 8038-8096
Extract: whole

---

### Move Object

#### Domain Language

- Move Object is a Control type effect that allows the character to lift and move objects or unwilling targets at range using telekinesis, magnetism, or similar force.
- Stat block: type Control, action Standard, range Ranged, duration Sustained, cost 2 per rank.
- Effective Strength for lifting and moving equals the effect rank; objects up to the corresponding mass rank can be manipulated.
- Move Object cannot be used to directly damage a target; it can be used for disarm, grab, or trip maneuvers at range.
- A target can resist being moved with a Strength check vs. the effect rank; objects do not resist.
- Move Object is sustained; the object falls (or the grab ends) if concentration is broken.

#### References

**Ref — Move Object**
Source: context/rules/HeroesHandbook-rules__chunk_122.md
Locator: lines 8155-8245
Extract: whole

---

### Movement

#### Domain Language

- Movement is a Movement type effect that grants one or more special locomotion modes, each at 1 rank per mode.
- Stat block: type Movement, action Free, range Personal, duration Sustained, cost 2 per rank.
- Each rank of Movement grants access to one movement mode; available modes include: Dimension Travel, Environmental Adaptation (a specific environment), Permeate, Safe Fall, Slithering, Space Travel, Sure-Footed, Swinging, Time Travel, Trackless, Wall-Crawling, Water-Walking.
- Movement modes operate according to their own specific sub-rules; Dimension Travel and Time Travel interact with the GM's setting.
- Movement is sustained; losing it ends the movement mode until reactivated.

#### References

**Ref — Dimension Travel**
Source: context/rules/HeroesHandbook-rules__chunk_123.md
Locator: lines 8246-8298
Extract: whole

**Ref — Space Travel**
Source: context/rules/HeroesHandbook-rules__chunk_124.md
Locator: lines 8299-8352
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Nullify

#### Domain Language

- Nullify is an Attack type effect that counters and disables other power effects matching a specified descriptor.
- Stat block: type Attack, action Standard, range Ranged, duration Instant, cost 1 per rank.
- A ranged attack check is required; on a hit, the target makes an opposed check of their effect rank (or Will, whichever is higher) vs. Nullify rank.
- Success counters (turns off) the targeted effect; the target can re-activate countered effects normally on their next action.
- Nullify targets effects by descriptor; if the user applies Broad or Simultaneous extras, it can affect multiple effects at once.
- The user can voluntarily end a Nullify effect they maintain; countered effects that are sustained resume when the target re-activates them.

#### References

**Ref — Nullify**
Source: context/rules/HeroesHandbook-rules__chunk_125.md
Locator: lines 8353-8457
Extract: whole

---

### Protection

#### Domain Language

- Protection is a Defense type effect that provides additional Toughness, hardening the character against damage.
- Stat block: type Defense, action None, range Personal, duration Permanent, cost 1 per rank.
- Each rank adds +1 to the character's Toughness defense; this stacks with the character's base Stamina-derived Toughness.
- Protection is permanent and always active; it cannot be deactivated, cannot benefit from extra effort, and stacks with Impervious if that extra is applied.
- Protection is the most efficient single-purpose damage reduction effect in the system.

#### References

**Ref — Protection**
Source: context/rules/HeroesHandbook-rules__chunk_126.md
Locator: lines 8458-8500
Extract: whole

---

### Quickness

#### Domain Language

- Quickness is a General type effect that allows the character to perform routine tasks at superhuman speed.
- Stat block: type General, action Free, range Personal, duration Sustained, cost 1 per rank.
- Each rank reduces the time rank of routine tasks by 1; at high ranks, actions that normally take hours take minutes or seconds.
- Quickness does not affect non-routine tasks (those requiring checks) or movement speed — use Speed for that.
- At very high Quickness ranks, routine tasks effectively become free actions within the same time frame.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

---

### Regeneration

#### Domain Language

- Regeneration is a Defense type effect that allows the character to recover from damage conditions over time.
- Stat block: type Defense, action None, range Personal, duration Permanent, cost 1 per rank.
- Recovery proceeds in two phases: first, Toughness penalties are removed at rate of 1 per (rank × minutes); then damage conditions are removed at rate of 1 per (rank × minutes) starting from the most severe.
- Regeneration is permanent and always active — it cannot be deactivated.
- Regeneration works independently of normal recovery rules; characters with Regeneration do not need rest or medical attention to recover from damage.

#### References

**Ref — Regeneration**
Source: context/rules/HeroesHandbook-rules__chunk_127.md
Locator: lines 8501-8647
Extract: whole

---

### Remote Sensing

#### Domain Language

- Remote Sensing is a Sensory type effect that displaces the character's senses to a distant location, allowing them to perceive events there.
- Stat block: type Sensory, action Free, range Rank range, duration Sustained, cost 1–5 per rank based on sense types.
- While Remote Sensing is active, the character's normal senses are suppressed; they perceive only through the displaced senses at the remote location.
- The character is considered vulnerable while Remote Sensing is active (active defenses halved) because their attention is elsewhere.
- Sense type cost matches Communication/Illusion: 1 rank for one sense type, up to 5 ranks for all senses.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

---

### Senses

#### Domain Language

- Senses is a Sensory type effect that allocates ranks to a variety of sensory enhancements, new sense types, or perceptive capabilities.
- Stat block: type Sensory, action None, range Personal, duration Permanent, cost 1 per rank.
- Each rank buys one enhancement from a large menu; options include: Accurate, Acute, Analytical, Awareness (of a specific phenomenon), Communication Link, Counters Concealment, Counters Illusion, Danger Sense, Darkvision, Detect (a specific type of phenomenon), Direction Sense, Distance Sense, Extended, Infravision, Low-Light Vision, Microscopic Vision, Penetrates Concealment, Postcognition, Precognition, Radio, Radius, Ranged, Rapid, Time Sense, Tracking, Ultra-Hearing, Ultravision.
- Senses is the catch-all effect for any perceptive capability not covered by a dedicated effect.
- Senses is permanent — purchased enhancements are always active unless specified otherwise.

#### References

**Ref — Senses**
Source: context/rules/HeroesHandbook-rules__chunk_128.md
Locator: lines 8648-8698
Extract: whole

**Ref — Communication Link**
Source: context/rules/HeroesHandbook-rules__chunk_129.md
Locator: lines 8699-8760
Extract: whole

**Ref — Direction Sense**
Source: context/rules/HeroesHandbook-rules__chunk_130.md
Locator: lines 8761-8806
Extract: whole

**Ref — Penetrates Concealment**
Source: context/rules/HeroesHandbook-rules__chunk_131.md
Locator: lines 8807-8917
Extract: whole

**Ref — Time Sense**
Source: context/rules/HeroesHandbook-rules__chunk_132.md
Locator: lines 8918-9006
Extract: whole

**Ref — Sense Types**
Source: context/rules/HeroesHandbook-rules__chunk_085.md
Locator: lines 5315-5354
Extract: whole

---

### Shrinking

#### Domain Language

- Shrinking is a General type effect that decreases the character's physical size, improving defenses and stealth at the cost of Strength and reach.
- Stat block: type General, action Free, range Personal, duration Sustained, cost 2 per rank.
- Per 4 ranks: −1 size category.
- Per rank: +1 Stealth, −1 Strength (for size-based purposes), −1 Intimidation per 2 ranks.
- Per 2 ranks: +1 active defense (Dodge and Parry), −1 Speed.
- At very small sizes, the character may be difficult to target; at extreme sizes, they may interact with the world differently (GM discretion).

#### References

**Ref — Shrinking**
Source: context/rules/HeroesHandbook-rules__chunk_133.md
Locator: lines 9007-9051
Extract: whole

---

### Speed

#### Domain Language

- Speed is a Movement type effect that increases the character's ground movement speed.
- Stat block: type Movement, action Free, range Personal, duration Sustained, cost 1 per rank.
- Ground speed rank equals the effect rank on the speed table; ranks add to the character's base speed.
- Speed improves all ground-speed-based movement including sprinting, charging, and any movement that derives from the character's base speed.
- Speed does not grant flight, swimming, or other non-ground movement modes; those require separate effects.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

---

### Summon

#### Domain Language

- Summon is a Control type effect that calls a minion (independently acting character) under the summoner's direction.
- Stat block: type Control, action Standard, range Close, duration Sustained, cost 2 per rank.
- The summoned minion has power points = effect rank × 15; the minion's power level cannot exceed the effect rank.
- The minion is dazed when summoned (only a standard action on its first turn); after that it acts on the summoner's initiative.
- Directing the minion is a move action for the summoner; the minion otherwise acts on its own following the character's last instructions.
- If the minion is incapacitated, it disappears; the summoner can re-summon it later (same action and cost).
- Summon (Multiple) extra allows multiple minions simultaneously; cost scales with number of simultaneous minions.

#### References

**Ref — Summon**
Source: context/rules/HeroesHandbook-rules__chunk_134.md
Locator: lines 9052-9210
Extract: whole

**Ref — Summon And Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_135.md
Locator: lines 9211-9257
Extract: whole

---

### Swimming

#### Domain Language

- Swimming is a Movement type effect that grants enhanced aquatic movement speed.
- Stat block: type Movement, action Free, range Personal, duration Sustained, cost 1 per rank.
- Water speed rank = effect rank − 2 on the speed table.
- Swimming allows routine Athletics (Swimming) checks to be handled automatically; the character does not need to roll for routine swimming.
- Swimming does not grant underwater breathing — a character still suffocates without Immunity (Suffocation) or a related effect.

#### References

**Ref — Swimming**
Source: context/rules/HeroesHandbook-rules__chunk_136.md
Locator: lines 9258-9382
Extract: whole

---

### Teleport

#### Domain Language

- Teleport is a Movement type effect that allows the character to instantly move from one location to another.
- Stat block: type Movement, action Move, range Rank range, duration Instant, cost 2 per rank.
- The destination must be either a well-known location or one the character can accurately sense; blind teleporting to unknown locations risks "teleport error" (GM discretion).
- The character carries mass rank 0 worth of additional mass by default; the Mass extra extends this.
- When teleporting, the character retains their velocity from before the teleport (momentum is conserved).
- Teleport is instant — the character simply appears at the destination; there is no transit time.

#### References

**Ref — Power Effects Summary Table (N-W) & Countering**
Source: context/rules/HeroesHandbook-rules__chunk_088.md
Locator: lines 5800-5979
Extract: whole

---

### Transform

#### Domain Language

- Transform is a Control type effect that changes one type of object into another type.
- Stat block: type Control, action Standard, range Close, duration Sustained, cost 2–5 per rank depending on scope.
- Cost depends on breadth of transformation: 2 pp/rank for narrow (one substance to one substance), 3 pp/rank for broader, up to 5 pp/rank for anything to anything.
- Mass that can be transformed = effect rank − 6 on the mass rank table; higher ranks transform larger volumes.
- Inanimate objects do not resist transformation; living targets make a Fortitude check to resist.
- Sustained duration means the transformation reverses when the effect ends; permanent transformation requires the Continuous extra.

#### References

**Ref — Destructive Transformations**
Source: context/rules/HeroesHandbook-rules__chunk_137.md
Locator: lines 9383-9455
Extract: whole

**Ref — Morph**
Source: context/rules/HeroesHandbook-rules__chunk_121.md
Locator: lines 8097-8154
Extract: whole

---

### Variable

#### Domain Language

- Variable is a General type effect that provides a pool of power points the character can allocate to any effects matching a defined type or descriptor set.
- Stat block: type General, action Standard, range Personal, duration Sustained, cost 7 per rank.
- The pool size = effect rank × 5 power points; these can be allocated to any effects of the appropriate type.
- Allocation requires a standard action to change; effects built from the pool are subject to PL limits.
- The descriptor or type of effects that Variable can emulate must be defined at acquisition and meaningfully limits the scope.
- If the Variable effect is not maintained, all allocated effects end and the pool "resets."

#### References

**Ref — Variable**
Source: context/rules/HeroesHandbook-rules__chunk_138.md
Locator: lines 9456-9560
Extract: whole

---

### Weaken

#### Domain Language

- Weaken is an Attack type effect that temporarily reduces a specific trait of the target.
- Stat block: type Attack, action Standard, range Close, duration Instant, resistance Fortitude or Will (depending on trait type), cost 1 per rank.
- On a failed resistance check, the target's specified trait is reduced by the degree of failure, up to the Weaken rank.
- Weaken is cumulative — multiple applications stack up to the effect rank maximum reduction.
- Targets recover at 1 point of the reduced trait per round (automatic recovery without action).
- Weaken can target any trait — abilities, defenses, or other derived values; the targeted trait is chosen at acquisition.

#### References

**Ref — Weaken**
Source: context/rules/HeroesHandbook-rules__chunk_139.md
Locator: lines 9561-9684
Extract: whole

---

### Accurate

#### Domain Language

- Accurate is an extra that improves the character's attack check bonus for a specific effect.
- Type: flat extra; cost 1 point per +2 attack bonus (i.e., each rank of Accurate = +2 to attack checks, costing 1 flat point per rank of bonus).
- Accurate is applied to an effect at acquisition; it improves attack check rolls with that effect only.
- The attack bonus from Accurate cannot push the character's attack bonus beyond PL × 2 (PL limits cap total attack bonus).
- Accurate is commonly used to make area or perception effects more reliable in targeted scenarios via the Attack extra combination.

#### References

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Area

#### Domain Language

- Area is an extra that removes the need for an attack check and instead affects all targets in a defined area.
- Type: per-rank extra; cost +1 per rank.
- Targets in the area make a Dodge resistance check (DC 10 + effect rank); success reduces the effect's rank by half for them.
- Area shapes available: Burst (spherical), Cloud (lingering), Cone, Cylinder, Line, Perception (all perceiving the user), Shapeable.
- Area effects cannot be used to target a specific individual within the area and exclude others — everyone in the area is affected.
- Area is one of the most powerful extras in terms of tactical impact; it eliminates the attack-check bottleneck for effects at the cost of giving targets a Dodge save.

#### References

**Ref — Affects Insubstantial**
Source: context/rules/HeroesHandbook-rules__chunk_142.md
Locator: lines 9790-9998
Extract: whole

**Ref — Power Effects Summary Table (A-M)**
Source: context/rules/HeroesHandbook-rules__chunk_087.md
Locator: lines 5398-5799
Extract: whole

---

### Multiattack

#### Domain Language

- Multiattack is an extra that allows an effect to target multiple opponents or strike a single target multiple times in one action.
- Type: per-rank extra; cost +1 per rank.
- Against a single target: each additional degree of success on the attack check adds +2 to the effect DC (at 2 degrees) or +5 (at 3+ degrees).
- Against multiple targets: the character makes one attack roll and applies a penalty equal to the number of targets being attacked; each target whose Dodge the attack roll exceeds is hit.
- Multiattack represents machine-gun fire, multiple-fist attacks, or rapid-fire energy bursts.

#### References

**Ref — Single Target**
Source: context/rules/HeroesHandbook-rules__chunk_146.md
Locator: lines 10453-10574
Extract: whole

---

### Penetrating

#### Domain Language

- Penetrating is an extra that allows an effect to overcome Impervious resistance.
- Type: flat extra; cost 1 point per rank of Penetrating.
- Impervious resistance normally blocks effects whose ranks are equal to or lower than the Impervious rank; Penetrating overcomes this protection to degree equal to the Penetrating rank.
- A target with Impervious Toughness must resist damage rank equal to the Penetrating rank even if the attack rank is normally blocked.
- Penetrating is primarily used to make attacks effective against heavily armored or fortified targets.

#### References

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

---

### Activation

#### Domain Language

- Activation is a flaw that requires the character to spend an action activating the power before any of its effects become available.
- Type: flat flaw; cost −1 (move action activation) or −2 (standard action activation) to the power's total cost.
- Activation applies to the entire power — all effects within the power require the activation first.
- If the power is Nullified or deactivated, the character must spend the activation action again to re-enable it.
- Activation is appropriate for powered armor, gadget belts, or equipment that requires preparation before use.

#### References

**Ref — Activation And Permanent Effects**
Source: context/rules/HeroesHandbook-rules__chunk_149.md
Locator: lines 10716-10775
Extract: whole

---

### Check Required

#### Domain Language

- Check Required is a flaw that mandates a successful skill or ability check before the effect can function.
- Type: flat flaw; cost −1 per rank of the effect.
- The check DC is 10 + any additional ranks beyond the first; natural 1 always fails regardless of modifiers.
- On a failed check the effect does not activate; on a success, the character gains 1 effective rank per point exceeding the DC.
- Check Required is in addition to any other checks the effect normally requires (e.g., attack checks).

#### References

**Ref — Check Examples**
Source: context/rules/HeroesHandbook-rules__chunk_150.md
Locator: lines 10776-10941
Extract: whole

---

### Limited

#### Domain Language

- Limited is a flaw that restricts an effect to function only under certain circumstances, against certain targets, or in certain conditions.
- Type: per-rank flaw; cost −1 per rank.
- The limitation must genuinely reduce the effect's utility to approximately half or less of its unrestricted use; the GM determines whether a proposed limitation qualifies.
- Limited is distinct from a complication: a complication is a narrative restriction with hero point rewards; Limited is a mechanical cost reduction.
- Examples: "only against living targets," "only at night," "only when emotionally agitated."

#### References

**Ref — Applying Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_140.md
Locator: lines 9685-9745
Extract: whole

---

### Removable

#### Domain Language

- Removable is a flaw that represents a power built into a device or object that can be taken away from the character.
- Type: flat flaw; cost −1 per 5 points of the power's final cost (or −2 per 5 points if easily removable).
- The item can be taken from the character when they are both stunned and defenseless, or via a successful disarm or grab maneuver.
- Removable applies to the entire power — all effects within the power are unavailable if the item is taken.
- The device can itself be damaged using the object damage rules; its Toughness is the character's power level.

#### References

**Ref — Removable And Damage**
Source: context/rules/HeroesHandbook-rules__chunk_153.md
Locator: lines 11060-11137
Extract: whole

---

### descriptor

#### Domain Language

- A descriptor is a free label attached to a power that identifies its nature, medium, source, or results in thematic and mechanical terms.
- Descriptors are not modifiers — they cost no power points; they are assigned to a power at acquisition and inform how it interacts with Immunity, Nullify, and narrative situations.
- Descriptors can be broad (fire, electricity, magic) or specific (Greek divine fire, mutant electromagnetic field).
- At minimum every power must have at least one descriptor; most have several (e.g., origin descriptor + source descriptor + result descriptor).
- Descriptors determine what Nullify counters, what Immunity blocks, and how environmental and narrative effects interact with the power.

#### References

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

**Ref — Applying Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_156.md
Locator: lines 11447-11497
Extract: whole

**Ref — Changing Descriptors In Play**
Source: context/rules/HeroesHandbook-rules__chunk_157.md
Locator: lines 11498-11554
Extract: whole

---

### origin descriptor

#### Domain Language

- An origin descriptor identifies how a character came to have their powers — the narrative source of the character's abilities.
- Common origin descriptors: Accidental (radiation exposure, lab accident), Bestowed (given by an external force), Invented (technological creation), Mutant (innate genetic ability), Training (developed through practice and skill).
- Origin descriptors rarely have mechanical effects but inform narrative interactions and may affect certain plot-level Nullify or Immunity interactions.
- A character typically has one origin descriptor that applies to their entire power set.

#### References

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

---

### source descriptor

#### Domain Language

- A source descriptor identifies the energy or force that a power draws upon to function.
- Common source descriptors: Biological, Cosmic, Divine, Extradimensional, Magical, Moral, Psionic, Technological.
- Source descriptors have mechanical significance: a Nullify effect targeting "magical effects" would counter all powers with a Magical source descriptor; Immunity to "magical effects" would block them.
- A power can have multiple source descriptors if it draws on more than one source.

#### References

**Ref — Types Of Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_155.md
Locator: lines 11243-11446
Extract: whole

**Ref — Applying Descriptors**
Source: context/rules/HeroesHandbook-rules__chunk_156.md
Locator: lines 11447-11497
Extract: whole

---

### Array

#### Domain Language

- An Array is a collection of Alternate Effects (and optionally Dynamic Alternate Effects) grouped together under one power that share a single cost pool.
- All effects in an Array are mutually exclusive — only one can be active at a time; activating one automatically deactivates the others.
- Switching between effects within an Array is a free action, usable once per turn.
- If any one effect in the Array is disabled, Nullified, or otherwise affected, all effects in the Array are equally affected.
- The Array structure allows a character to have many varied effects for less total cost than purchasing each independently.

#### References

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

---

### Alternate Effect

#### Domain Language

- An Alternate Effect is a variant effect purchased at flat cost that allows the character to swap out the primary effect for an alternate one within a power Array.
- Type: flat extra; cost 1 point per Alternate Effect added.
- The total point cost of the alternate effect cannot exceed the total point cost of the primary (base) effect in the Array.
- Permanent effects cannot be made into Alternate Effects (since switching requires a free action, and permanent effects cannot be turned off).
- Only one effect in the Array (including all Alternate Effects) can be active at any time.

#### References

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

**Ref — Flat-Value Modifiers**
Source: context/rules/HeroesHandbook-rules__chunk_141.md
Locator: lines 9746-9789
Extract: whole

---

### Dynamic Alternate Effect

#### Domain Language

- A Dynamic Alternate Effect is a variant of the Alternate Effect that can share power points with other Dynamic effects and operate simultaneously at reduced effectiveness.
- Type: flat extra; the base effect pays 1 extra point to become "dynamic"; each Dynamic Alternate Effect costs 2 flat points.
- The character can reallocate power points among all Dynamic effects in the Array as a free action once per turn — each point shared reduces the effective rank of both sharing effects.
- Dynamic Alternate Effects can be active simultaneously as long as their combined point allocation does not exceed the total Array pool.
- Dynamic Arrays are significantly more flexible but more expensive than standard Arrays with simple Alternate Effects.

#### References

**Ref — Dynamic Alternate Effect**
Source: context/rules/HeroesHandbook-rules__chunk_143.md
Locator: lines 9999-10222
Extract: whole

---

# Boundary Domain

## power point

Owned by: Character Construction

- The currency spent to acquire effects, traits, advantages, and skills at character creation and advancement.
- Power point budget is set by power level (PL × 15 at creation); spending power points on effects is the primary mechanism for building powers.
- Power belongs to this module only for effect cost calculation; the budget and economy are Character Construction concerns.

## rank

Owned by: Character Construction

- The numeric level of an effect, ability, skill, or other trait; effects are acquired in ranks and scale with rank.
- Rank determines the scale, intensity, and reach of a power effect; the Power module uses rank as input to cost formulas and effect resolution.
- The concept of rank as a general scaling mechanism is defined in Character Construction.

## resistance check

Owned by: Check Resolution

- The check made by a target to resist a power effect; typically DC 10 + effect rank.
- Every attack-type effect in this module specifies which resistance check applies (Toughness, Fortitude, Will, Dodge).
- The mechanics of how checks are resolved, degrees of success/failure, and DC scaling belong to Check Resolution.

## Toughness

Owned by: Combat

- The defense used to resist Damage effects; derived from Stamina + Protection ranks + other bonuses.
- Toughness is referenced by Damage, Blast, and similar effects in this module as the resistance check target.
- Combat owns the Toughness defense calculation and damage condition application.

## Fortitude

Owned by: Combat

- The defense used to resist Affliction effects targeting physical resilience and Weaken effects targeting physical traits.
- Fortitude is referenced by Affliction and Weaken in this module as one of the selectable resistance checks.
- Combat owns the Fortitude defense value and its interaction with conditions.

## Will

Owned by: Combat

- The defense used to resist mental Affliction, Mind Reading, and Will-targeted Weaken effects.
- Will is referenced by Mind Reading, Affliction, and Weaken in this module.
- Combat owns the Will defense value.

## Dodge

Owned by: Combat

- The defense used to avoid ranged attacks and Area effect Dodge saves (DC 10 + effect rank to take half).
- Dodge is referenced by Blast, Area-extra effects, and Concealment targeting in this module.
- Combat owns the Dodge defense calculation and its role in combat resolution.
