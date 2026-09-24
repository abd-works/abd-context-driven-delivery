---
state: key-abstractions
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

- battlesuit, costume, and enhanced equipment are subtypes/specializations of Device, not their own KAs — all three are devices with specific descriptors (independence test: they make no sense without the device concept).
- Removable, Easily Removable, and Indestructible are properties/modifiers of Device, not independent KAs — they exist only in the context of making a power into a device (independence test).
- Device vs. Equipment is a single binary distinction owned by this module; the boundary between them is the device's defining rule.

#### device

#### Domain Language

- A device is an item providing a power effect or set of effects; mechanically it is a power with the Removable or Easily Removable flaw applied.
- Devices may originate from advanced science, magic, alien technology, or psychic power; all work identically in game terms regardless of origin or descriptor.
- A device is a permanent part of the character's trait set — the character pays power points for it; if lost or destroyed the character can replace it.
- Unlike mundane equipment, devices grant effects beyond normal technology and are only ever taken away temporarily.
- Characters may temporarily use a device for a single scene or adventure without paying power points; continuing use requires purchasing the device as a regular power.
- The GM may require a hero point to temporarily use a device belonging to another character.

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

#### Removable

#### Domain Language

- Removable is a flaw applied to powers that are external to the character, making the power dependent on an item that can be taken away.
- Applying Removable reduces the power's point cost to reflect the vulnerability of losing access.
- When the device is taken away the character loses those powers until the item is recovered.
- Devices are defined as powers with the Removable or Easily Removable flaw; without one of these flaws the power is internal, not a device.

#### References

**Ref — Ch7 Gadgets & Gear**
Source: context/rules/HeroesHandbook-rules__chunk_158.md
Locator: lines 11555-11629
Extract: whole

```source
A device is an item that provides a particular power effect or set of effects.

Generally speaking, devices are powers with the Removable flaw applied to them (see Removable in the Powers chapter), meaning the power is external to the character. Take away the device, and the wielder loses the ability to use those powers. So if an armored hero loses access to his battlesuit, for example, he also loses access to the powers tied-up in it.
```

---

#### Easily Removable

#### Domain Language

- Easily Removable is a more severe form of the Removable flaw — the device can be stripped away even more readily.
- The greater vulnerability to loss is reflected in a larger point-cost reduction compared to standard Removable.
- Items that are easily grabbed, small, or designed so opponents can quickly take them qualify for Easily Removable.

#### References

**Ref — Ch7 Gadgets & Gear**
Source: context/rules/HeroesHandbook-rules__chunk_158.md
Locator: lines 11555-11629
Extract: whole

```source
A device is an item that provides a particular power effect or set of effects.

Generally speaking, devices are powers with the Removable flaw applied to them (see Removable in the Powers chapter), meaning the power is external to the character.

Equipment, on the other hand, is limited to fairly "mundane" things, can be taken away or even destroyed with impunity, and merely supplements the character's traits.
```

---

#### Indestructible

#### Domain Language

- Indestructible is a modifier applied to a Removable or Easily Removable device indicating the item cannot be permanently destroyed.
- An Indestructible device can still be taken away but cannot be eliminated through destruction.
- Applying Indestructible costs additional points (reducing the benefit of the Removable flaw) because the item is less vulnerable overall.

#### References

**Ref — Ch7 Gadgets & Gear**
Source: context/rules/HeroesHandbook-rules__chunk_158.md
Locator: lines 11555-11629
Extract: whole

```source
Generally speaking, devices are powers with the Removable flaw applied to them (see Removable in the Powers chapter), meaning the power is external to the character. Take away the device, and the wielder loses the ability to use those powers.

Just like other powers, devices cost power points (albeit reduced some by the Removable flaw). Characters who want to have and use a device on a regular basis have to pay power points to have it, just like having any other power.
```

---

#### battlesuit

#### Domain Language

- A battlesuit (power armor) is an advanced suit of technological or magical armor granting the wearer power effects structured as a Removable device.
- Common battlesuit powers: Protection (possibly Impervious or Sustained), attack effects (Damage, often as Alternate Effects), Immunity to environmental hazards, movement (Flight, Leaping, Swimming), Senses (darkvision, radio, infrared, GPS, time sense), and Enhanced Strength.
- The battlesuit is the prototypical device: integral to the character's concept, powers the wearer beyond mundane capability, only ever taken away temporarily.

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

#### costume

#### Domain Language

- A costume may be made of unusual materials (super-science or magic) giving it a Protection effect beyond ordinary clothing.
- Costumes may serve as the source of a hero's powers (e.g., a battlesuit is a specialized powered costume).
- Comic book costumes are conventionally immune to the wearer's own powers; this is a descriptor costing no points.

#### References

**Ref — Battlesuits**
Source: context/rules/HeroesHandbook-rules__chunk_159.md
Locator: lines 11630-11680
Extract: whole

```source
In addition to being stylish, costumes may be made of unusual materials much tougher than they appear (courtesy of super-science or magic), allowing them to provide a Protection effect. Costumes may have other properties and can even be the source of a hero's powers, such as in the case of battlesuits (previously).

Comic book costumes are usually immune to their wearer's powers. They don't burn, tear, or otherwise suffer damage when the wearer changes size or shape, bursts into flames, freezes, and so forth. The GM can assume this is just a descriptor for all costumes. It costs no points, since everyone has it.
```

---

#### enhanced equipment

#### Domain Language

- Enhanced equipment is normal equipment given special properties through magic or super-science, crossing from equipment into the device category.
- Examples: magical weapons with greater Damage bonuses, magical armor with greater Protection, equipment using super-alloys or bulletproof cloth.
- The line from equipment to device is crossed when item properties exceed what the real world can produce.

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

- Equipment advantage and equipment point are grouped under Equipment because they are pure acquisition mechanics — the advantage is how you buy equipment, the point is the unit of purchase; neither stands independently of the equipment system.
- Alternate Equipment and on-hand equipment are found terms but are core to the equipment acquisition model; they belong here.
- The "bonus stacking" and "no extra effort" rules are properties of the Equipment KA, not separate concepts.

#### equipment

#### Domain Language

- Equipment covers mundane items — ordinary real-world things — that supplement a character's traits without granting powers per se.
- Equipment is acquired using equipment points from the Equipment advantage; each piece has a point cost.
- Equipment is limited to technology commonly available in the setting; the GM decides what qualifies.
- Equipment bonuses do not stack with each other or with other bonus types; only the highest bonus applies.
- Equipment cannot benefit from extra effort; a hero point must be spent instead for equipment stunts.
- Equipment is subject to damage, malfunction, and loss; the GM may declare it fails as a complication.

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

#### Equipment advantage

#### Domain Language

- The Equipment advantage is the character trait that grants equipment points for purchasing items.
- Characters pay each item's point cost from their equipment points and can thereafter own and use that item.
- An item's cost is based on its effects and features, just as a power's cost is based on effect rank and modifiers.

#### References

**Ref — What Items Do You Pay For?**
Source: context/rules/HeroesHandbook-rules__chunk_162.md
Locator: lines 11765-11807
Extract: whole

```source
Equipment is acquired with points from the Equipment advantage. Each piece of equipment has a cost in points, just like other traits. The character pays the item's cost out of the points from the Equipment advantage and can thereafter have and use that item.

An item's cost is based on its effects and features, just like a power (see the Powers chapter for more information), so a ranged weapon has a cost based on its Ranged Damage rank.
```

---

#### equipment point

#### Domain Language

- An equipment point is the unit of currency for purchasing items via the Equipment advantage; the pool size is determined by ranks in the advantage.
- Every piece of equipment has a point cost; the character pays it and can thereafter own and use the item.
- Equipment points are distinct from power points: equipment points buy mundane gear and vehicles; power points buy devices and character traits.

#### References

**Ref — What Items Do You Pay For?**
Source: context/rules/HeroesHandbook-rules__chunk_162.md
Locator: lines 11765-11807
Extract: whole

```source
Equipment is acquired with points from the Equipment advantage. Each piece of equipment has a cost in points, just like other traits. The character pays the item's cost out of the points from the Equipment advantage and can thereafter have and use that item.
```

---

#### Alternate Equipment

#### Domain Language

- Alternate Equipment is an array of items usable only one at a time, analogous to Alternate Effect for powers.
- Cost: full price for the most expensive item, 1 equipment point per additional item of equal or lesser cost.
- The utility belt is the classic example: a collection of tools and weapons available situationally but not simultaneously.
- Spending a hero point allows temporarily adding an item to the array for one scene.

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

#### on-hand equipment

#### Domain Language

- On-hand equipment allows a character to spend a hero point to have a particular item available in a scene without having planned ahead.
- It functions as an equipment power stunt for one scene; the GM decides whether having the item is plausible given the situation.
- The same rule applies to vehicles and replacement items.

#### References

**Ref — Alternate Equipment**
Source: context/rules/HeroesHandbook-rules__chunk_163.md
Locator: lines 11808-11851
Extract: whole

```source
Characters may not necessarily carry all their equipment with them at all times. The GM may allow players to spend a hero point in order to have a particular item of equipment "on-hand" at a particular time. This is essentially an equipment "power stunt" — a one-time use of the item for one scene — and the Gamemaster rules whether or not having a particular item on-hand is even possible.
```

---

### Invention

Invention is the system that allows characters to create temporary devices on the fly, bypassing the normal power-point acquisition process at the cost of time, skill, and sometimes luck. It owns the design-and-construction workflow (two sequential Technology checks with time requirements scaled to power-point cost), the jury-rigging emergency shortcut (skip design, spend a hero point, compress construction to rounds at higher DC), and the ritual variant (same workflow but using Expertise: Magic for characters with the Ritualist advantage). Invention interacts with Device (invented items are temporary devices), with the Technology skill and Expertise: Magic skill (the check mechanics), and with the hero point economy (the currency for jury-rigging and reuse). The invariant is that invented and jury-rigged devices are temporary — they last one scene; permanent use requires spending power points.

#### Decisions made

- inventing, jury-rigging, and ritual are grouped as one KA because they share the same two-phase (design + construct) pattern with the same DC formula; ritual is the magical variant — independence test: jury-rigging has no meaning without inventing, and ritual is structurally identical to inventing.
- The mishap rule is part of Invention, not a separate KA.
- magical inventions (Expertise: Magic check substitution) are part of inventing, not ritual — they use the invention workflow with a different skill.

#### inventing

#### Domain Language

- Inventing is the process by which a character with the Inventor advantage creates a temporary device for single-adventure use.
- Requires two sequential checks: Design Check (Technology, DC 10 + point cost, 1 hour/pp) then Construction Check (Technology, DC 10 + point cost, 4 hours/pp).
- Both checks may be routine checks; reducing work time incurs a -5 penalty per -1 time rank reduction.
- The GM makes the design check secretly; 3+ degrees of failure means the design appears correct but won't function.
- A completed invention lasts one scene; reuse costs a hero point or the character spends power points to make it permanent.
- Magical inventions use Expertise: Magic instead of Technology for both checks.

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

#### jury-rigging

#### Domain Language

- Jury-rigging is an emergency inventing technique that produces a working device immediately by spending a hero point.
- The design check is skipped; construction time compresses to 1 round per power point of cost; the construction DC increases by +5.
- Cannot use routine check when jury-rigging; the check must be rolled.
- A jury-rigged device functions for one scene; each additional use costs one hero point with no further checks.

#### References

**Ref — Using The Invention**
Source: context/rules/HeroesHandbook-rules__chunk_161.md
Locator: lines 11725-11764
Extract: whole

```source
An inventor can choose to spend a hero point to jury-rig a device; ideal for when a particular device is needed right now. When jury-rigging a device, skip the design check and reduce the time of the construction check to one round per power point of the device's cost, but increase the DC of the check by +5. The inventor makes the check and, if successful, has use of the device for one scene before it burns out, falls apart, blows up, or otherwise fails. You can't jury-rig an invention as a routine check.
```

---

#### ritual

#### Domain Language

- A ritual is a magical version of inventing available to characters with the Ritualist advantage; uses Expertise: Magic for all checks.
- Research phase: 4 hours per power point of cost; performance phase: 10 minutes per power point.
- Failing the research check makes the ritual unusable; 3+ degrees of failure may result in a mishap.
- Jury-rigging a ritual: spend a hero point, skip research, perform in rounds equal to cost, DC 15 + cost; works for one scene.

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

The Weapon KA owns the equipment-grade offensive tools available to heroes and villains: melee weapons (hand-held close combat weapons with Strength-based Damage), ranged weapons (thrown and projectile weapons spanning simple pistols to rocket launchers), grenades (thrown area-effect weapons), and explosives (placed area-damage devices). It interacts with the Equipment KA (weapons are purchased with equipment points) and the Device KA (magical or super-scientific weapons are devices, not equipment). Weapons each carry four traits: category, effect, critical threat range, and point cost; this structure is uniform across melee, ranged, grenade, and explosive types. The invariant is that all weapon effects use the Power chapter's effect mechanics (Damage, Affliction, etc.) at the specified rank, and critical threat ranges are bounded by the Improved Critical advantage cost.

#### Decisions made

- melee weapon, ranged weapon, grenade, and explosive are grouped as one KA because they all follow the same weapon-trait model (category, effect, critical, cost) and are all purchased as equipment; distinct mechanics (thrown vs. projectile vs. area) map to sub-categories within Weapon.
- Weapon accessories (laser sight, stun ammo, etc.) are properties of ranged weapons, not separate KA terms.
- The grenade/explosive distinction (thrown vs. placed area damage) is captured within the Weapon KA.

#### melee weapon

#### Domain Language

- A melee weapon is a hand-held close-combat weapon, typically with Strength-based Damage adding the wielder's Strength rank to the weapon's damage rank.
- Ordinary melee weapons break if the wielder's Strength exceeds the weapon's Toughness (4 for wood, 7-8 for metal).
- Categories: simple (brass knuckles, club, knife, pepper spray, stun gun), archaic (battleaxe, sword, spear, warhammer), exotic (chain Reach 2 + Improved Grab/Trip; chainsaw non-Strength; nunchaku; whip Reach 3 + Improved Grab/Trip).
- Critical threat range can be extended by 1 for 1 equipment point (same cost as Improved Critical advantage).

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

#### ranged weapon

#### Domain Language

- Ranged weapons include thrown weapons (Strength-based Damage) and projectile weapons (not Strength-based): bows, crossbows, guns, energy weapons.
- Categories: Projectile Weapons, Energy Weapons (blasters, taser), Heavy Weapons (flamethrower, grenade launcher, rocket launcher), Thrown Weapons (bolos, boomerang, javelin, shuriken).
- Shuriken are thrown but not Strength-based (too light); boomerangs return to the thrower's hand next round (descriptor, not a power).
- Weapon accessories (laser sight, stun ammo, suppressor, targeting scope) cost 1 equipment point each.

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

#### grenade

#### Domain Language

- A grenade is a thrown area-effect weapon affecting all targets within a burst or cloud area; targets beat a Dodge DC to halve or avoid effects.
- Types: fragmentation (Burst Area Damage 5, DC 15), smoke (Cloud Area Concealment Attack), flash-bang (Burst Area Dazzle 4), sleep gas (Cloud Area Affliction — fatigued/exhausted/asleep), tear gas (Cloud Area Affliction — dazed/vision-impaired, stunned/vision-disabled, incapacitated).

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

**Ref — Other Ranged Weapons**
Source: context/rules/HeroesHandbook-rules__chunk_173.md
Locator: lines 12451-12516
Extract: whole

```source
Grenades And Explosives
Item — Effect — Grenades — Dodge DC — Cost
Fragmentation — Ranged Burst Area Damage 5 — DC 15
Smoke — Ranged Cloud Area Concealment Attack 4
Flash-bang — Ranged Burst Area Dazzle 4
Sleep gas — Ranged Cloud Area Sleep 4
Tear gas — Ranged Cloud Area Affliction 4
```

---

#### explosive

#### Domain Language

- An explosive is a non-thrown area-damage device placed or delivered by other means.
- Types: dynamite (Burst Area Damage 5 per stick) and plastic explosive (Burst Area Damage 10 per 1-lb block); each doubling of quantity increases Damage rank by 1.
- Explosives have a Dodge DC that targets beat to halve damage from the burst area.

#### References

**Ref — Grenades And Explosives**
Source: context/rules/HeroesHandbook-rules__chunk_175.md
Locator: lines 12557-12606
Extract: whole

```source
Dynamite: A common explosive. The damage on the table is for a single stick of dynamite. Each doubling of the amount of explosive increases Damage rank by 1.

Plastic explosive: Another common explosive, which can be worked into different shapes. The damage listed is for a 1-lb block. Each doubling of the amount of explosive increases Damage rank by 1.
```

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

---

### Armor and Defense

The Armor and Defense KA owns the protective gear that characters wear or carry — armors (which add a Protection bonus to Toughness) and shields (which grant active defense bonuses to Dodge and Parry). It also owns the Toughness bonus concept, which is the mechanical output of armor: a stacking-restricted bonus to Toughness. This KA interacts with the Device KA (super-shields and battlesuits are device versions of shield and armor concepts), with the Vehicle KA (vehicles can have armor features), and with the power level rules (Toughness from equipment cannot exceed power level). The fundamental invariant is that equipment-sourced Toughness bonuses do not stack — only the highest applies — whereas device-sourced Protection does stack.

#### Decisions made

- armor, shield, and Toughness bonus are grouped because they are all parts of the same protection system: armor provides Toughness bonus, shield provides defense bonus, Toughness bonus is the measured output.
- Super-shield is a device variant described within the shield term, not a separate KA — its device nature is captured under the Device KA.
- The "modern armor limited to ballistic" constraint is a property of specific armor items, not a separate KA concept.

#### armor

#### Domain Language

- Armor provides a Protection effect, granting a bonus to Toughness to resist damage.
- Categories: archaic (leather Prot 1, chain-mail Prot 3, plate-mail Prot 5, full-plate Prot 6), modern (undercover shirt Prot 2 Limited/Ballistic/Subtle; bulletproof vest Prot 4 Limited/Ballistic/Subtle).
- Equipment armor bonuses do not stack with other armor or Protection bonuses; only the highest applies.
- Toughness from armor cannot exceed the series' power level limit.

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

#### shield

#### Domain Language

- A shield grants active defense bonuses (Enhanced Dodge and Parry) functioning as mobile cover rather than passive Protection.
- Sizes: small (+1 active defenses, 2 points), medium (+2 active defenses, 4 points), large (+3 active defenses, 6 points).
- Super-shields are device versions; their Protection stacks with other effects (not equipment-based) and can be Impervious or Sustained.
- A super-shield can be an Alternate Effect weapon (Damage, Strength-based or Ranged) — offensive and defensive modes cannot be active simultaneously.

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

#### Toughness bonus

#### Domain Language

- The Toughness bonus is the bonus to Toughness granted by the Protection effect from armor or similar sources.
- Equipment-sourced Toughness bonuses do not stack with each other or with non-equipment bonuses; only the highest applies.
- Device-based Protection (battlesuits, super-shields) stacks with other effects because it is not an equipment bonus.
- Toughness, even when granted by armor, is capped by the series' power level.

#### References

**Ref — Grenades And Explosives**
Source: context/rules/HeroesHandbook-rules__chunk_175.md
Locator: lines 12557-12606
Extract: whole

```source
Armor provides a Protection effect, a bonus to Toughness. Like other equipment, armor bonuses do not stack with other armor or effect bonuses, only the highest bonus applies. Toughness, even that granted by armor, is limited by your series' power level.
```

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

- vehicle, vehicle size, and vehicle feature are grouped as one KA because size and features are properties/components of a vehicle, not independent concepts (independence test: vehicle size has no meaning without a vehicle to apply it to).
- Alternate Vehicles (arrays of vehicles) is a property of Vehicle, captured in the vehicle term's domain language.
- Vehicle power effects (armor, cloaking, weapons) are vehicle features — this is the bridge to the power-effect boundary term.

#### vehicle

#### Domain Language

- A vehicle is a transportation device acquired as equipment with five traits purchased at equipment point cost: Size, Strength, Speed, Defense, and Toughness.
- Base cost is the Speed movement effect; other traits, features, and powers cost additional points.
- Vehicles with multiple movement modes pay full cost for the most expensive and acquire others as Alternate Effects.
- Teams may pool equipment points to share a vehicle, dividing cost as they see fit.
- Alternate Vehicles: pay full cost for the most expensive, 1 point per additional vehicle of equal or lesser cost.

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

#### vehicle size

#### Domain Language

- Vehicle size is measured in categories from Medium (default) upward: Large, Huge, Gargantuan, Colossal, Awesome.
- Size determines base Strength, Toughness, and Defense values (Awesome: Str 20/Tgh 15/Def -12; Medium: Str 0/Tgh 5/Def 0).
- Larger vehicles have greater Strength and Toughness but a Defense penalty (easier to hit); penalty can be bought off at 1 point per -1 removed.
- Each size increase costs 1 equipment point.

#### References

**Ref — Vehicle Size Categories**
Source: context/rules/HeroesHandbook-rules__chunk_179.md
Locator: lines 12740-12880
Extract: whole

```source
Vehicle Size Categories
Awesome — Str 20 / Toughness 15 / Defense -12
Colossal — Str 16 / Toughness 13 / Defense -8
Gargantuan — Str 12 / Toughness 11 / Defense -4
Huge — Str 8 / Toughness 9 / Defense -2
Large — Str 4 / Toughness 7 / Defense -1
Medium — Str 0 / Toughness 5 / Defense 0

A vehicle's size determines its base Defense, which is used to determine the Defense Class to hit the vehicle with attacks. For sizes larger than medium, this is a penalty, making it easier to target the vehicle. You can "buy off" the Defense penalty applied to a vehicle for 1 equipment point per -1 penalty removed.
```

---

#### vehicle feature

#### Domain Language

- Vehicle features are optional extras each costing 1 equipment point; standard features include Alarm (Technology DC 20), Caltrops dispenser, Hidden Compartments (Perception DC 20), Navigation System (+5 navigation), Oil Slick (DC 15 Vehicles check), Remote Control.
- Some features are power effects: Armor (Protection), Cloaking Device (Concealment 4 or 8 points), Immunity (environmental hazards), Smokescreen (Cloud Area Concealment Attack, 12 points), Weapons (Damage effects).
- Vehicle power effects cost one-fifth normal power cost, paid in equipment points.

#### References

**Ref — Vehicle Size Categories**
Source: context/rules/HeroesHandbook-rules__chunk_179.md
Locator: lines 12740-12880
Extract: whole

```source
Alarm: The vehicle has an alarm system that goes off when an unauthorized access or activation attempt is made. A Technology check (DC 20) can overcome the alarm.

Navigation System: The vehicle is equipped with a navigation system that grants a +5 circumstance bonus on skill checks related to navigation.

Oil Slick: The vehicle can release an oil slick, covering a 20-ft. by 20-ft. area and forcing the driver of a pursuing vehicle to make a Vehicles check (DC 15) to retain control of the vehicle.
```

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

---

### Headquarters

The Headquarters KA owns fixed bases of operation — from underground caves to orbiting satellites — acquired as equipment. It governs the two primary traits (Size and Toughness) and the menu of features that define a base's capabilities. Headquarters interacts with the Vehicle KA (both share the shared/alternate ownership pattern and feature-based customization), with the Equipment KA (all costs are equipment points), and with the Construct KA (HQ computers may be AI constructs). The invariant is that a headquarters power level caps the strength of power-effect features at twice the PL, and that a destroyed headquarters can always be rebuilt using the same equipment points.

#### Decisions made

- headquarters, headquarters size, and headquarters feature are grouped because size and features are properties of a headquarters, not independent concepts.
- The HQ power level is a property of headquarters, not a separate KA.
- Shared headquarters and Alternate Headquarters patterns are behaviors of the Headquarters KA, not separate terms.

#### headquarters

#### Domain Language

- A headquarters is a base of operations purchased as equipment with equipment points.
- Teams may pool equipment points to share a headquarters; cost is divided as members see fit.
- Alternate Headquarters: pay full cost for the most expensive, 1 point per additional HQ of equal or lesser cost.
- If destroyed, the owner may rebuild it with the same features or build a new one using the same equipment points.
- The HQ power level governs certain feature strengths; for player characters it equals the series power level.

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

**Ref — Workshop**
Source: context/rules/HeroesHandbook-rules__chunk_192.md
Locator: lines 13795-13835
Extract: whole

```source
A team of heroes most often has a headquarters they all share. In this case, the team members may divide up the equipment point cost of the HQ among them however they wish, usually as evenly as possible.

In the event that a character has more than one headquarters, such as hidden bases scattered around the world, the others are treated as Alternate Equipment: the character pays the points for the most expensive HQ, then 1 equipment point for each additional HQ of the same or lesser cost.
```

---

#### headquarters size

#### Domain Language

- HQ size categories range from Fine/Miniscule (-4 points) upward through Tiny, Small (default, 0 points), Medium, Large, Huge, Gargantuan, Colossal, Awesome.
- Starting size is Small (house-sized); each size increase costs 1 point; reducing below Small grants 1 extra point per step.
- Colossal is city-block-sized; Awesome is small-town-scale.

#### References

**Ref — Equipment Cost**
Source: context/rules/HeroesHandbook-rules__chunk_187.md
Locator: lines 13522-13624
Extract: whole

```source
Structure Size Categories
Awesome — 6 points — Small town, sprawling installation
Colossal — 5 points — City block, private estate
Gargantuan — 4 points — Skyscraper
Huge — 3 points — Castle
Large — 2 points — Mansion, cave complex
Medium — 1 point — Warehouse
Small — 0 points — House
Tiny — -1 point — Townhouse
Diminutive — -2 points — Apartment

A headquarters' Toughness indicates the strength of its structural materials. A structure starts out with Toughness 6 for 0 points. +2 Toughness costs 1 equipment point.
```

---

#### headquarters feature

#### Domain Language

- Each feature costs 1 equipment point; features with power effects cannot exceed twice the HQ power level.
- Feature list includes: Combat Simulator, Communications, Computer, Concealed (DC+10 to find), Defense System (up to 2x HQ PL), Deathtraps, Dimensional Portal, Dock, Dual Size, Fire Prevention System (Nullify Fire 5), Garage, Gym, Hangar, Holding Cells (Nullify at HQ PL or +50% Toughness), Infirmary, Isolated, Laboratory, Library, Living Space, Personnel, Power System, Sealed, Secret, Security System (DC 20 +5/application, max DC 40), Self-repairing, Temporal Limbo, Workshop.
- Self-repairing taken twice allows the HQ to rebuild within a week if destroyed.

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

**Ref — Workshop**
Source: context/rules/HeroesHandbook-rules__chunk_192.md
Locator: lines 13795-13835
Extract: whole

```source
A workshop has all the facilities for making various things. It includes tools, workbenches, supplies, and so forth.

Security System: Various locks and alarms protect the headquarters from unauthorized access. A Technology check (DC 20) overcomes these systems. Each additional feature increases the DC by +5, to a maximum of DC 40.

Temporal Limbo: Time within the headquarters actually moves at a different rate than that of the world outside! Time within the structure is either slowed or sped up compared to the normal passage of time, passing at half or twice the normal rate.
```

---

### Construct

The Construct KA owns nonliving beings capable of independent action — robots, androids, animated golems, zombies — acquired via the Minion advantage rather than as equipment. It governs the special build rules that make constructs distinct from living characters: no Stamina (cannot recover, must be repaired), immunity to Fortitude effects unless working on objects, and the mandatory absence of one ability pair (either Intellect+Presence for automatons, or Strength+Agility for immobile intellects). It interacts with the Equipment KA (constructs are explicitly not equipment), with the Device KA (constructs are not devices), and with the Headquarters KA (HQ AI computers are a construct variant). The fundamental invariant is that loss of three abilities minus Immunity to Fortitude effects nets to zero power points — constructs cost nothing extra for their exceptional traits.

#### Decisions made

- construct, animated object, and robot are grouped as one KA because animated object and robot are subtypes of construct with no independent meaning.
- Construct command mechanics (move action, last-order persistence) are properties of the Construct KA, not a separate term.
- The Minion advantage is a boundary term, not part of this KA — constructs are acquired via Minion, but this module does not own the Minion advantage.

#### construct

#### Domain Language

- A construct is a nonliving being (robot, android, golem, zombie) capable of action; treated as a Minion, not equipment or a device.
- Constructs are created like other characters but have no Stamina (do not recover — must be repaired) and are immune to Fortitude-resisted effects unless the effect works on objects.
- Constructs lack either (a) Intellect and Presence — automatons, immune to Will and interaction effects — or (b) Strength and Agility — immobile intellects that cannot perform physical actions.
- Loss of three abilities (-30 points) plus Immunity to Fortitude effects (+30 points) nets to zero extra cost.
- Constructs can have skills, advantages, and power effects like other characters but cannot take those requiring absent abilities.
- Owner commands a construct as a move action; in the absence of new orders the construct follows the last order given.

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

#### animated object

#### Domain Language

- An animated object is a construct variant in which a normally inanimate object (golem, magically-animated skeleton, enchanted armor) has been given the capacity for action through magic.
- As a construct it has no Stamina, does not recover from damage, and is immune to Fortitude-resisted effects.
- Animated objects are typically automatons — lacking Intellect and Presence — that obey literal commands without creativity or initiative.

#### References

**Ref — Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_194.md
Locator: lines 13879-13935
Extract: whole

```source
Armored robots, humanlike androids, even magically-animated golems or zombies are all examples of constructs, nonliving things capable of acting on their own to one degree or another, carrying out pre-programmed instructions, or even possessing independent thought in some cases.
```

**Ref — Commanding Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_195.md
Locator: lines 13936-14082
Extract: whole

```source
Non-intelligent constructs do exactly as they're told, without creativity or initiative, while intelligent constructs have the ability to interpret and improvise. An owner can also give a construct a series of basic orders for it to fulfill, such as "stay and guard this place and attack anyone who comes here other than me."
```

---

#### robot

#### Domain Language

- A robot is a construct variant driven by technology (armored robots, androids, mechanical drones).
- Robots with Intellect and Presence ranks can interpret orders and improvise; may be intelligent but non-sentient (Intellect without Presence) or fully self-aware.
- Robots without Strength and Agility ranks are immobile intellects (AI computers) capable only of directing other constructs.
- Robots do not recover from damage; they must be repaired using the Technology skill.

#### References

**Ref — Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_194.md
Locator: lines 13879-13935
Extract: whole

```source
Armored robots, humanlike androids, even magically-animated golems or zombies are all examples of constructs.

Constructs without Strength and Agility ranks are immobile intellects, like an artificially intelligent computer or a sentient magic item. They cannot undertake physical actions on their own. They can have Dexterity, used for manipulating remotes and such.

A construct can buy up one of its nonexistent ability ranks by spending power points; +1 rank per 2 power points, as usual, but starting at a rank of -5.

Constructs do not recover from damage. Instead, they must be repaired. See the Technology skill description for guidelines on repairing damaged objects.
```

**Ref — Commanding Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_195.md
Locator: lines 13936-14082
Extract: whole

```source
A construct's owner can give it orders verbally or through any other means the construct understands. Commanding a construct is a move action. Non-intelligent constructs do exactly as they're told, without creativity or initiative, while intelligent constructs have the ability to interpret and improvise.
```

---

## Boundary terms

### power effect

Owned by: Powers

#### Domain Language

- Equipment and devices are built using power effects (Damage, Protection, Features, Affliction, etc.) with their standard costs.
- Device power effects cost the same as non-device powers but are reduced by the Removable or Easily Removable flaw.
- Vehicle and headquarters power effects cost one-fifth normal because they are paid in equipment points.

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

#### References

**Ref — Constructs**
Source: context/rules/HeroesHandbook-rules__chunk_194.md
Locator: lines 13879-13935
Extract: whole

```source
Since they are capable of action on their own (rather than just improving their owner's abilities), constructs are considered minions — full-fledged characters — rather than devices or equipment and are acquired using the Minions advantage or summoned or created by a Summon effect.
```
