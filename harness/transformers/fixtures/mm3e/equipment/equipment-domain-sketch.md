---
state: domain-sketch
---

# Module: [Equipment]

Scope: Devices vs equipment distinction, the Equipment advantage, inventing/jury-rigging, general gear, weapons, armor, vehicles, headquarters, and constructs.

**Core terms**:
- device
- equipment
- Equipment advantage
- Removable
- Easily Removable
- Indestructible
- battlesuit
- costume
- enhanced equipment
- inventing
- jury-rigging
- ritual
- melee weapon
- ranged weapon
- grenade
- explosive
- armor
- shield
- Toughness bonus
- vehicle
- vehicle size
- vehicle feature
- headquarters
- headquarters size
- headquarters feature
- construct
- animated object
- robot
- equipment point
- Alternate Equipment
- on-hand equipment

---

# Core Domain

## Key Abstractions

### Device

A Device is the central concept of powered, character-owned gear in MM3E — the bridge between the character's power point investment and a physical item that can be taken away. It owns the definition of what makes an item a device (it is a power with the Removable or Easily Removable flaw applied), the rules for temporary use without power-point cost, and the recovery rules when a device is lost. Device interacts with the Equipment advantage (which it contrasts with), with the Removable and Indestructible modifiers (which govern its vulnerability), and with inventing and jury-rigging (which produce temporary devices). The invariant that defines a Device is that it must always be traceable to a power effect paying power points; an item with no power-point cost is not a device — it is equipment.

A Device also owns the taxonomy of specialized device types: battlesuits (comprehensive power-armor devices), costumes (wearable devices or mundane gear with device-like immunity), and enhanced equipment (mundane items crossing into device territory via magic or super-science). The Removable flaw spectrum (Removable → Easily Removable, with or without Indestructible) determines the cost reduction and vulnerability trade-off. The character always retains the ability to replace a permanently lost device, because the device is considered a permanent part of their concept — unlike equipment, which can be taken with impunity.

#### Decisions made

- battlesuit, costume, and enhanced equipment are subtypes/specializations of Device, not their own KAs — all three are devices with specific descriptors.
- Removable, Easily Removable, and Indestructible are properties/modifiers of Device, not independent KAs — they exist only in the context of making a power into a device.
- Device vs. Equipment is a single binary distinction owned by this module; the boundary between them is the device's defining rule.

### device

#### Domain Language

- A device is an item providing a power effect or set of effects; mechanically it is a power with the Removable or Easily Removable flaw applied.
- Devices may originate from advanced science, magic, alien technology, or psychic power; all work identically in game terms regardless of origin or descriptor.
- A device is a permanent part of the character's trait set — the character pays power points for it; if lost or destroyed the character can replace it.
- Unlike mundane equipment, devices grant effects beyond normal technology and are only ever taken away temporarily.
- Characters may temporarily use a device for a single scene or adventure without paying power points; continuing use requires purchasing the device as a regular power.
- The GM may require a hero point to temporarily use a device belonging to another character.

#### Domain Sketch

- Records the character's power-point payment at cost reduced by the Removable or Easily Removable flaw ratio.
- Grants its power effects to the owner whenever the owner has possession of the device.
- Suspends all its power effects immediately when removed from the owner's possession.
- Restores all its power effects immediately when the owner recovers the device.
- Permits a non-owner to use the device for one scene without transferring power points.
- Permits the character to replace a permanently lost device because the power points remain spent on the character's sheet.
- Invariant: must carry either Removable or Easily Removable as a flaw; a power without that flaw is not a device.

#### References

**Ref — Ch7 Gadgets & Gear**
Source: context/rules/HeroesHandbook-rules__chunk_158.md
Locator: lines 11555-11629
Extract: whole

```source
A device is an item that provides a particular power effect or set of effects. While devices are typically creations of advanced science, they don't have to be. Many heroes and villains have magical devices such as enchanted weapons and armor, magical talismans, wands and staves of power, and so forth.

Generally speaking, devices are powers with the Removable flaw applied to them (see Removable in the Powers chapter), meaning the power is external to the character. Take away the device, and the wielder loses the ability to use those powers.

There can sometimes be a fine line between devices (Removable powers) and equipment (relatively mundane technology). The primary differences are: Devices are part of the character's traits. They grant effects beyond the capabilities of normal equipment, and they're only ever lost or taken away temporarily. If an item is integral to the character's concept or abilities, it's probably a device.
```

---

### Removable

#### Domain Language

- Removable is a flaw applied to powers that are external to the character, making the power dependent on an item that can be taken away.
- Applying Removable reduces the power's point cost to reflect the vulnerability of losing access.
- When the device is taken away the character loses those powers until the item is recovered.
- Devices are defined as powers with the Removable or Easily Removable flaw; without one of these flaws the power is internal, not a device.

#### Domain Sketch

- Reduces the point cost of its host power by the Removable flaw's cost-reduction ratio.
- Flags the device as one that opponents can physically take from the character during play.
- Triggers power-loss for the host power when the device is removed from the character's possession.
- Triggers power-restoration when the character recovers the device.
- Invariant: cannot be applied to a power that has no physical item form; internalized powers cannot carry this flaw.

#### References

*(Ref deduplication: chunk_158 already cited under device in this KA.)*

---

### Easily Removable

#### Domain Language

- Easily Removable is a more severe form of the Removable flaw — the device can be stripped away even more readily.
- The greater vulnerability to loss is reflected in a larger point-cost reduction compared to standard Removable.
- Items that are easily grabbed, small, or designed so opponents can quickly take them qualify for Easily Removable.

#### Domain Sketch

- Reduces the point cost of its host power by a larger ratio than standard Removable.
- Flags the device as one that opponents can strip away with minimal effort or contest.
- Applies the same power-loss and power-restoration triggers as Removable, with a faster stripping threshold.
- Invariant: applies only to items that are small, loosely carried, or designed for quick removal; bulky or worn gear qualifies for standard Removable instead.

#### References

*(Ref deduplication: chunk_158 already cited under device in this KA.)*

---

### Indestructible

#### Domain Language

- Indestructible is a modifier applied to a Removable or Easily Removable device indicating the item cannot be permanently destroyed.
- An Indestructible device can still be taken away but cannot be eliminated through destruction.
- Applying Indestructible costs additional points (reducing the benefit of the Removable flaw) because the item is less vulnerable overall.

#### Domain Sketch

- Reduces the flaw-based cost discount on the device it modifies by the Indestructible surcharge.
- Prevents the device from being permanently eliminated from play through any destructive means.
- Allows the device to be taken but guarantees the character can always recover it eventually.
- Invariant: can only be applied to a device that already carries Removable or Easily Removable; cannot make an equipment item indestructible.

#### References

*(Ref deduplication: chunk_158 already cited under device in this KA.)*

---

### battlesuit *is a type of* device

A battlesuit is a comprehensive power-armor device that bundles Protection, attack, movement, and Senses effects into a single Removable package. It adds no new rules to the device concept but defines a canonical power combination pattern for this class of device.

#### Domain Language

- A battlesuit (power armor) is an advanced suit of technological or magical armor granting the wearer power effects structured as a Removable device.
- Common battlesuit powers: Protection (possibly Impervious or Sustained), attack effects (Damage, often as Alternate Effects), Immunity to environmental hazards, movement (Flight, Leaping, Swimming), Senses (darkvision, radio, infrared, GPS, time sense), and Enhanced Strength.
- The battlesuit is the prototypical device: integral to the character's concept, powers the wearer beyond mundane capability, only ever taken away temporarily.

#### Domain Sketch

- Bundles Protection, Damage, movement, and Senses effects into a single Removable device instance.
- Loses all bundled powers simultaneously when removed from the wearer.
- Accepts Alternate Effect structures for multiple attack modes under one device cost.
- Invariant: all powers listed on the battlesuit are lost together when the battlesuit is away — no selective availability.

#### References

**Ref — Battlesuits**
Source: context/rules/HeroesHandbook-rules__chunk_159.md
Locator: lines 11630-11680
Extract: whole

```source
A common staple of comic books is the battlesuit, also known as power-armor. It is an advanced suit of technological (sometime magical) armor, giving the wearer various powers. Battlesuits commonly grant the following powers:

Armor: Protection is the foundation power for a battlesuit. Whether it is armor plating, metallic mesh, flexible ballistic material, or some combination of these and other cutting-edge technologies, a battlesuit protects its wearer from damage.

Attacks: Battlesuits are typically equipped with some kind of weapon or weapons, based around various attack effects, particularly Damage.

Movement: After defense and offense, battlesuits typically allow the wearer to get around, whether it's hydraulic-assisted Leaping, boot-jets or anti-gravity repulsion for Flight, turbines for Swimming, or some other movement effect.

Sensors: Battlesuits often come equipped with a suite of sensors providing Senses.
```

---

### costume *is a type of* device

A costume is a wearable device (or mundane item with a device-grade descriptor) that provides Protection and a no-cost immunity convention. It is the lightest form of device — sometimes purely a descriptor rather than a power-point investment.

#### Domain Language

- A costume may be made of unusual materials (super-science or magic) giving it a Protection effect beyond ordinary clothing.
- Costumes may serve as the source of a hero's powers (e.g., a battlesuit is a specialized powered costume).
- Comic book costumes are conventionally immune to the wearer's own powers; this is a descriptor costing no points.

#### Domain Sketch

- Grants Protection from its material (device-grade, stacks with non-equipment Protection bonuses) when purchased as a device.
- Applies the no-cost immunity-to-own-powers descriptor to all costumes by default in standard play.
- May serve as the physical housing for any other device effect the character carries.
- Invariant: the immunity-to-own-powers descriptor costs nothing and is assumed unless the GM rules otherwise.

#### References

*(Ref deduplication: chunk_159 already cited under battlesuit in this KA.)*

---

### enhanced equipment *is a type of* device

Enhanced equipment is mundane gear that has crossed the real-world technology ceiling through magic or super-science, acquiring device status. It differs from a battlesuit in that it starts as a recognizable real-world item type.

#### Domain Language

- Enhanced equipment is normal equipment given special properties through magic or super-science, crossing from equipment into the device category.
- Examples: magical weapons with greater Damage bonuses, magical armor with greater Protection, equipment using super-alloys or bulletproof cloth.
- The line from equipment to device is crossed when item properties exceed what the real world can produce.

#### Domain Sketch

- Exceeds the real-world technology ceiling in at least one property to qualify as a device.
- Acquires device status at the point its properties become impossible without magic or super-science.
- Carries the same Removable (or Easily Removable) flaw structure as any other device once it qualifies.
- Invariant: the crossing point is the real-world technology ceiling; items on the mundane side remain equipment regardless of rarity or cost.

#### References

**Ref — Enhanced Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_160.md
Locator: lines 11681-11724
Extract: whole

```source
Some devices are otherwise normal equipment with special properties. Magical items, normal equipment imbued with magical properties, are examples. Magical weapons may have greater damage bonuses or grant attack bonuses while magical armor imposes no penalties and provides greater protection. Such enchantments move archaic weapons and armor from the realm of mundane equipment to devices. The same is true of equipment using super-alloys, bulletproof cloth, and other wonders of super-science.
```

---

### Equipment

The Equipment KA governs the acquisition and use of mundane items in the game. It owns the concept of an equipment point pool derived from the Equipment advantage, the rules for what qualifies as adventuring equipment (and therefore requires payment), and the constraints on equipment's effectiveness relative to devices and powers. Equipment interacts with Device (it is the contrasting concept: mundane vs. powered) and with the Weapon, Armor, Vehicle, and Headquarters KAs (which define what can be purchased as equipment). The fundamental invariant is that equipment is bounded by real-world technology; anything exceeding that boundary becomes a device.

Equipment also owns the Alternate Equipment and on-hand equipment patterns — the rules for arrays of items usable one-at-a-time and the hero-point rule for having a specific item conveniently available. These patterns give equipment a limited flexibility analogous to power arrays and stunts, while remaining distinct from the device system.

#### Decisions made

- Equipment advantage and equipment point are grouped under Equipment because they are pure acquisition mechanics.
- Alternate Equipment and on-hand equipment are found terms but are core to the equipment acquisition model.
- The "bonus stacking" and "no extra effort" rules are properties of the Equipment KA.

### equipment

#### Domain Language

- Equipment covers mundane items — ordinary real-world things — that supplement a character's traits without granting powers per se.
- Equipment is acquired using equipment points from the Equipment advantage; each piece has a point cost.
- Equipment is limited to technology commonly available in the setting; the GM decides what qualifies.
- Equipment bonuses do not stack with each other or with other bonus types; only the highest bonus applies.
- Equipment cannot benefit from extra effort; a hero point must be spent instead for equipment stunts.
- Equipment is subject to damage, malfunction, and loss; the GM may declare it fails as a complication.

#### Domain Sketch

- Grants benefits as equipment-type bonuses up to the real-world technology ceiling.
- Applies its bonus only if it is the highest equipment bonus of its type currently in effect.
- Becomes unavailable when destroyed, lost, or declared a complication by the GM with no power-point recovery.
- Cannot be used with extra effort; a hero point is the only way to perform an equipment stunt.
- Invariant: benefits must remain within real-world technology; any item whose benefits exceed the ceiling is a device, not equipment.

#### References

**Ref — What Items Do You Pay For?**
Source: context/rules/HeroesHandbook-rules__chunk_162.md
Locator: lines 11765-11807
Extract: whole

```source
In addition to their amazing devices, characters often make use of various mundane equipment — ordinary things found in the real world — ranging from a simple set of tools to cell phones, laptop computers, and even common appliances. These items are known as equipment to differentiate them from devices.

Equipment is acquired with points from the Equipment advantage. Each piece of equipment has a cost in points, just like other traits. The character pays the item's cost out of the points from the Equipment advantage and can thereafter have and use that item.
```

**Ref — The Limits Of Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_164.md
Locator: lines 11852-11905
Extract: whole

```source
While equipment is useful it does have its limits, particularly when compared to powers or devices. Equipment is less expensive — it's cheaper to have a handgun than a Damage power or even a super-science blaster weapon — but equipment is also more limited.

Equipment includes only items and technology commonly available in the setting. The GM decides what is "commonly available," but as a rule of thumb assume equipment only includes things from the real world, not battlesuits, anti-gravity devices, shrink rays, and so forth.

Equipment bonuses are limited compared to the bonuses granted by other effects. Generally, they do not stack with each other or other types of bonuses, only the highest bonus applies.
```

---

### Equipment advantage

#### Domain Language

- The Equipment advantage is the character trait that grants equipment points for purchasing items.
- Characters pay each item's point cost from their equipment points and can thereafter own and use that item.
- An item's cost is based on its effects and features, just as a power's cost is based on effect rank and modifiers.

#### Domain Sketch

- Maintains the character's equipment point pool; the pool size equals the advantage's benefit level.
- Validates each item purchase against the remaining pool balance before allowing it.
- Invariant: the pool cannot be exceeded; purchases that would overspend the pool are not allowed.

#### References

*(Ref deduplication: chunk_162 already cited under equipment in this KA.)*

---

### equipment point

#### Domain Language

- An equipment point is the unit of currency for purchasing items via the Equipment advantage; the pool size is determined by ranks in the advantage.
- Every piece of equipment has a point cost; the character pays it and can thereafter own and use the item.
- Equipment points are distinct from power points: equipment points buy mundane gear and vehicles; power points buy devices and character traits.

#### Domain Sketch

- Functions as the unit of exchange for all equipment purchases (gear, vehicles, headquarters).
- Decrements the character's equipment pool when spent; the pool does not regenerate outside advancement.
- Converts vehicle and headquarters power effects to one-fifth their normal power-point cost for purchasing purposes.
- Invariant: vehicle and HQ power effects always cost one-fifth the normal amount in equipment points regardless of effect type.

#### References

*(Ref deduplication: chunk_162 already cited under equipment in this KA.)*

---

### Alternate Equipment

#### Domain Language

- Alternate Equipment is an array of items usable only one at a time, analogous to Alternate Effect for powers.
- Cost: full price for the most expensive item, 1 equipment point per additional item of equal or lesser cost.
- The utility belt is the classic example: a collection of tools and weapons available situationally but not simultaneously.
- Spending a hero point allows temporarily adding an item to the array for one scene.

#### Domain Sketch

- Activates exactly one item from its array at any given time; deactivates all others simultaneously.
- Charges full price for the most expensive item in the array and 1 point per additional item.
- Allows a hero-point stunt to add a non-array item for one scene without adding it permanently.
- Invariant: only one array item can be active at a time; selecting a new item deactivates the previous one.

#### References

**Ref — Alternate Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_163.md
Locator: lines 11808-11851
Extract: whole

```source
Just as with power effects, there is a diminishing value in having multiple items with a similar function, or a single piece of equipment with multiple functions, usable only one at a time. Equipment can have the Alternate Effect modifier (see the Extras section of the Powers chapter), such as a weapon capable of different modes of operation, or a reconfigurable tool.

Characters can also have Alternate Equipment, an array of items usable only one at a time. This is typically a multi-function item, or a kit or collection of various smaller items. The classic example is the utility belt (see its description later in this chapter).
```

**Ref — Utility Belt**
Source: context/rules/HeroesHandbook-rules__chunk_166.md
Locator: lines 11966-12022
Extract: whole

```source
A common piece of equipment for crime fighters and espionage agents is the utility belt (or bag, pouch, backpack, etc.): a collection of useful tools and equipment in a compact carrying case. A utility belt is an array of Alternate Equipment.

By spending hero points you can temporarily add Alternate Equipment to your utility belt, for those one-time items you may need in a pinch.
```

---

### on-hand equipment

#### Domain Language

- On-hand equipment allows a character to spend a hero point to have a particular item available in a scene without having planned ahead.
- It functions as an equipment power stunt for one scene; the GM decides whether having the item is plausible given the situation.
- The same rule applies to vehicles and replacement items.

#### Domain Sketch

- Produces a specific item for one scene after the character spends a hero point.
- Leaves the plausibility determination entirely to the GM; no rules enforce when this is possible.
- Applies to vehicles and replacement items under the same hero-point stunt rule.
- Invariant: on-hand equipment is always one-scene; continued use requires purchasing the item through normal means.

#### References

*(Ref deduplication: chunk_163 already cited under Alternate Equipment in this KA.)*

---

### Invention

Invention is the system that allows characters to create temporary devices on the fly, bypassing the normal power-point acquisition process at the cost of time, skill, and sometimes luck. It owns the design-and-construction workflow (two sequential Technology checks with time requirements scaled to power-point cost), the jury-rigging emergency shortcut (skip design, spend a hero point, compress construction to rounds at higher DC), and the ritual variant (same workflow but using Expertise: Magic for characters with the Ritualist advantage). Invention interacts with Device (invented items are temporary devices), with the Technology skill and Expertise: Magic skill (the check mechanics), and with the hero point economy (the currency for jury-rigging and reuse). The invariant is that invented and jury-rigged devices are temporary — they last one scene; permanent use requires spending power points.

#### Decisions made

- inventing, jury-rigging, and ritual are grouped as one KA because they share the same two-phase (design + construct) pattern.
- Ritual is the magical variant — same workflow, different skill.
- The mishap rule is part of Invention, not a separate KA.

### inventing

#### Domain Language

- Inventing is the process by which a character with the Inventor advantage creates a temporary device for single-adventure use.
- Requires two sequential checks: Design Check (Technology, DC 10 + point cost, 1 hour/pp) then Construction Check (Technology, DC 10 + point cost, 4 hours/pp).
- Both checks may be routine checks; reducing work time incurs a -5 penalty per -1 time rank reduction.
- The GM makes the design check secretly; 3+ degrees of failure means the design appears correct but won't function.
- A completed invention lasts one scene; reuse costs a hero point or the character spends power points to make it permanent.
- Magical inventions use Expertise: Magic instead of Technology for both checks.

#### Domain Sketch

- Executes a two-check workflow: GM makes design check in secret, then player makes construction check.
- Scales both check DCs and time requirements proportionally to the device's power-point cost.
- Allows time reduction by accepting a -5 check penalty per time rank reduced.
- Delivers a working device usable for one scene; permits hero-point reuse or permanent purchase.
- Invariant: both checks must be made before the device is available; only jury-rigging can skip the design phase.

#### References

**Ref — Enhanced Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_160.md
Locator: lines 11681-11724
Extract: whole

```source
Characters with the Inventor advantage can create inventions, temporary devices. To create an invention, the inventor defines its effects and its cost in power points. This cost is used for the necessary skill checks, and determines the time required to create the invention.

First, the inventor must design the invention. This is a Technology skill check the GM should make in secret. The DC is 10 + the invention's total power point cost.

Design Check = DC 10 + invention's point cost

Once the design is in-hand, the character can construct the invention. This requires four hours of work per power point of the invention's cost.

Construction Check = DC 10 + invention's point cost
```

**Ref — Using The Invention**
Source: context/rules/HeroesHandbook-rules__chunk_161.md
Locator: lines 11725-11764
Extract: whole

```source
Once the invention is complete, it is good for use in one scene, after which it breaks down or runs out of power. If the character wishes to use the invention again, there are two options.

The first is to spend the necessary power points to acquire the invention as a regular power, part of the character's traits.

The other option is to spend a hero point to get another one-scene use out of the invention. Each use costs an additional hero point, but doesn't require any further skill checks.
```

---

### jury-rigging

#### Domain Language

- Jury-rigging is an emergency inventing technique that produces a working device immediately by spending a hero point.
- The design check is skipped; construction time compresses to 1 round per power point of cost; the construction DC increases by +5.
- Cannot use routine check when jury-rigging; the check must be rolled.
- A jury-rigged device functions for one scene; each additional use costs one hero point with no further checks.

#### Domain Sketch

- Replaces the full inventing workflow by spending a hero point and skipping the design phase.
- Compresses construction time to one round per power point of cost.
- Applies a +5 DC penalty to the construction check.
- Blocks the routine-check option; the construction check must be rolled under pressure.
- Invariant: jury-rigged devices last one scene; extension requires another hero point each time.

#### References

*(Ref deduplication: chunk_161 already cited under inventing in this KA.)*

---

### ritual

#### Domain Language

- A ritual is a magical version of inventing available to characters with the Ritualist advantage; uses Expertise: Magic for all checks.
- Research phase: 4 hours per power point of cost; performance phase: 10 minutes per power point.
- Failing the research check makes the ritual unusable; 3+ degrees of failure may result in a mishap.
- Jury-rigging a ritual: spend a hero point, skip research, perform in rounds equal to cost, DC 15 + cost; works for one scene.

#### Domain Sketch

- Substitutes Expertise: Magic for Technology in both the design (research) and construction (performance) checks.
- Applies the same DC formula (10 + pp cost) for research and performance checks.
- Triggers a potential mishap at 3+ degrees of failure on the research check.
- Converts to jury-rig mode at the cost of one hero point, compressing to rounds per point at DC 15 + cost.
- Invariant: 3+ degrees of failure on research prevents the ritual from being performed and may cause adverse consequences.

#### References

**Ref — What Items Do You Pay For?**
Source: context/rules/HeroesHandbook-rules__chunk_162.md
Locator: lines 11765-11807
Extract: whole

```source
Characters with the Ritualist advantage can perform magical rituals. They are similar to inventions: one-time powers requiring some time and effort to set up.

For rituals, substitute the Expertise: Magic skill for both the design and construction checks. The design portion of the ritual takes 4 hours per power point of the ritual's cost. The performance of the actual ritual takes 10 minutes per point of the ritual's cost.

"Jury-rigging" a ritual has the same effects as for an invention. Spending a hero point allows the ritualist to skip the design check and perform the ritual in a number of rounds equal to its cost. An Expertise: Magic check against a DC equal of (15 + the ritual's cost) is needed to successfully perform the ritual.
```

---

### Weapon

The Weapon KA owns the equipment-grade offensive tools available to heroes and villains: melee weapons (hand-held close combat weapons with Strength-based Damage), ranged weapons (thrown and projectile weapons spanning simple pistols to rocket launchers), grenades (thrown area-effect weapons), and explosives (placed area-damage devices). It interacts with the Equipment KA (weapons are purchased with equipment points) and the Device KA (magical or super-scientific weapons are devices, not equipment). Weapons each carry four traits: category, effect, critical threat range, and point cost; this structure is uniform across melee, ranged, grenade, and explosive types.

#### Decisions made

- melee weapon, ranged weapon, grenade, and explosive are grouped as one KA because they all follow the same weapon-trait model.
- Weapon accessories (laser sight, stun ammo, etc.) are properties of ranged weapons, not separate KA terms.
- The grenade/explosive distinction (thrown vs. placed area damage) is captured within the Weapon KA.

### melee weapon

#### Domain Language

- A melee weapon is a hand-held close-combat weapon, typically with Strength-based Damage adding the wielder's Strength rank to the weapon's damage rank.
- Ordinary melee weapons break if the wielder's Strength exceeds the weapon's Toughness (4 for wood, 7-8 for metal).
- Categories: simple (brass knuckles, club, knife, pepper spray, stun gun), archaic (battleaxe, sword, spear, warhammer), exotic (chain Reach 2 + Improved Grab/Trip; chainsaw non-Strength; nunchaku; whip Reach 3 + Improved Grab/Trip).
- Critical threat range can be extended by 1 for 1 equipment point (same cost as Improved Critical advantage).

#### Domain Sketch

- Adds the wielder's Strength rank to its Damage rank for all Strength-based variants.
- Breaks when the wielder exerts Strength greater than the weapon's Toughness rating.
- Assigns one of three categories (simple, archaic, exotic) that determines which mechanical properties the weapon may have.
- Allows critical threat range extension at 1 equipment point per +1 range (up to Improved Critical advantage value).
- Invariant: each melee weapon carries exactly four traits — category, effect, critical range, and cost — none are optional.

#### References

**Ref — Melee Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_167.md
Locator: lines 12023-12074
Extract: whole

```source
Melee weapons are hand-held close combat weapons. They typically have a Strength-based Damage effect (see the Damage effect in the Powers chapter), adding the wielder's Strength rank to the weapon's damage rank. Ordinary melee weapons are limited by their Toughness in terms of the amount of Strength they can add. If a wielder exerts Strength greater than the weapon's Toughness (4 for wooden weapons, 7 or 8 for metal weapons), the weapon breaks when it is used.
```

**Ref — Simple Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_168.md
Locator: lines 12075-12170
Extract: whole

```source
Category: Melee weapons are categorized as simple, archaic, and exotic.

Effect: The effect a hit with the weapon causes, typically Damage, although some modern melee weapons have other effects.

Critical: The threat range for a critical hit with the weapon. Some weapons have a larger threat range than others. Increasing a weapon's threat range by 1 costs 1 point, like the Improved Critical advantage.

Cost: This is the weapon's cost in points.
```

**Ref — Simple Melee Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_169.md
Locator: lines 12171-12213
Extract: whole

```source
Brass Knuckles: Pieces of molded metal fitting over the fingers, brass knuckles add +1 damage to your unarmed strikes.

Club: Any of a number of blunt weapons used to strike, including nightsticks, batons, light maces, quarterstaffs, and similar bludgeoning weapons.

Sword: A blade between 18 and 30 or more inches in length, single or double-edged. It includes longswords, katanas, sabers, scimitars, and similar weapons.

Chain: A length of chain can strike targets up to 10 ft. away (Reach 2) and provides the benefits of the Improved Grab and Improved Trip advantages.
```

---

### ranged weapon

#### Domain Language

- Ranged weapons include thrown weapons (Strength-based Damage) and projectile weapons (not Strength-based): bows, crossbows, guns, energy weapons.
- Categories: Projectile Weapons, Energy Weapons (blasters, taser), Heavy Weapons (flamethrower, grenade launcher, rocket launcher), Thrown Weapons (bolos, boomerang, javelin, shuriken).
- Shuriken are thrown but not Strength-based (too light); boomerangs return to the thrower's hand next round (descriptor, not a power).
- Weapon accessories (laser sight, stun ammo, suppressor, targeting scope) cost 1 equipment point each.

#### Domain Sketch

- Applies Damage independently of the wielder's Strength for projectile and energy weapons.
- Adds the wielder's Strength rank to Damage for thrown weapons (Strength-based thrown category).
- Returns to the wielder's hand on the next round for boomerangs as a descriptor with no power cost.
- Accepts optional accessories at 1 equipment point each that modify attack or damage properties.
- Invariant: accessories are purchased separately at 1 point each and are never bundled into the weapon's base cost.

#### References

**Ref — Ranged Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_170.md
Locator: lines 12214-12268
Extract: whole

```source
Ranged weapons include both thrown and projectile weapons. Thrown weapons are Strength-based, adding the wielder's Strength rank to their Damage rank. Projectile weapons include bows, crossbows, and guns as well as energy weapons like lasers and blasters. Their Damage is generally not Strength-based.

Like melee weapons, ranged weapons have category, effect, critical, and cost traits. Ranged weapon categories are Projectile Weapons, Energy Weapons, Heavy Weapons, and Thrown Weapons.
```

**Ref — Ranged Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_171.md
Locator: lines 12269-12326
Extract: whole

```source
Holdout pistol — Ranged Damage 2
Light pistol — Ranged Damage 3
Heavy pistol — Ranged Damage 4
Assault Rifle — Ranged Multiattack Damage 5
Blaster pistol — Ranged Damage 5
Blaster rifle — Ranged Damage 8
Taser — Ranged Affliction 5
```

**Ref — Energy Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_172.md
Locator: lines 12327-12450
Extract: whole

```source
Flamethrower — Cone or Line Area Damage 6
Grenade Launcher — Burst Area Ranged Damage 5
Rocket Launcher — Ranged Damage 10, Burst Area 7
Bolos — Ranged Snare 3
Boomerang — Ranged Damage 1
Javelin — Ranged Damage 2
Shuriken — Ranged Multiattack Damage 1
```

**Ref — Other Ranged Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_173.md
Locator: lines 12451-12516
Extract: whole

```source
Bolos: A set of weighted cords intended to entangle an opponent with a Snare Affliction that hinders and impedes, then renders the target defenseless and immobile.

Boomerang: A common throwing weapon for heroes, a thrown boomerang returns to the thrower's hand, ready to be thrown again on the next round (less a Feature and more a special descriptor).

Shuriken: Flat metal stars or spikes for throwing. Shuriken can be thrown in groups as a Multiattack. Although they are thrown weapons, shuriken are not Strength-based, being too light.
```

---

### grenade

#### Domain Language

- A grenade is a thrown area-effect weapon affecting all targets within a burst or cloud area; targets beat a Dodge DC to halve or avoid effects.
- Types: fragmentation (Burst Area Damage 5, DC 15), smoke (Cloud Area Concealment Attack), flash-bang (Burst Area Dazzle 4), sleep gas (Cloud Area Affliction — fatigued/exhausted/asleep), tear gas (Cloud Area Affliction — dazed/vision-impaired, stunned/vision-disabled, incapacitated).

#### Domain Sketch

- Delivers its effect to all targets in the burst or cloud area simultaneously on a successful throw.
- Requires each affected target to beat the Dodge DC to halve or avoid the effect.
- Maintains cloud area effects for multiple rounds until the cloud disperses.
- Invariant: grenades are thrown weapons; they use the same throw rules and range penalties as other thrown items.

#### References

**Ref — Grenades And Explosives**
Source: context/rules/HeroesHandbook-rules__chunk_175.md
Locator: lines 12557-12606
Extract: whole

```source
Fragmentation grenade: A common military grenade that sprays shrapnel in all directions.

Smoke grenade: A smoke grenade fills an area with thick smoke (colored as desired) providing total concealment to all visual senses.

Flash-bang grenade: A flash-bang grenade gives off a bright flash and a loud bang that can render targets temporarily blind and deaf.

Sleep gas grenade: This grenade releases a gas with an Affliction (Sleep) effect.

Tear gas grenade: This type of grenade releases a cloud of gas that irritates the eyes and lungs, causing temporarily blindness and nausea.
```

*(Ref deduplication: chunk_173 already cited under ranged weapon in this KA.)*

---

### explosive

#### Domain Language

- An explosive is a non-thrown area-damage device placed or delivered by other means.
- Types: dynamite (Burst Area Damage 5 per stick) and plastic explosive (Burst Area Damage 10 per 1-lb block); each doubling of quantity increases Damage rank by 1.
- Explosives have a Dodge DC that targets beat to halve damage from the burst area.

#### Domain Sketch

- Requires placement or delivery rather than throwing to deploy.
- Scales its Damage rank upward by 1 for each doubling of quantity used.
- Applies the same Burst Area Dodge-for-half mechanic as grenades but is not a thrown weapon.
- Invariant: each doubling of explosive material increases Damage rank by exactly 1; the scaling is logarithmic, not linear.

#### References

**Ref — Explosives**
Source: context/rules/HeroesHandbook-rules__chunk_174.md
Locator: lines 12517-12556
Extract: whole

```source
Explosives
Ranged Burst Area Damage 5
Ranged Burst Area Damage 10

Suppressor: A suppressor muffles the noise of a ballistic weapon, giving it Subtle 1 and making it difficult (DC 20) for normal hearing to detect it.

Targeting Scope: A targeting scope gives a weapon the benefits of the Improved Aim advantage, doubling the normal benefits of aiming.
```

*(Ref deduplication: chunk_175 already cited under grenade in this KA.)*

---

### Armor and Defense

The Armor and Defense KA owns the protective gear that characters wear or carry — armors (which add a Protection bonus to Toughness) and shields (which grant active defense bonuses to Dodge and Parry). It also owns the Toughness bonus concept, which is the mechanical output of armor: a stacking-restricted bonus to Toughness. This KA interacts with the Device KA (super-shields and battlesuits are device versions of shield and armor concepts), with the Vehicle KA (vehicles can have armor features), and with the power level rules (Toughness from equipment cannot exceed power level).

#### Decisions made

- armor, shield, and Toughness bonus are grouped because they are all parts of the same protection system.
- Super-shield is a device variant described within the shield term, not a separate KA.
- The "modern armor limited to ballistic" constraint is a property of specific armor items, not a separate KA concept.

### armor

#### Domain Language

- Armor provides a Protection effect, granting a bonus to Toughness to resist damage.
- Categories: archaic (leather Prot 1, chain-mail Prot 3, plate-mail Prot 5, full-plate Prot 6), modern (undercover shirt Prot 2 Limited/Ballistic/Subtle; bulletproof vest Prot 4 Limited/Ballistic/Subtle).
- Equipment armor bonuses do not stack with other armor or Protection bonuses; only the highest applies.
- Toughness from armor cannot exceed the series' power level limit.

#### Domain Sketch

- Provides a Protection bonus to Toughness counted as an equipment-type bonus.
- Restricts modern armor's Protection to ballistic damage via the Limited modifier.
- Applies its bonus only if it is the single highest equipment Toughness bonus currently in effect.
- Invariant: equipment armor bonuses never stack — only the highest applies regardless of how many armors are worn.

#### References

**Ref — Grenades And Explosives**
Source: context/rules/HeroesHandbook-rules__chunk_175.md
Locator: lines 12557-12606
Extract: whole

```source
Armor provides a Protection effect, a bonus to Toughness. Like other equipment, armor bonuses do not stack with other armor or effect bonuses, only the highest bonus applies, one of the reasons why tough heroes rarely, if ever, wear armor. Toughness, even that granted by armor, is limited by your series' power level.

Armor has the following traits:
Category: Armors are categorized as archaic (ancient styles of armor like chain- and plate-mail), modern (typically bulletproof composites and synthetics), and shields (requiring some active use to protect against attacks).
Effect: The effect of most armor is Protection, sometimes with the Impervious modifier.
```

**Ref — Modern**
Source: context/rules/HeroesHandbook-rules__chunk_177.md
Locator: lines 12652-12693
Extract: whole

```source
Modern
Protection 2, Limited to Ballistic, Subtle — [Undercover shirt]
Protection 4, Limited to Ballistic, Subtle — [Bulletproof vest]

Shields
Small shield — +1 Active Defenses — 2 points
Medium shield — +2 Active Defenses — 4 points
Large shield — +3 Active Defenses — 6 points
```

---

### shield

#### Domain Language

- A shield grants active defense bonuses (Enhanced Dodge and Parry) functioning as mobile cover rather than passive Protection.
- Sizes: small (+1 active defenses, 2 points), medium (+2 active defenses, 4 points), large (+3 active defenses, 6 points).
- Super-shields are device versions; their Protection stacks with other effects (not equipment-based) and can be Impervious or Sustained.
- A super-shield can be an Alternate Effect weapon (Damage, Strength-based or Ranged) — offensive and defensive modes cannot be active simultaneously.

#### Domain Sketch

- Provides Enhanced Dodge and Enhanced Parry as active defense bonuses (mobile cover mechanic).
- In device (super-shield) form, provides Protection that stacks with non-equipment bonuses.
- Supports an Alternate Effect attack mode; offensive and defensive modes are mutually exclusive.
- Invariant: a shield's active defense bonus cannot be used while the shield is deployed as an Alternate Effect offensive weapon.

#### References

**Ref — Shields**
Source: context/rules/HeroesHandbook-rules__chunk_178.md
Locator: lines 12694-12739
Extract: whole

```source
Small shield: A small hand shield large enough to cover the wearer's forearm.
Medium shield: A larger shield covering almost the entire arm, able to shield a large portion of the torso.
Large shield: A "kite" shield able to cover more than half of the wielder's body.

Shields
Effect: The effect of most armor is Protection, sometimes with the Impervious modifier. Shields provide a sort of mobile cover (see Cover in the Action & Adventure chapter), granting Enhanced Dodge and Parry defenses.
```

**Ref — Under The Hood: Super-shields**
Source: context/rules/HeroesHandbook-rules__chunk_176.md
Locator: lines 12607-12651
Extract: whole

```source
Just as power armor is a device version of otherwise ordinary equipment armor, some heroes (and, less often, villains) have shield devices providing them with greater benefits than an ordinary shield.

A shield device may provide Enhanced Dodge and Parry defenses like a mundane shield, or it can grant ranks of Protection (which do stack with other effects, since they're not from equipment), perhaps even Impervious Protection for a "bulletproof" or "indestructible" shield.

A super-shield might even be useful as a weapon, providing a Damage effect, probably Strength-based. This is best handled as an Alternate Effect of the shield, meaning you can't use it both offensively and defensively at the same time!
```

---

### Toughness bonus

#### Domain Language

- The Toughness bonus is the bonus to Toughness granted by the Protection effect from armor or similar sources.
- Equipment-sourced Toughness bonuses do not stack with each other or with non-equipment bonuses; only the highest applies.
- Device-based Protection (battlesuits, super-shields) stacks with other effects because it is not an equipment bonus.
- Toughness, even when granted by armor, is capped by the series' power level.

#### Domain Sketch

- Distinguishes between equipment-type and device-type Toughness bonuses for stacking purposes.
- Caps at the series power level regardless of the combined total from any source.
- Allows device-based Protection to stack on top of equipment armor Protection (they are different bonus types).
- Invariant: equipment Toughness bonuses never stack with each other; device Toughness bonuses follow normal stacking rules and are separately PL-capped.

#### References

*(Ref deduplication: chunk_175 already cited under armor in this KA.)*

**Ref — The Limits Of Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_164.md
Locator: lines 11852-11905
Extract: whole

```source
Equipment bonuses are limited compared to the bonuses granted by other effects. Generally, they do not stack with each other or other types of bonuses, only the highest bonus applies. Thus a hero with a high Protection bonus doesn't get much, if any, advantage from wearing a bulletproof vest.
```

---

### Vehicle

The Vehicle KA owns transportation devices acquired as equipment. It governs the five-trait model (Size, Strength, Speed, Defense, Toughness) through which vehicles are purchased and upgraded, the size-based stat derivation table, and the full menu of vehicle features. Vehicle interacts with the Equipment KA (vehicles cost equipment points), the Device KA (vehicles can have power effects), and the Headquarters KA (both use shared/alternative ownership patterns). The invariant is that a vehicle's standard amenities cost nothing and that vehicles with multiple movement modes must pay full cost for the most expensive, acquiring others as Alternate Effects.

#### Decisions made

- vehicle, vehicle size, and vehicle feature are grouped as one KA because size and features are properties/components of a vehicle.
- Alternate Vehicles are a property of Vehicle, captured in the vehicle term's domain language.
- Vehicle power effects are vehicle features — this is the bridge to the power-effect boundary term.

### vehicle

#### Domain Language

- A vehicle is a transportation device acquired as equipment with five traits purchased at equipment point cost: Size, Strength, Speed, Defense, and Toughness.
- Base cost is the Speed movement effect; other traits, features, and powers cost additional points.
- Vehicles with multiple movement modes pay full cost for the most expensive and acquire others as Alternate Effects.
- Teams may pool equipment points to share a vehicle, dividing cost as they see fit.
- Alternate Vehicles: pay full cost for the most expensive, 1 point per additional vehicle of equal or lesser cost.

#### Domain Sketch

- Sets base trait values for Strength, Toughness, and Defense from its size category.
- Charges the full cost of the most expensive movement mode; additional movement modes are Alternate Effects.
- Permits a team to divide equipment point cost among members in any agreed proportion.
- Allows a hero-point stunt to produce a non-primary vehicle for one scene.
- Invariant: standard amenities (seating, seatbelts, radio, headlights, climate control) are included at no additional point cost.

#### References

**Ref — Shields**
Source: context/rules/HeroesHandbook-rules__chunk_178.md
Locator: lines 12694-12739
Extract: whole

```source
Not every hero can fly (or teleport, or run at super-speed...). Sometimes heroes make use of other means to get around. Vehicles are used primarily for transportation, although they may come with additional capabilities — including weapons — making them useful in other situations as well.

Vehicles have the following traits: Size, Strength, Speed, Defense, and Toughness. Like characters, each of a vehicle's traits costs points to improve. The basic cost for a vehicle is its Speed, but other things, like the vehicle's ability to haul cargo or resist damage, cost points as well. Vehicles can even have power effects of their own.
```

**Ref — Vehicle Size Categories**
Source: context/rules/HeroesHandbook-rules__chunk_179.md
Locator: lines 12740-12880
Extract: whole

```source
Vehicle Trait Cost
Size — 1 point per size category
Strength — 1 point per +1 Strength
Speed — movement effect cost
Toughness — 1 point per +1 Toughness
Defense — 1 point per +1 Defense
Features — 1 point per feature
Powers — power cost (see Chapter 5)
```

**Ref — Alternate Vehicles**
Source: context/rules/HeroesHandbook-rules__chunk_181.md
Locator: lines 12925-12978
Extract: whole

```source
Just like Alternate Equipment, characters may have multiple vehicles. These are generally Alternate Equipment by definition, since it's difficult to drive or pilot more than one vehicle at a time! So the character pays the full cost for the most expensive vehicle, and then 1 equipment point for each additional vehicle with the same or lesser cost.
```

---

### vehicle size

#### Domain Language

- Vehicle size is measured in categories from Medium (default) upward: Large, Huge, Gargantuan, Colossal, Awesome.
- Size determines base Strength, Toughness, and Defense values (Awesome: Str 20/Tgh 15/Def -12; Medium: Str 0/Tgh 5/Def 0).
- Larger vehicles have greater Strength and Toughness but a Defense penalty (easier to hit); penalty can be bought off at 1 point per -1 removed.
- Each size increase costs 1 equipment point.

#### Domain Sketch

- Determines the vehicle's baseline Strength, Toughness, and Defense from a fixed category table.
- Applies a Defense penalty for vehicles larger than Medium; larger vehicles are easier to target.
- Allows the Defense penalty to be bought off at 1 equipment point per -1 penalty removed.
- Invariant: baseline Strength, Toughness, and Defense values per size category are fixed; they may be improved above baseline but not reduced below it.

#### References

*(Ref deduplication: chunk_179 already cited under vehicle in this KA.)*

---

### vehicle feature

#### Domain Language

- Vehicle features are optional extras each costing 1 equipment point; standard features include Alarm (Technology DC 20), Caltrops dispenser, Hidden Compartments (Perception DC 20), Navigation System (+5 navigation), Oil Slick (DC 15 Vehicles check), Remote Control.
- Some features are power effects: Armor (Protection), Cloaking Device (Concealment 4 or 8 points), Immunity (environmental hazards), Smokescreen (Cloud Area Concealment Attack, 12 points), Weapons (Damage effects).
- Vehicle power effects cost one-fifth normal power-point cost, paid in equipment points.

#### Domain Sketch

- Charges one equipment point per feature for standard non-power features.
- Charges one-fifth normal power-point cost for power-effect features (converted to equipment points).
- Allows any appropriate power effect as a vehicle feature within the converted cost structure.
- Invariant: vehicle power effect ranks may not exceed limits derived from the series power level.

#### References

**Ref — Features**
Source: context/rules/HeroesHandbook-rules__chunk_180.md
Locator: lines 12881-12924
Extract: whole

```source
Certain things are considered "standard" on any vehicle. These include seating, safety harnesses or seat belts, heating and air-conditioning, radio receiver, headlights, and similar things with little or no impact on game play. Features are "optional extras" for vehicles and cost 1 point each.

A vehicle can have power effects of its own, usually reflecting the vehicle's systems. Vehicle powers have their normal cost for the vehicle (meaning they cost one-fifth the normal amount for the vehicle's owner, since the effects are incorporated into the vehicle and cost equipment points rather than power points).

Armor: Armor provides Protection for a vehicle in addition to its normal Toughness. 1 point per +1 Toughness.
Cloaking Device: A vehicle may have a "cloaking device" granting Concealment from visual senses. 4 points (normal vision or all of another sense type) or 8 points (all visual senses).
Smokescreen: The vehicle can release a cloud of thick smoke or mist that provides an Area visual Concealment Attack to hide the vehicle or confuse pursuers. 12 points.
```

*(Ref deduplication: chunk_179 already cited under vehicle in this KA.)*

---

### Headquarters

The Headquarters KA owns fixed bases of operation — from underground caves to orbiting satellites — acquired as equipment. It governs the two primary traits (Size and Toughness) and the menu of features that define a base's capabilities. Headquarters interacts with the Vehicle KA (both share the shared/alternate ownership pattern and feature-based customization), with the Equipment KA (all costs are equipment points), and with the Construct KA (HQ computers may be AI constructs). The invariant is that a headquarters power level caps the strength of power-effect features at twice the PL, and that a destroyed headquarters can always be rebuilt using the same equipment points.

#### Decisions made

- headquarters, headquarters size, and headquarters feature are grouped because size and features are properties of a headquarters.
- The HQ power level is a property of headquarters, not a separate KA.
- Shared headquarters and Alternate Headquarters patterns are behaviors of the Headquarters KA.

### headquarters

#### Domain Language

- A headquarters is a base of operations purchased as equipment with equipment points.
- Teams may pool equipment points to share a headquarters; cost is divided as members see fit.
- Alternate Headquarters: pay full cost for the most expensive, 1 point per additional HQ of equal or lesser cost.
- If destroyed, the owner may rebuild it with the same features or build a new one using the same equipment points.
- The HQ power level governs certain feature strengths; for player characters it equals the series power level.

#### Domain Sketch

- Starts at Small size for zero points; each size step up costs one additional equipment point.
- Maintains a feature menu that defines the base's capabilities; each feature costs one point.
- Permits a team to divide equipment point cost among members in any agreed proportion.
- Can be rebuilt after destruction using the same equipment points; the character never permanently loses those points with the structure.
- Invariant: if destroyed, the character may rebuild to the same specifications or choose different features; the equipment points are retained.

#### References

**Ref — Special Vehicles**
Source: context/rules/HeroesHandbook-rules__chunk_186.md
Locator: lines 13482-13521
Extract: whole

```source
Whether it's an underground cave, the top floors of a skyscraper, a satellite in orbit, or a base on the Moon, many heroes and villains maintain their own secret (or not so secret) headquarters. Teams may even pool their equipment points to have a headquarters they share, with the Gamemaster's approval.

A character can even have multiple bases of operation (see Alternate Headquarters later in this section).

If a character's headquarters is destroyed, the character can choose to rebuild it or build a new headquarters with different features using the same equipment points.
```

**Ref — Equipment Cost**
Source: context/rules/HeroesHandbook-rules__chunk_187.md
Locator: lines 13522-13624
Extract: whole

```source
Headquarters have two main traits — Size and Toughness — and a number of possible Features. Each of these costs equipment points.

A structure's size is measured similarly to that of a vehicle, and gives a general idea of the overall space it occupies. A headquarters starts out at Small size for 0 points. Each increase in size category costs 1 point.

Some features refer to a headquarters' power level. For player characters, this is the power level of the series overall.
```

---

### headquarters size

#### Domain Language

- HQ size categories range from Fine/Miniscule (-4 points) upward through Tiny, Small (default, 0 points), Medium, Large, Huge, Gargantuan, Colossal, Awesome.
- Starting size is Small (house-sized); each size increase costs 1 point; reducing below Small grants 1 extra point per step.
- Colossal is city-block-sized; Awesome is small-town-scale.

#### Domain Sketch

- Sets the physical scale of the base from house-sized Small to small-town Awesome.
- Charges 1 point per size increase; grants 1 reclaimed point per step below Small.
- Invariant: base Toughness starts at 6 for zero points; increasing Toughness costs 1 point per +2.

#### References

*(Ref deduplication: chunk_187 already cited under headquarters in this KA.)*

---

### headquarters feature

#### Domain Language

- Each feature costs 1 equipment point; features with power effects cannot exceed twice the HQ power level.
- Feature list includes: Combat Simulator, Communications, Computer, Concealed (DC+10 to find), Defense System (up to 2x HQ PL), Deathtraps, Dimensional Portal, Dock, Dual Size, Fire Prevention System (Nullify Fire 5), Garage, Gym, Hangar, Holding Cells (Nullify at HQ PL or +50% Toughness), Infirmary, Isolated, Laboratory, Library, Living Space, Personnel, Power System, Sealed, Secret, Security System (DC 20 +5/application, max DC 40), Self-repairing, Temporal Limbo, Workshop.
- Self-repairing taken twice allows the HQ to rebuild within a week if destroyed.

#### Domain Sketch

- Caps any power-effect feature rank at twice the HQ power level.
- Sets Defense System attack bonus exactly equal to the HQ power level.
- Increments Security System DC by +5 per additional security application to a maximum of DC 40.
- Charges 1 equipment point per feature regardless of complexity for non-power features.
- Invariant: standard structural amenities (doors, windows, power outlets, utilities) are included at no cost and are never charged as features.

#### References

**Ref — Features**
Source: context/rules/HeroesHandbook-rules__chunk_188.md
Locator: lines 13625-13664
Extract: whole

```source
A headquarters may have a number of features, chosen from the list below. A headquarters automatically has the basic structural amenities like doors and windows, power outlets, utilities, and so forth at no cost. Each feature costs 1 equipment point.

Combat Simulator: A combat simulator is a special room equipped with various devices intended to test characters' powers and skills. Generally, a combat simulator has a suite of equipment that can simulate any appropriate attack effect at a rank up to the HQ power level.

Defense System: A defense system consists of various weapon emplacements defending the exterior and interior of the headquarters. A defense system can have any attack effect with a cost no greater than twice the HQ power level. Their attack bonus is equal to the power level.

Security System: Various locks and alarms protect the headquarters from unauthorized access. A Technology check (DC 20) overcomes these systems. Each additional feature increases the DC by +5, to a maximum of DC 40.
```

**Ref — Deathtraps**
Source: context/rules/HeroesHandbook-rules__chunk_189.md
Locator: lines 13665-13707
Extract: whole

```source
A villainous version of the Defense System feature is deathtraps: the villain's lair has one or more fiendish traps suitable for disposing of those pesky heroes. Some deathtraps are designed as security systems to keep heroes out: concealed auto-guns, walls of flames, sealing rooms that fill with water or sand, and so forth.
```

**Ref — Fire Prevention System**
Source: context/rules/HeroesHandbook-rules__chunk_190.md
Locator: lines 13708-13750
Extract: whole

```source
The headquarters is equipped with an automatic system for detecting and extinguishing fires. Any large open flame sets the system off. It functions as a Nullify Fire 5 effect.

Garage: A garage houses ground vehicles and includes a ramp, elevator, or other access to move vehicles in and out, facilities for repairing and maintaining vehicles, and a sliding access door.

Hangar: A hangar houses air and space vehicles. It includes a hatch and/or runway for the vehicles to launch and facilities for repairing and maintaining flying vehicles.

Holding Cells: These are cells for holding prisoners. The cells are equipped with Nullify devices (ranked at the HQ power level) or their basic Toughness is increased by 50%.
```

**Ref — Library**
Source: context/rules/HeroesHandbook-rules__chunk_191.md
Locator: lines 13751-13794
Extract: whole

```source
A library allows for use of various Knowledge skills when doing research. A library may consist of printed matter (books and periodicals), microfilm, digital files, or a combination of all three.

Living Space: The headquarters includes all the necessary amenities for people to live there full-time. This is usually a number of residents equal to the HQ's power level comfortably.

Power System: A power system makes the headquarters completely independent of outside power. It has its own generators. The headquarters also has emergency back-up power should the generators fail. This generally lasts for a number of hours equal to the HQ's power level.

Self-repairing: The structure of the headquarters "heals" any damage done to it over time. If this feature is taken twice, the structure will even rebuild itself in a week if it is destroyed!
```

*(Ref deduplication: chunk_192 already cited under headquarters in this KA.)*

---

### Construct

The Construct KA owns nonliving beings capable of independent action — robots, androids, animated golems, zombies — acquired via the Minion advantage rather than as equipment. It governs the special build rules that make constructs distinct from living characters: no Stamina (cannot recover, must be repaired), immunity to Fortitude effects unless working on objects, and the mandatory absence of one ability pair (either Intellect+Presence for automatons, or Strength+Agility for immobile intellects). It interacts with the Equipment KA (constructs are explicitly not equipment), with the Device KA (constructs are not devices), and with the Headquarters KA (HQ AI computers are a construct variant).

#### Decisions made

- construct, animated object, and robot are grouped as one KA because animated object and robot are subtypes of construct.
- Construct command mechanics (move action, last-order persistence) are properties of the Construct KA.
- The Minion advantage is a boundary term — constructs are acquired via Minion, but this module does not own the Minion advantage.

### construct

#### Domain Language

- A construct is a nonliving being (robot, android, golem, zombie) capable of action; treated as a Minion, not equipment or a device.
- Constructs are created like other characters but have no Stamina (do not recover — must be repaired) and are immune to Fortitude-resisted effects unless the effect works on objects.
- Constructs lack either (a) Intellect and Presence — automatons, immune to Will and interaction effects — or (b) Strength and Agility — immobile intellects that cannot perform physical actions.
- Loss of three abilities (-30 points) plus Immunity to Fortitude effects (+30 points) nets to zero extra cost.
- Constructs can have skills, advantages, and power effects like other characters but cannot take those requiring absent abilities.
- Owner commands a construct as a move action; in the absence of new orders the construct follows the last order given.

#### Domain Sketch

- Builds using the Minion advantage rules as a full character, not as equipment or a device.
- Forces the absence of one ability pair (Intellect + Presence for automatons, or Strength + Agility for immobile intellects).
- Grants immunity to all Fortitude-resisted effects unless the effect specifically targets objects.
- Must be repaired using the Technology skill after taking damage; never recovers naturally.
- Executes the owner's most recent order when no new command has been given.
- Invariant: loss of three ability ranks (-30 pp) plus Immunity to Fortitude effects (+30 pp) nets to exactly zero extra cost; constructs are not more expensive than living characters.

#### References

**Ref — Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_194.md
Locator: lines 13879-13935
Extract: whole

```source
Armored robots, humanlike androids, even magically-animated golems or zombies are all examples of constructs, nonliving things capable of acting on their own to one degree or another, carrying out pre-programmed instructions, or even possessing independent thought in some cases.

Since they are capable of action on their own (rather than just improving their owner's abilities), constructs are considered minions — full-fledged characters — rather than devices or equipment and are acquired using the Minions advantage or summoned or created by a Summon effect.

Constructs have no Stamina, because they are not living beings. Constructs do not recover from damage; they must be repaired instead. Constructs are immune to effects permitting Fortitude resistance checks unless the effect works on objects.

Constructs without Intellect and Presence are automatons, operating on simple instinct or programmed instructions. They are immune to Will effects and interaction skills.

These qualities of constructs: lacking three abilities (-30 points) and Immunity to Fortitude Effects (30 points) average out to 0 points.
```

**Ref — Commanding Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_195.md
Locator: lines 13936-14082
Extract: whole

```source
A construct's owner can give it orders verbally or through any other means the construct understands. Commanding a construct is a move action. Constructs follow orders to the best of their ability. Non-intelligent constructs do exactly as they're told, without creativity or initiative, while intelligent constructs have the ability to interpret and improvise.

In the absence of new orders, constructs follow the last order they were given.

Constructs suffer damage like inanimate objects. Constructs do not recover from damage. Instead, they must be repaired.
```

---

### animated object *is a type of* construct

An animated object is a magically-activated construct — an ordinarily inanimate thing (golem, skeleton, enchanted armor) given motion and limited purpose. It adds no new structural rules but defines the automaton behavior pattern as the default for magically-animated constructs.

#### Domain Language

- An animated object is a construct variant in which a normally inanimate object (golem, magically-animated skeleton, enchanted armor) has been given the capacity for action through magic.
- As a construct it has no Stamina, does not recover from damage, and is immune to Fortitude-resisted effects.
- Animated objects are typically automatons — lacking Intellect and Presence — that obey literal commands without creativity or initiative.

#### Domain Sketch

- Executes orders literally without improvisation or creativity (automaton behavior default).
- Cannot interpret ambiguous commands; does only exactly what it is literally told.
- Invariant: has no Intellect or Presence ranks; is immune to Will effects and interaction skills.

#### References

*(Ref deduplication: chunk_194 and chunk_195 already cited under construct in this KA.)*

---

### robot *is a type of* construct

A robot is a technology-driven construct. It ranges from a simple automaton to a fully self-aware artificial intelligence depending on whether Intellect and Presence ranks are purchased.

#### Domain Language

- A robot is a construct variant driven by technology (armored robots, androids, mechanical drones).
- Robots with Intellect and Presence ranks can interpret orders and improvise; may be intelligent but non-sentient (Intellect without Presence) or fully self-aware.
- Robots without Strength and Agility ranks are immobile intellects (AI computers) capable only of directing other constructs.
- Robots do not recover from damage; they must be repaired using the Technology skill.

#### Domain Sketch

- Ranges in intelligence from simple automaton to full artificial sentience depending on purchased ability ranks.
- In immobile-intellect form (no Strength or Agility), can direct other constructs but cannot perform physical actions.
- Requires the Technology skill for all repair after damage; the skill user's check result determines repair extent.
- Invariant: same no-Stamina, Immunity to Fortitude, and no-recovery rules from the construct base apply to all robot variants without exception.

#### References

*(Ref deduplication: chunk_194 and chunk_195 already cited under construct in this KA.)*

---

## Boundary terms

### power effect

Owned by: Powers

#### Domain Language

- Equipment and devices are built using power effects (Damage, Protection, Features, Affliction, etc.) with their standard costs.
- Device power effects cost the same as non-device powers but are reduced by the Removable or Easily Removable flaw.
- Vehicle and headquarters power effects cost one-fifth normal because they are paid in equipment points.

#### Domain Sketch

- This module defines that vehicle and HQ power effects cost one-fifth of the normal power-point amount when converted to equipment points.
- The Powers module owns the power effect definitions (Damage, Protection, Affliction, Concealment, etc.) and their standard costs, DCs, and saving throws.
- This module enforces: when a vehicle or HQ includes a power effect feature, the equipment point cost = normal power cost ÷ 5; the Powers module enforces the effect's in-play mechanics (resistance checks, area calculations, durations).

#### References

**Ref — Ch7 Gadgets & Gear**
Source: context/rules/HeroesHandbook-rules__chunk_158.md
Locator: lines 11555-11629
Extract: whole

```source
Generally speaking, devices are powers with the Removable flaw applied to them (see Removable in the Powers chapter), meaning the power is external to the character.

Just like other powers, devices cost power points (albeit reduced some by the Removable flaw). Characters who want to have and use a device on a regular basis have to pay power points to have it, just like having any other power.
```

---

### power points

Owned by: Character Construction

#### Domain Language

- Devices (powers with Removable flaws) are paid for with power points reduced by the Removable discount.
- A character who permanently loses a Removable device may reallocate those power points.
- Constructs are created as characters using power points in the normal creation pool.

#### Domain Sketch

- This module defines the Removable flaw discount applied when a device is purchased: the power's point cost is reduced by the flaw ratio.
- Character Construction owns the total power-point budget and the rules for spending and tracking power points.
- This module enforces: device pp cost = power base cost minus Removable/Easily Removable reduction; if permanently lost, those pp remain spent on the sheet (character retains them and can replace the device).

#### References

**Ref — Ch7 Gadgets & Gear**
Source: context/rules/HeroesHandbook-rules__chunk_158.md
Locator: lines 11555-11629
Extract: whole

```source
Just like other powers, devices cost power points (albeit reduced some by the Removable flaw). Characters who want to have and use a device on a regular basis have to pay power points to have it, just like having any other power. The device becomes a part of the character's abilities. If the device is lost, stolen, or destroyed, the character can replace it, given time, since the device is considered a permanent part of the character. Only a re-allocation of the character's power points will change this.
```

---

### Strength

Owned by: Abilities

#### Domain Language

- Melee weapon damage is typically Strength-based: the wielder's Strength rank adds to the weapon's Damage rank.
- Weapon breakage occurs when the wielder's Strength exceeds the weapon's Toughness.
- A vehicle's Strength determines carrying capacity and can be increased above the size-based default for 1 point per rank.

#### Domain Sketch

- The Abilities module defines the Strength trait, its rank range, and how it contributes to checks and damage.
- This module defines the melee weapon Strength-based Damage formula (weapon Damage rank + wielder Strength rank) and the weapon breakage rule (wielder Strength > weapon Toughness → break on use).
- This module also defines the vehicle Strength trait (carrying capacity) and its upgrade cost (1 point per +1 rank above size default); the Abilities module enforces the Strength rules in all other contexts.

#### References

**Ref — Melee Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_167.md
Locator: lines 12023-12074
Extract: whole

```source
Melee weapons are hand-held close combat weapons. They typically have a Strength-based Damage effect (see the Damage effect in the Powers chapter), adding the wielder's Strength rank to the weapon's damage rank. Ordinary melee weapons are limited by their Toughness in terms of the amount of Strength they can add. If a wielder exerts Strength greater than the weapon's Toughness (4 for wooden weapons, 7 or 8 for metal weapons), the weapon breaks when it is used.
```

**Ref — Shields**
Source: context/rules/HeroesHandbook-rules__chunk_178.md
Locator: lines 12694-12739
Extract: whole

```source
A vehicle's Strength, much like a character's, determines its carrying capacity. You can increase a vehicle's Strength over the base rank for its size for 1 equipment point per Strength rank.
```

---

### Technology skill

Owned by: Skills

#### Domain Language

- Technology is used for both the design and construction checks in inventing.
- Technology checks are also used to repair damaged equipment and constructs, and to bypass vehicle alarms and security systems.

#### Domain Sketch

- The Skills module defines the Technology skill and the general rules for how skill checks work (modifier, DC, degrees of success).
- This module defines the inventing workflow that depends on Technology: Design DC = 10 + pp cost (1 hr/pp); Construction DC = 10 + pp cost (4 hr/pp); routine checks allowed; time reduction at -5 per rank.
- This module also enforces Technology as the repair skill for constructs and damaged equipment, and the skill used to bypass alarm systems (DC 20 base for most vehicle and HQ security).

#### References

**Ref — Enhanced Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_160.md
Locator: lines 11681-11724
Extract: whole

```source
Characters with the Inventor advantage can create inventions, temporary devices. To create an invention, the inventor defines its effects and its cost in power points.

First, the inventor must design the invention. This is a Technology skill check the GM should make in secret. The DC is 10 + the invention's total power point cost.

Once the design is in-hand, the character can construct the invention. This requires four hours of work per power point of the invention's cost. When the construction time is complete, make a Technology skill check.
```

---

### Minion advantage

Owned by: Advantages

#### Domain Language

- Constructs are acquired via the Minion advantage (or summoned via the Summon power effect); they are full characters, not equipment-point purchases.
- The Minion advantage is distinct from the Equipment advantage.

#### Domain Sketch

- The Advantages module defines the Minion advantage and the rules for what a minion may do and how it is acquired.
- This module defines the construct — the specific kind of minion produced when the Minion advantage is used to create a nonliving being.
- This module enforces the construct-specific traits (no Stamina, one ability pair absent, Immunity to Fortitude) that apply to minions of construct type; the Advantages module enforces the general minion rules (loyalty, command, minion defeat).

#### References

**Ref — Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_194.md
Locator: lines 13879-13935
Extract: whole

```source
Since they are capable of action on their own (rather than just improving their owner's abilities), constructs are considered minions — full-fledged characters — rather than devices or equipment and are acquired using the Minions advantage or summoned or created by a Summon effect.
```
