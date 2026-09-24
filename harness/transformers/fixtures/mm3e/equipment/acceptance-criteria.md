# Acceptance Criteria — Equipment Module

Source epic: `(E) Equip Hero` — Pass 2 story map decomposition.
Domain sketch: `docs/equipment/equipment-domain-sketch.md`.

---

## Story: `Acquire Equipment Advantage Ranks`

**Story type:** user

### Domain terms

- *Equipment Advantage* — character trait granting equipment points per rank
- *Equipment Points* — currency for purchasing items
- *Rank* — the level of the advantage purchased

### Acceptance criteria

1. **WHEN** the *Player* selects the *Equipment Advantage* at rank 1 during character creation
   **THEN** the *System* grants 5 *Equipment Points* to the character's pool
   **Evidence:** HeroesHandbook-rules__chunk_162 — "Equipment advantage" section

2. **WHEN** the *Player* increases the *Equipment Advantage* rank
   **THEN** the *System* adds the corresponding *Equipment Points* to the existing pool
   **AND** the total pool reflects all ranks purchased
   **Evidence:** HeroesHandbook-rules__chunk_162 — acquisition rules

3. **WHEN** the *Player* has zero ranks in the *Equipment Advantage*
   **THEN** the *System* provides no *Equipment Points*
   **BUT** the character may still receive equipment via GM ruling or story circumstance
   **Evidence:** HeroesHandbook-rules__chunk_162

4. **WHEN** the *Player* reviews the character sheet
   **THEN** the *System* displays the current *Equipment Points* pool and remaining budget
   **Evidence:** HeroesHandbook-rules__chunk_162

---

## Story: `Pay Equipment Points for Item`

**Story type:** user

### Domain terms

- *Equipment Points* — currency for item purchase
- *Item Cost* — the point cost of the specific piece of equipment
- *Equipment Pool* — remaining balance of unspent equipment points

### Acceptance criteria

1. **WHEN** the *Player* selects an item with a listed point cost within the current *Equipment Pool*
   **THEN** the *System* adds the item to the character's equipment list
   **AND** decrements the *Equipment Pool* by the item's cost
   **Evidence:** HeroesHandbook-rules__chunk_162

2. **WHEN** the *Player* attempts to purchase an item whose cost exceeds the remaining *Equipment Pool*
   **THEN** the *System* rejects the purchase
   **BUT** the *Equipment Pool* is unchanged
   **Evidence:** HeroesHandbook-rules__chunk_162 — pool limit rule

3. **WHEN** the *Player* sells or removes an item
   **THEN** the *System* returns the item's *Equipment Points* to the *Equipment Pool*
   **Evidence:** HeroesHandbook-rules__chunk_162

4. **WHEN** the *Player* purchases multiple items
   **THEN** the *System* deducts each item's cost sequentially until the pool is exhausted
   **Evidence:** HeroesHandbook-rules__chunk_162

---

## Story: `Enforce Equipment Bonus Non-stacking`

**Story type:** system

### Domain terms

- *Equipment Bonus* — Toughness or other bonus from equipment
- *Stacking Rule* — only the highest equipment bonus of the same type applies
- *Protection* — the Toughness bonus effect

### Acceptance criteria

1. **WHEN** a character wears multiple pieces of armor simultaneously
   **THEN** the *System* applies only the highest *Equipment Bonus* to Toughness
   **BUT** the lower bonuses do not add to the total
   **Evidence:** HeroesHandbook-rules__chunk_164 — "The Limits of Equipment"

2. **WHEN** a character has both an equipment *Protection* bonus and a device *Protection* bonus
   **THEN** the *System* applies both bonuses (they are different bonus types)
   **AND** the character's Toughness reflects the sum
   **Evidence:** HeroesHandbook-rules__chunk_176 — super-shield stacking rule

3. **WHEN** a character's total equipment Toughness bonus would exceed the series power level
   **THEN** the *System* caps the effective Toughness at the power level
   **Evidence:** HeroesHandbook-rules__chunk_175 — PL cap rule

4. **WHEN** the *System* calculates defense for a damage resistance check
   **THEN** only one equipment armor bonus contributes to the Toughness total
   **Evidence:** HeroesHandbook-rules__chunk_164

---

## Story: `Build Alternate Equipment Array`

**Story type:** user

### Domain terms

- *Alternate Equipment* — array of items usable one at a time
- *Array Cost* — full cost for most expensive item plus 1 point per additional
- *Active Item* — the one item currently selected from the array

### Acceptance criteria

1. **WHEN** the *Player* designates multiple items as an *Alternate Equipment* array
   **THEN** the *System* charges full cost for the most expensive and 1 point per additional item
   **Evidence:** HeroesHandbook-rules__chunk_163

2. **WHEN** the *Player* activates a different item from the *Alternate Equipment* array
   **THEN** the *System* deactivates the previously *Active Item*
   **AND** only one item is available at a time
   **Evidence:** HeroesHandbook-rules__chunk_163

3. **WHEN** the *Player* spends a hero point during play
   **THEN** the *System* permits adding one non-array item for one scene
   **BUT** the temporary item is removed at the scene's end
   **Evidence:** HeroesHandbook-rules__chunk_163

4. **WHEN** the *Player* reviews the utility belt array
   **THEN** the *System* shows all available items and the current *Active Item*
   **Evidence:** HeroesHandbook-rules__chunk_166 — utility belt

---

## Story: `Access On-Hand Item with Hero Point`

**Story type:** user

### Domain terms

- *On-Hand Equipment* — item produced for one scene via hero-point stunt
- *Hero Point* — currency spent to perform equipment stunts
- *GM Plausibility* — gamemaster judgment on whether having the item is possible

### Acceptance criteria

1. **WHEN** the *Player* spends a hero point to produce a specific item in a scene
   **THEN** the *GM* determines whether having that item on-hand is plausible
   **AND** if approved, the *System* makes the item available for one scene
   **Evidence:** HeroesHandbook-rules__chunk_163

2. **WHEN** the scene in which the *On-Hand Equipment* was produced ends
   **THEN** the *System* removes the item from the character's available gear
   **BUT** the character's equipment pool is not affected
   **Evidence:** HeroesHandbook-rules__chunk_163

3. **WHEN** the *GM* rules that having the item is not plausible
   **THEN** the hero point is not spent
   **AND** the item is unavailable
   **Evidence:** HeroesHandbook-rules__chunk_163

4. **WHEN** the *Player* attempts to use the *On-Hand Equipment* stunt for a vehicle
   **THEN** the same hero point rule applies
   **Evidence:** HeroesHandbook-rules__chunk_163

---

## Story: `Pool Equipment Points with Team Members`

**Story type:** user

### Domain terms

- *Team Equipment Pool* — combined pool from multiple characters' Equipment advantages
- *Shared Vehicle* / *Shared Headquarters* — asset co-owned by the team

### Acceptance criteria

1. **WHEN** multiple characters agree to pool *Equipment Points* for a shared asset
   **THEN** the *System* divides the asset's total cost among the contributing characters
   **AND** each character's pool is decremented by their agreed share
   **Evidence:** HeroesHandbook-rules__chunk_187 — team HQ pooling; chunk_181 — team vehicles

2. **WHEN** a team member leaves the group
   **THEN** their portion of the shared asset cost is returned to their pool
   **AND** the remaining team must cover the gap or lose features
   **Evidence:** HeroesHandbook-rules__chunk_187

3. **WHEN** the team's combined pool is insufficient to cover the full asset cost
   **THEN** the *System* rejects the purchase
   **Evidence:** HeroesHandbook-rules__chunk_187

4. **WHEN** the *Player* reviews team asset costs
   **THEN** the *System* shows each member's contribution share
   **Evidence:** HeroesHandbook-rules__chunk_187

---

## Story: `Select Simple Melee Weapon`

**Story type:** user

### Domain terms

- *Simple Melee Weapon* — club, knife, brass knuckles, stun gun, etc.
- *Damage Rank* — the weapon's Damage effect rank
- *Equipment Points* — cost in points

### Acceptance criteria

1. **WHEN** the *Player* selects a simple melee weapon from the equipment list
   **THEN** the *System* records the weapon's Damage effect and cost
   **AND** deducts the cost from the *Equipment Pool*
   **Evidence:** HeroesHandbook-rules__chunk_168 — simple weapons table

2. **WHEN** the character uses the weapon in combat
   **THEN** the *System* adds the wielder's *Strength* rank to the weapon's *Damage Rank* for Strength-based weapons
   **Evidence:** HeroesHandbook-rules__chunk_167 — melee weapon rules

3. **WHEN** the *Player* selects brass knuckles
   **THEN** the *System* applies a +1 bonus to unarmed strike Damage
   **Evidence:** HeroesHandbook-rules__chunk_169 — brass knuckles entry

4. **WHEN** the *Player* selects a stun gun
   **THEN** the *System* applies the Affliction effect (not Damage)
   **AND** the Strength-based rule does not apply
   **Evidence:** HeroesHandbook-rules__chunk_169

---

## Story: `Select Archaic Melee Weapon`

**Story type:** user

### Domain terms

- *Archaic Melee Weapon* — sword, battleaxe, spear, warhammer
- *Weapon Toughness* — structural rating; breakage threshold

### Acceptance criteria

1. **WHEN** the *Player* selects an archaic weapon
   **THEN** the *System* applies its Strength-based Damage effect
   **Evidence:** HeroesHandbook-rules__chunk_169

2. **WHEN** the wielder's *Strength* rank exceeds the weapon's *Weapon Toughness*
   **THEN** the weapon breaks on use
   **AND** the weapon is removed from available equipment
   **Evidence:** HeroesHandbook-rules__chunk_167

3. **WHEN** the character uses an archaic weapon
   **THEN** the *System* uses the weapon's listed critical threat range
   **Evidence:** HeroesHandbook-rules__chunk_168

4. **WHEN** the *Player* pays 1 extra equipment point for the weapon
   **THEN** the critical threat range increases by 1
   **Evidence:** HeroesHandbook-rules__chunk_168 — critical range extension

---

## Story: `Select Exotic Melee Weapon`

**Story type:** user

### Domain terms

- *Exotic Melee Weapon* — chain, chainsaw, nunchaku, whip
- *Reach* — extended range for melee attacks
- *Improved Grab* / *Improved Trip* — advantage-equivalent effects from certain weapons

### Acceptance criteria

1. **WHEN** the *Player* selects a chain
   **THEN** the *System* grants Reach 2 and the benefits of *Improved Grab* and *Improved Trip*
   **Evidence:** HeroesHandbook-rules__chunk_169 — chain entry

2. **WHEN** the *Player* selects a whip
   **THEN** the *System* grants Reach 3 and the benefits of *Improved Grab* and *Improved Trip*
   **Evidence:** HeroesHandbook-rules__chunk_169 — whip entry

3. **WHEN** the *Player* selects a chainsaw
   **THEN** the *System* applies a fixed Damage rank (not Strength-based)
   **Evidence:** HeroesHandbook-rules__chunk_169

4. **WHEN** the *Player* uses an exotic weapon with Reach
   **THEN** the *System* allows melee attacks at the extended range
   **BUT** attacks at point-blank range still apply
   **Evidence:** HeroesHandbook-rules__chunk_169

---

## Story: `Add Weapon Accessory`

**Story type:** user

### Domain terms

- *Weapon Accessory* — optional attachment costing 1 equipment point
- *Laser Sight* / *Targeting Scope* / *Suppressor* / *Stun Ammo* — specific accessory types

### Acceptance criteria

1. **WHEN** the *Player* adds a laser sight to a ranged weapon
   **THEN** the *System* charges 1 *Equipment Point* and applies +2 to attack rolls when aiming
   **Evidence:** HeroesHandbook-rules__chunk_174 — accessories

2. **WHEN** the *Player* adds a targeting scope
   **THEN** the *System* charges 1 *Equipment Point* and doubles aiming benefits
   **Evidence:** HeroesHandbook-rules__chunk_174

3. **WHEN** the *Player* adds a suppressor
   **THEN** the *System* charges 1 *Equipment Point* and applies Subtle 1 (DC 20 hearing check)
   **Evidence:** HeroesHandbook-rules__chunk_174

4. **WHEN** the *Player* adds stun ammunition
   **THEN** the *System* charges 1 *Equipment Point* and changes the weapon's Damage to an Affliction
   **Evidence:** HeroesHandbook-rules__chunk_174

---

## Story: `Apply Grenade Burst Area Effect`

**Story type:** system

### Domain terms

- *Grenade* — thrown area-effect weapon
- *Burst Area* — effect radius centered on target point
- *Dodge DC* — check to halve or avoid area effect

### Acceptance criteria

1. **WHEN** a *Player* throws a fragmentation grenade at a target point
   **THEN** the *System* applies Damage 5 to all characters in the burst area
   **AND** each target makes a Dodge check against DC 15 to take half damage
   **Evidence:** HeroesHandbook-rules__chunk_175 — fragmentation grenade

2. **WHEN** a target in the burst area succeeds on the *Dodge DC* check
   **THEN** the *System* halves the Damage rank applied to that target
   **Evidence:** HeroesHandbook-rules__chunk_175

3. **WHEN** a flash-bang grenade is thrown
   **THEN** the *System* applies Dazzle 4 to vision and hearing for all targets in the burst
   **AND** each target makes a separate Dodge check for the Dazzle effect
   **Evidence:** HeroesHandbook-rules__chunk_175

4. **WHEN** a smoke grenade is thrown
   **THEN** the *System* creates a Cloud Area of visual Concealment
   **AND** the cloud persists until dispersed
   **Evidence:** HeroesHandbook-rules__chunk_175

---

## Story: `Apply Grenade Cloud Area Effect`

**Story type:** system

### Domain terms

- *Cloud Area* — lingering area effect
- *Sleep Gas* — Affliction grenade (fatigued/exhausted/asleep)
- *Tear Gas* — Affliction grenade (dazed/blinded, stunned, incapacitated)

### Acceptance criteria

1. **WHEN** a sleep gas grenade is deployed
   **THEN** the *System* creates a Cloud Area with Affliction (sleep progression) active each round
   **AND** each target in the cloud makes a resistance check each round
   **Evidence:** HeroesHandbook-rules__chunk_175

2. **WHEN** a target moves out of the cloud area
   **THEN** the *System* stops applying the cloud effect to that target
   **Evidence:** HeroesHandbook-rules__chunk_175

3. **WHEN** tear gas is deployed
   **THEN** the *System* applies vision and hearing Affliction to all targets in the cloud
   **AND** targets unable to see are considered to have concealment granted against them
   **Evidence:** HeroesHandbook-rules__chunk_175

4. **WHEN** a new cloud grenade is thrown into an existing cloud
   **THEN** the *GM* determines whether the effects combine or the new cloud overlaps
   **Evidence:** HeroesHandbook-rules__chunk_175

---

## Story: `Place Explosive Device`

**Story type:** user

### Domain terms

- *Explosive* — placed area-damage device (dynamite, plastic explosive)
- *Damage Rank Scaling* — each doubling of quantity adds +1 Damage rank

### Acceptance criteria

1. **WHEN** the *Player* places one stick of dynamite
   **THEN** the *System* applies Burst Area Damage 5 at detonation
   **Evidence:** HeroesHandbook-rules__chunk_175

2. **WHEN** the *Player* places two sticks of dynamite
   **THEN** the *System* applies Burst Area Damage 6 (Damage 5 +1 for doubling)
   **Evidence:** HeroesHandbook-rules__chunk_175

3. **WHEN** a target is in the explosion burst area
   **THEN** the *System* applies the Dodge check to halve damage
   **Evidence:** HeroesHandbook-rules__chunk_175

4. **WHEN** the *Player* uses 1 lb of plastic explosive
   **THEN** the *System* applies Burst Area Damage 10 at detonation
   **Evidence:** HeroesHandbook-rules__chunk_175

---

## Story: `Select Archaic Armor Type`

**Story type:** user

### Domain terms

- *Archaic Armor* — leather, chain-mail, plate-mail, full-plate
- *Protection* — the Toughness bonus effect from armor

### Acceptance criteria

1. **WHEN** the *Player* selects chain-mail armor
   **THEN** the *System* applies Protection 3 as an equipment Toughness bonus
   **AND** deducts 3 *Equipment Points* from the pool
   **Evidence:** HeroesHandbook-rules__chunk_175 — armor table

2. **WHEN** the *Player* already has armor equipped and selects a second piece
   **THEN** the *System* applies only the higher *Protection* value
   **BUT** does not stack both bonuses
   **Evidence:** HeroesHandbook-rules__chunk_164

3. **WHEN** the character's Toughness would exceed the series power level
   **THEN** the *System* caps Toughness at the power level
   **Evidence:** HeroesHandbook-rules__chunk_175

4. **WHEN** a device provides Protection on the same character
   **THEN** the *System* allows both the equipment armor bonus and the device Protection to apply
   **AND** they do not suppress each other
   **Evidence:** HeroesHandbook-rules__chunk_176

---

## Story: `Select Modern Armor Type`

**Story type:** user

### Domain terms

- *Modern Armor* — undercover shirt, bulletproof vest
- *Limited Modifier* — restricts Protection to ballistic damage only

### Acceptance criteria

1. **WHEN** the *Player* selects a bulletproof vest
   **THEN** the *System* applies Protection 4 limited to ballistic damage
   **AND** the vest has the Subtle property (concealed)
   **Evidence:** HeroesHandbook-rules__chunk_177

2. **WHEN** the character is struck by a non-ballistic attack
   **THEN** the vest's *Limited* Protection does not apply to Toughness
   **Evidence:** HeroesHandbook-rules__chunk_177

3. **WHEN** the character wears both an undercover shirt and a bulletproof vest
   **THEN** the *System* applies only the vest's higher Protection (4)
   **BUT** not both simultaneously
   **Evidence:** HeroesHandbook-rules__chunk_164

4. **WHEN** the *Player* selects an undercover shirt
   **THEN** the *System* applies Protection 2 limited to ballistic with Subtle
   **Evidence:** HeroesHandbook-rules__chunk_177

---

## Story: `Select Shield Type`

**Story type:** user

### Domain terms

- *Shield* — active defense equipment granting Dodge and Parry bonuses
- *Active Defense Bonus* — enhancement to Dodge and Parry defenses

### Acceptance criteria

1. **WHEN** the *Player* selects a medium shield
   **THEN** the *System* grants +2 to both Dodge and Parry
   **AND** deducts 4 *Equipment Points*
   **Evidence:** HeroesHandbook-rules__chunk_177 — shield table

2. **WHEN** the character uses a shield as an *Alternate Effect* weapon
   **THEN** the *System* disables the shield's active defense bonus for that round
   **Evidence:** HeroesHandbook-rules__chunk_176 — super-shield Alternate Effect

3. **WHEN** the shield is in defensive mode
   **THEN** the *System* adds the active defense bonus to both Dodge and Parry
   **Evidence:** HeroesHandbook-rules__chunk_178

4. **WHEN** the character is disarmed of the shield
   **THEN** the *System* removes the active defense bonus immediately
   **Evidence:** HeroesHandbook-rules__chunk_178

---

## Story: `Designate Power as Removable Device`

**Story type:** user

### Domain terms

- *Removable* — flaw applied to external powers
- *Device* — power with Removable or Easily Removable flaw
- *Flaw Cost Reduction* — point cost decrease from applying the flaw

### Acceptance criteria

1. **WHEN** the *Player* designates a power as having the *Removable* flaw
   **THEN** the *System* reduces the power's point cost by the Removable discount
   **AND** marks the power as a device (external item)
   **Evidence:** HeroesHandbook-rules__chunk_158 — device definition

2. **WHEN** an opponent removes or destroys the device in play
   **THEN** the *System* removes all powers tied to that device from the character
   **AND** restores them when the device is recovered
   **Evidence:** HeroesHandbook-rules__chunk_158

3. **WHEN** the device is permanently lost
   **THEN** the *System* allows the character to reallocate the power points
   **BUT** the device must be purchased again if the character wants it back
   **Evidence:** HeroesHandbook-rules__chunk_158

4. **WHEN** the *Player* reviews device cost
   **THEN** the *System* shows the power's base cost and the Removable-discounted cost
   **Evidence:** HeroesHandbook-rules__chunk_158

---

## Story: `Designate Power as Easily Removable Device`

**Story type:** user

### Domain terms

- *Easily Removable* — more severe form of Removable flaw with greater cost reduction
- *Stripping Threshold* — how easily the device can be taken in play

### Acceptance criteria

1. **WHEN** the *Player* designates a small or loosely carried item as *Easily Removable*
   **THEN** the *System* applies a larger cost reduction than standard Removable
   **Evidence:** HeroesHandbook-rules__chunk_158

2. **WHEN** an opponent attempts to remove an *Easily Removable* device
   **THEN** the *System* applies a lower threshold (easier to strip) compared to standard Removable
   **Evidence:** HeroesHandbook-rules__chunk_158

3. **WHEN** the device is stripped
   **THEN** the *System* removes all associated powers as with any Removable device
   **Evidence:** HeroesHandbook-rules__chunk_158

4. **WHEN** the *Player* attempts to apply *Easily Removable* to a bulky worn device (battlesuit)
   **THEN** the *System* flags that standard *Removable* is appropriate instead
   **Evidence:** HeroesHandbook-rules__chunk_158

---

## Story: `Mark Device as Indestructible`

**Story type:** user

### Domain terms

- *Indestructible* — modifier preventing permanent destruction of a Removable device
- *Cost Adjustment* — Indestructible reduces the flaw discount

### Acceptance criteria

1. **WHEN** the *Player* applies *Indestructible* to a Removable device
   **THEN** the *System* reduces the Removable cost discount by the Indestructible surcharge
   **AND** the device's net cost increases compared to a non-Indestructible version
   **Evidence:** HeroesHandbook-rules__chunk_158

2. **WHEN** an opponent destroys an *Indestructible* device
   **THEN** the *System* rejects the permanent destruction
   **AND** treats the device as temporarily lost or damaged, not eliminated
   **Evidence:** HeroesHandbook-rules__chunk_158

3. **WHEN** an *Indestructible* device is taken away
   **THEN** the character still loses its powers until recovered
   **BUT** the device cannot be permanently removed from play
   **Evidence:** HeroesHandbook-rules__chunk_158

4. **WHEN** the *Player* attempts to add *Indestructible* to a power without Removable
   **THEN** the *System* rejects the modifier (Indestructible requires Removable or Easily Removable)
   **Evidence:** HeroesHandbook-rules__chunk_158

---

## Story: `Build Battlesuit Power Armor Device`

**Story type:** user

### Domain terms

- *Battlesuit* — comprehensive power-armor device
- *Removable Device* — device that can be taken away in play
- *Bundled Powers* — Protection, attack, movement, Senses all on one device

### Acceptance criteria

1. **WHEN** the *Player* builds a battlesuit by applying Removable to a set of powers
   **THEN** the *System* groups all those powers under one device record
   **AND** calculates the combined cost with the Removable discount applied
   **Evidence:** HeroesHandbook-rules__chunk_159 — battlesuit structure

2. **WHEN** the battlesuit is removed from the wearer
   **THEN** the *System* simultaneously removes Protection, attack, movement, and Senses powers
   **AND** the character's stats revert to their base values
   **Evidence:** HeroesHandbook-rules__chunk_159

3. **WHEN** the *Player* adds Alternate Effects to battlesuit attack modes
   **THEN** the *System* treats them as standard Alternate Effects within the battlesuit device
   **Evidence:** HeroesHandbook-rules__chunk_159

4. **WHEN** the *Player* attempts to use two battlesuit attack modes simultaneously
   **THEN** the *System* allows only one Alternate Effect at a time
   **Evidence:** HeroesHandbook-rules__chunk_159

---

## Story: `Use Device Temporarily Without Power Points`

**Story type:** user

### Domain terms

- *Temporary Device Use* — using another character's device for one scene without paying power points
- *Hero Point* — currency for temporary device borrowing (GM may require)

### Acceptance criteria

1. **WHEN** the *Player* finds a device and uses it for one scene without paying power points
   **THEN** the *System* makes the device's powers available for that scene only
   **AND** removes them at the scene's end
   **Evidence:** HeroesHandbook-rules__chunk_158

2. **WHEN** the *Player* uses another character's device
   **THEN** the *GM* may require spending a hero point (analogous to a power stunt)
   **Evidence:** HeroesHandbook-rules__chunk_158

3. **WHEN** the scene ends
   **THEN** the borrowed device powers are no longer available
   **BUT** the power points remain unspent (temporary use costs no pp)
   **Evidence:** HeroesHandbook-rules__chunk_158

4. **WHEN** the *Player* wants to continue using the device beyond one scene
   **THEN** the *System* requires purchasing it as a regular power (spending power points)
   **Evidence:** HeroesHandbook-rules__chunk_158

---

## Story: `Define Invention Effect and Point Cost`

**Story type:** user

### Domain terms

- *Invention* — temporary device created by a character with the Inventor advantage
- *Point Cost* — the power-point cost of the invention's effects
- *Design Check DC* — DC 10 + point cost

### Acceptance criteria

1. **WHEN** the *Player* declares an invention with a specific set of power effects
   **THEN** the *System* calculates the total *Point Cost* from the effects
   **AND** sets the Design Check DC to 10 + that cost
   **Evidence:** HeroesHandbook-rules__chunk_160

2. **WHEN** the *Player* specifies the invention's effects
   **THEN** each effect is costed using standard power-effect rules
   **AND** the total is the invention's declared point cost
   **Evidence:** HeroesHandbook-rules__chunk_160

3. **WHEN** the declared point cost is high
   **THEN** both check DCs and construction times increase proportionally
   **Evidence:** HeroesHandbook-rules__chunk_160

4. **WHEN** the *Player* reviews the invention definition
   **THEN** the *System* shows the effects, total cost, DC for both checks, and time required
   **Evidence:** HeroesHandbook-rules__chunk_160

---

## Story: `Make Design Check in Secret`

**Story type:** system

### Domain terms

- *Design Check* — Technology check, DC 10 + pp cost, made by GM in secret
- *Flawed Design* — design that appears correct but will not function (3+ degrees failure)

### Acceptance criteria

1. **WHEN** the design phase begins
   **THEN** the *GM* rolls the Technology check secretly
   **AND** the *Player* does not know the result
   **Evidence:** HeroesHandbook-rules__chunk_160

2. **WHEN** the *GM* rolls 3 or more degrees of failure
   **THEN** the *System* records the design as flawed
   **AND** the *Player* is not informed until the invention fails to function
   **Evidence:** HeroesHandbook-rules__chunk_160

3. **WHEN** a flawed invention is used
   **THEN** the *System* reveals the flaw and the invention does not work
   **Evidence:** HeroesHandbook-rules__chunk_160

4. **WHEN** the design check succeeds
   **THEN** the construction phase may begin
   **Evidence:** HeroesHandbook-rules__chunk_160

---

## Story: `Complete Construction Check`

**Story type:** user

### Domain terms

- *Construction Check* — Technology check, DC 10 + pp cost, made by player
- *Construction Time* — 4 hours per power point of cost

### Acceptance criteria

1. **WHEN** the design is complete
   **THEN** the *Player* makes the construction check after the required time elapses
   **AND** the DC is 10 + the invention's total power point cost
   **Evidence:** HeroesHandbook-rules__chunk_160

2. **WHEN** the construction time is 4 hours per point and the *Player* wishes to reduce it
   **THEN** a -5 penalty applies per time rank reduction
   **AND** the *Player* may use a routine check at normal time
   **Evidence:** HeroesHandbook-rules__chunk_160

3. **WHEN** the construction check succeeds
   **THEN** the invention is completed and available for one scene
   **Evidence:** HeroesHandbook-rules__chunk_161

4. **WHEN** the construction check fails
   **THEN** the invention is not completed
   **AND** the design phase may be attempted again
   **Evidence:** HeroesHandbook-rules__chunk_161

---

## Story: `Reuse Invention with Hero Point`

**Story type:** user

### Domain terms

- *Hero Point* — currency for reusing an invention
- *One-Scene Duration* — the default lifespan of an invention

### Acceptance criteria

1. **WHEN** an invention has been used for one scene
   **THEN** the *Player* may spend a hero point to extend use for another scene
   **AND** no further checks are required
   **Evidence:** HeroesHandbook-rules__chunk_161

2. **WHEN** the *Player* wishes to use the invention a third time
   **THEN** another hero point must be spent
   **Evidence:** HeroesHandbook-rules__chunk_161

3. **WHEN** no hero points remain
   **THEN** the invention cannot be reused beyond its current scene
   **BUT** the character may purchase it permanently with power points
   **Evidence:** HeroesHandbook-rules__chunk_161

4. **WHEN** the *Player* decides to make the invention permanent
   **THEN** the *System* adds the invention's powers to the character's permanent traits
   **AND** deducts the power points from the character's total
   **Evidence:** HeroesHandbook-rules__chunk_161

---

## Story: `Jury-Rig Device by Spending Hero Point`

**Story type:** user

### Domain terms

- *Jury-Rigging* — emergency invention skipping the design phase
- *Compressed Construction* — 1 round per power point instead of 4 hours per point
- *DC Penalty* — +5 to construction check DC when jury-rigging

### Acceptance criteria

1. **WHEN** the *Player* spends a hero point to jury-rig a device
   **THEN** the *System* skips the design phase entirely
   **AND** sets construction time to 1 round per power point of cost
   **Evidence:** HeroesHandbook-rules__chunk_161 — jury-rigging rule

2. **WHEN** the jury-rig construction check is made
   **THEN** the DC is the normal construction DC + 5
   **AND** routine checks are not permitted
   **Evidence:** HeroesHandbook-rules__chunk_161

3. **WHEN** the jury-rig check succeeds
   **THEN** the device is available for one scene
   **AND** may be extended with additional hero points
   **Evidence:** HeroesHandbook-rules__chunk_161

4. **WHEN** the jury-rig check fails
   **THEN** the hero point is spent but the device is not created
   **Evidence:** HeroesHandbook-rules__chunk_161

---

## Story: `Perform Magical Ritual`

**Story type:** user

### Domain terms

- *Ritual* — magical equivalent of inventing using Expertise: Magic
- *Research Phase* — 4 hours per power point
- *Performance Phase* — 10 minutes per power point

### Acceptance criteria

1. **WHEN** a character with the *Ritualist* advantage begins a ritual
   **THEN** the research phase uses Expertise: Magic instead of Technology
   **AND** the DC is 10 + power point cost of the ritual
   **Evidence:** HeroesHandbook-rules__chunk_162 — ritual rules

2. **WHEN** the ritual research roll results in 3+ degrees of failure
   **THEN** the ritual is unusable and a mishap may occur
   **AND** the *GM* determines the nature of the mishap
   **Evidence:** HeroesHandbook-rules__chunk_162

3. **WHEN** research succeeds
   **THEN** the performance phase begins (Expertise: Magic check, same DC, 10 min/pp)
   **Evidence:** HeroesHandbook-rules__chunk_162

4. **WHEN** the *Player* jury-rigs a ritual
   **THEN** the same hero-point rule applies: skip research, perform in rounds, DC 15 + cost
   **Evidence:** HeroesHandbook-rules__chunk_162

---

## Story: `Select Vehicle Size Category`

**Story type:** user

### Domain terms

- *Vehicle Size* — category from Medium to Awesome
- *Base Traits* — Strength, Toughness, Defense derived from size
- *Defense Penalty* — negative Defense modifier for large vehicles

### Acceptance criteria

1. **WHEN** the *Player* selects a size category for a vehicle
   **THEN** the *System* sets the vehicle's base Strength, Toughness, and Defense from the category table
   **Evidence:** HeroesHandbook-rules__chunk_179 — vehicle size table

2. **WHEN** the *Player* selects Huge or larger
   **THEN** the *System* applies a Defense penalty (e.g., Huge: -2, Gargantuan: -4)
   **AND** the vehicle is easier to target in combat
   **Evidence:** HeroesHandbook-rules__chunk_179

3. **WHEN** the *Player* pays 1 equipment point per -1 Defense penalty
   **THEN** the *System* removes that penalty from the vehicle's Defense
   **Evidence:** HeroesHandbook-rules__chunk_179

4. **WHEN** the *Player* increases size above Medium
   **THEN** the *System* charges 1 equipment point per size category above Medium
   **Evidence:** HeroesHandbook-rules__chunk_179

---

## Story: `Calculate Vehicle Power Effect at One-Fifth Cost`

**Story type:** system

### Domain terms

- *Vehicle Power Effect* — power built into the vehicle (cloaking, weapons, armor)
- *One-Fifth Cost Rule* — vehicle power effects cost 1/5 normal power-point cost in equipment points

### Acceptance criteria

1. **WHEN** the *Player* adds a Concealment 4 cloaking device to a vehicle
   **THEN** the *System* charges 4 ÷ 5 = rounded equipment points (approximately 1 point)
   **Evidence:** HeroesHandbook-rules__chunk_180 — cloaking device

2. **WHEN** the *Player* adds a smokescreen (Cloud Area Concealment Attack, 12 power points)
   **THEN** the *System* charges 12 ÷ 5 = approximately 2-3 equipment points
   **Evidence:** HeroesHandbook-rules__chunk_180

3. **WHEN** the *Player* adds standard Protection armor to a vehicle
   **THEN** the *System* charges 1 equipment point per +1 Toughness from the armor effect
   **Evidence:** HeroesHandbook-rules__chunk_180

4. **WHEN** the vehicle includes a weapon effect
   **THEN** the *System* applies the one-fifth rule to the weapon's power cost
   **AND** the vehicle weapons are treated as standard power effects in combat
   **Evidence:** HeroesHandbook-rules__chunk_180

---

## Story: `Set Up Alternate Vehicles Array`

**Story type:** user

### Domain terms

- *Alternate Vehicles* — array of vehicles usable one at a time
- *Primary Vehicle* — the most expensive vehicle paid at full cost

### Acceptance criteria

1. **WHEN** the *Player* designates multiple vehicles as an *Alternate Vehicles* array
   **THEN** the *System* charges full cost for the most expensive and 1 point per additional vehicle
   **Evidence:** HeroesHandbook-rules__chunk_181

2. **WHEN** the *Player* activates a secondary vehicle
   **THEN** only that vehicle is available; the primary vehicle is not simultaneously accessible
   **Evidence:** HeroesHandbook-rules__chunk_181

3. **WHEN** the *Player* spends a hero point
   **THEN** a non-array vehicle of equal or lesser cost may be produced for one scene
   **Evidence:** HeroesHandbook-rules__chunk_181

4. **WHEN** the *Player* reviews the vehicle array
   **THEN** all vehicles in the array are listed with their costs and current active status
   **Evidence:** HeroesHandbook-rules__chunk_181

---

## Story: `Select Headquarters Size Category`

**Story type:** user

### Domain terms

- *Headquarters Size* — from Fine/Miniscule to Awesome
- *Starting Size* — Small at 0 points
- *Toughness* — structural Toughness starting at 6

### Acceptance criteria

1. **WHEN** the *Player* starts a headquarters
   **THEN** the *System* sets the default size to Small at 0 equipment points
   **AND** sets structural Toughness to 6
   **Evidence:** HeroesHandbook-rules__chunk_187

2. **WHEN** the *Player* selects a size above Small
   **THEN** the *System* charges 1 equipment point per size step increase
   **Evidence:** HeroesHandbook-rules__chunk_187

3. **WHEN** the *Player* selects a size below Small
   **THEN** the *System* grants 1 equipment point per size step reduction
   **Evidence:** HeroesHandbook-rules__chunk_187

4. **WHEN** the *Player* selects Awesome (small-town scale)
   **THEN** the *System* charges 6 equipment points for size alone
   **Evidence:** HeroesHandbook-rules__chunk_187 — Awesome size entry

---

## Story: `Add Defense System Feature`

**Story type:** user

### Domain terms

- *Defense System* — weapon emplacements in and around the HQ
- *HQ Power Level* — governs maximum feature effect rank (series PL for PCs)
- *Attack Bonus* — equals HQ power level for defense system

### Acceptance criteria

1. **WHEN** the *Player* adds a Defense System feature
   **THEN** the *System* charges 1 equipment point
   **AND** sets the attack effect cost cap at twice the HQ power level
   **Evidence:** HeroesHandbook-rules__chunk_188

2. **WHEN** the Defense System makes an attack
   **THEN** the *System* uses the HQ power level as the attack bonus
   **Evidence:** HeroesHandbook-rules__chunk_188

3. **WHEN** the *Player* attempts to give the Defense System an effect with cost exceeding 2× HQ PL
   **THEN** the *System* rejects the effect or caps it at the allowed maximum
   **Evidence:** HeroesHandbook-rules__chunk_188

4. **WHEN** the headquarters is destroyed
   **THEN** the Defense System is also destroyed
   **AND** can be rebuilt with the next headquarters using the same equipment points
   **Evidence:** HeroesHandbook-rules__chunk_186

---

## Story: `Add Security System Feature`

**Story type:** user

### Domain terms

- *Security System* — locks and alarms protecting the HQ
- *Technology DC* — base DC 20, +5 per additional application, max DC 40
- *Application* — each additional security layer

### Acceptance criteria

1. **WHEN** the *Player* adds one application of a Security System
   **THEN** the *System* charges 1 equipment point and sets bypass DC to 20
   **Evidence:** HeroesHandbook-rules__chunk_188

2. **WHEN** the *Player* adds a second Security System application
   **THEN** the bypass DC increases to 25 (base 20 + 5 per additional)
   **AND** the *System* charges 1 additional equipment point
   **Evidence:** HeroesHandbook-rules__chunk_188

3. **WHEN** the Security System DC reaches 40 (4 applications)
   **THEN** no further Security System applications can be added to this system
   **Evidence:** HeroesHandbook-rules__chunk_188

4. **WHEN** an intruder attempts to bypass the Security System
   **THEN** the *System* requires a Technology check against the installed DC
   **Evidence:** HeroesHandbook-rules__chunk_188

---

## Story: `Add Self-Repairing Feature`

**Story type:** user

### Domain terms

- *Self-Repairing* — feature that heals HQ damage over time
- *Full Rebuild* — two self-repairing applications allow the HQ to rebuild from destruction

### Acceptance criteria

1. **WHEN** the *Player* adds the Self-Repairing feature once
   **THEN** the *System* charges 1 equipment point and the HQ recovers from damage over time
   **Evidence:** HeroesHandbook-rules__chunk_191

2. **WHEN** the *Player* adds Self-Repairing twice
   **THEN** if the HQ is destroyed, it rebuilds itself within one week
   **Evidence:** HeroesHandbook-rules__chunk_191

3. **WHEN** the HQ is destroyed and does not have Self-Repairing
   **THEN** the character must rebuild it manually using the same equipment points
   **Evidence:** HeroesHandbook-rules__chunk_186

4. **WHEN** the HQ is destroyed and has Self-Repairing × 2
   **THEN** the *System* marks it as rebuilding (one week)
   **AND** the character retains the equipment points during reconstruction
   **Evidence:** HeroesHandbook-rules__chunk_191

---

## Story: `Pool Equipment Points for Team Headquarters`

**Story type:** user

### Domain terms

- *Team Headquarters* — HQ with cost shared among multiple characters
- *Shared Cost* — equipment point contribution from each team member

### Acceptance criteria

1. **WHEN** a team agrees to share a headquarters
   **THEN** each member contributes equipment points up to their agreed share
   **AND** the *System* deducts each member's share from their pool
   **Evidence:** HeroesHandbook-rules__chunk_192 — team HQ

2. **WHEN** the total team contribution covers the HQ cost
   **THEN** the *System* marks the headquarters as owned by the team
   **Evidence:** HeroesHandbook-rules__chunk_192

3. **WHEN** a team member's contribution is returned
   **THEN** those equipment points are restored to their pool
   **AND** the remaining team must cover the gap or lose features
   **Evidence:** HeroesHandbook-rules__chunk_192

4. **WHEN** the team establishes alternate headquarters
   **THEN** the same Alternate Equipment cost rule applies (full cost for most expensive, 1 point per additional)
   **Evidence:** HeroesHandbook-rules__chunk_192

---

## Story: `Set Construct Stamina to None`

**Story type:** system

### Domain terms

- *No Stamina* — constructs have no Stamina (cannot recover naturally)
- *Repair* — the only way to restore a damaged construct

### Acceptance criteria

1. **WHEN** a construct is created
   **THEN** the *System* sets its Stamina to absent (no Stamina score)
   **AND** marks it as unable to recover from damage normally
   **Evidence:** HeroesHandbook-rules__chunk_194

2. **WHEN** a construct is damaged
   **THEN** the *System* does not apply any natural recovery
   **AND** the damage persists until repaired
   **Evidence:** HeroesHandbook-rules__chunk_195

3. **WHEN** a character uses the Technology skill to repair a construct
   **THEN** the *System* applies repair equal to the check result's degree of success
   **Evidence:** HeroesHandbook-rules__chunk_195

4. **WHEN** the construct is reduced to incapacitated
   **THEN** it remains incapacitated until repaired
   **BUT** the owner's equipment points are not spent again
   **Evidence:** HeroesHandbook-rules__chunk_194

---

## Story: `Grant Construct Immunity to Fortitude Effects`

**Story type:** system

### Domain terms

- *Fortitude Immunity* — constructs are immune to effects resisted by Fortitude
- *Object Exception* — effects that work on objects can still affect constructs

### Acceptance criteria

1. **WHEN** a Fortitude-resisted effect targets a construct
   **THEN** the *System* automatically grants success to the construct's resistance
   **AND** the effect does not apply
   **Evidence:** HeroesHandbook-rules__chunk_194

2. **WHEN** an effect that works on objects targets a construct
   **THEN** the *System* allows the effect to apply normally
   **Evidence:** HeroesHandbook-rules__chunk_194

3. **WHEN** an automaton (no Intellect/Presence) is targeted by a Will effect
   **THEN** the *System* grants immunity automatically
   **Evidence:** HeroesHandbook-rules__chunk_194

4. **WHEN** an intelligent construct is targeted by a Will effect
   **THEN** it makes a resistance check normally (not immune)
   **Evidence:** HeroesHandbook-rules__chunk_194

---

## Story: `Verify Zero Net Cost for Standard Construct Traits`

**Story type:** system

### Domain terms

- *Net Cost* — the power-point cost of the construct's special trait package (absent abilities + Immunity)
- *Absent Abilities* — two ability scores not purchased (−30 pp)
- *Immunity to Fortitude Effects* — +30 pp

### Acceptance criteria

1. **WHEN** a construct is created with the standard package (two abilities absent + Immunity to Fortitude)
   **THEN** the *System* calculates that the cost reduction from absent abilities equals the Immunity cost
   **AND** the net cost is zero
   **Evidence:** HeroesHandbook-rules__chunk_194 — "These qualities average out to 0 points"

2. **WHEN** the construct has Intellect + Presence absent (automaton)
   **THEN** the *System* confirms the -30 pp reduction
   **AND** the +30 pp Immunity to Fortitude Effects offsets it exactly
   **Evidence:** HeroesHandbook-rules__chunk_194

3. **WHEN** the construct has Strength + Agility absent (immobile intellect)
   **THEN** the same net-zero calculation applies
   **Evidence:** HeroesHandbook-rules__chunk_194

4. **WHEN** the *Player* attempts to purchase only one absent ability
   **THEN** the *System* flags that the standard construct package requires a full pair to be absent
   **Evidence:** HeroesHandbook-rules__chunk_194

---

## Story: `Issue Order to Construct on Move Action`

**Story type:** user

### Domain terms

- *Order* — command given to a construct by its owner
- *Move Action* — one of the action types used to command a construct
- *Last Order* — the most recent command; followed until new order given

### Acceptance criteria

1. **WHEN** the *Player* issues an order to the construct as a move action
   **THEN** the *System* records the order and the construct begins executing it
   **Evidence:** HeroesHandbook-rules__chunk_195

2. **WHEN** no new order is given during a round
   **THEN** the construct continues executing the *Last Order*
   **Evidence:** HeroesHandbook-rules__chunk_195

3. **WHEN** an intelligent construct receives an ambiguous order
   **THEN** it interprets the order using its Intellect and acts accordingly
   **BUT** an automaton executes only the literal instruction
   **Evidence:** HeroesHandbook-rules__chunk_195

4. **WHEN** the construct completes an order and receives no new command
   **THEN** the *System* keeps the construct on standby at its current position
   **Evidence:** HeroesHandbook-rules__chunk_195

---

## Story: `Choose Construct Ability Profile`

**Story type:** user

### Domain terms

- *Automaton Profile* — no Intellect, no Presence (immune to Will and interaction)
- *Immobile Intellect Profile* — no Strength, no Agility (AI computer form)
- *Full Profile* — purchases one pair back at power-point cost

### Acceptance criteria

1. **WHEN** the *Player* chooses the Automaton profile
   **THEN** the *System* removes Intellect and Presence from the construct
   **AND** grants immunity to Will effects and interaction skills
   **Evidence:** HeroesHandbook-rules__chunk_194

2. **WHEN** the *Player* chooses the Immobile Intellect profile
   **THEN** the *System* removes Strength and Agility from the construct
   **AND** the construct can direct others but cannot take physical actions
   **Evidence:** HeroesHandbook-rules__chunk_194

3. **WHEN** the *Player* wishes to partially restore absent abilities
   **THEN** the *System* charges 2 power points per +1 rank (starting at -5)
   **Evidence:** HeroesHandbook-rules__chunk_194

4. **WHEN** the *Player* selects a profile
   **THEN** the *System* shows the resulting ability scores and the net cost calculation
   **Evidence:** HeroesHandbook-rules__chunk_194

---

## Story: `Repair Damaged Construct with Technology Check`

**Story type:** user

### Domain terms

- *Technology Skill* — skill used for repairing constructs
- *Repair Check* — Technology check against the construct's damage level

### Acceptance criteria

1. **WHEN** a character with Technology skill attempts to repair a damaged construct
   **THEN** the *System* requires a Technology check against the appropriate DC
   **AND** the degree of success determines how much damage is repaired
   **Evidence:** HeroesHandbook-rules__chunk_195

2. **WHEN** the repair check succeeds at 2+ degrees
   **THEN** the construct's damage condition improves significantly
   **Evidence:** HeroesHandbook-rules__chunk_195

3. **WHEN** the repair check fails
   **THEN** no damage is repaired
   **AND** the construct remains at its current damage state
   **Evidence:** HeroesHandbook-rules__chunk_195

4. **WHEN** an automaton construct is repaired
   **THEN** it does not require medical care (Technology, not Treatment skill)
   **Evidence:** HeroesHandbook-rules__chunk_195

---

## Source Evidence Summary

All AC in this document cite context chunks from `c:\dev\mm3e-online-holistic\context\rules\`:

| Chunk | Section |
| --- | --- |
| HeroesHandbook-rules__chunk_158 | Ch7 Gadgets & Gear — device definition and Removable |
| HeroesHandbook-rules__chunk_159 | Battlesuits |
| HeroesHandbook-rules__chunk_160 | Enhanced Equipment and inventing design phase |
| HeroesHandbook-rules__chunk_161 | Using the Invention and jury-rigging |
| HeroesHandbook-rules__chunk_162 | What Items Do You Pay For? and rituals |
| HeroesHandbook-rules__chunk_163 | Alternate Equipment and on-hand equipment |
| HeroesHandbook-rules__chunk_164 | The Limits of Equipment |
| HeroesHandbook-rules__chunk_166 | Utility Belt |
| HeroesHandbook-rules__chunk_167 | Melee Weapons |
| HeroesHandbook-rules__chunk_168 | Simple Weapons traits |
| HeroesHandbook-rules__chunk_169 | Simple and Exotic Melee Weapons table |
| HeroesHandbook-rules__chunk_174 | Explosives and weapon accessories |
| HeroesHandbook-rules__chunk_175 | Grenades and Explosives, Armor introduction |
| HeroesHandbook-rules__chunk_176 | Super-shields |
| HeroesHandbook-rules__chunk_177 | Modern armor and shield tables |
| HeroesHandbook-rules__chunk_178 | Shield descriptions and vehicles introduction |
| HeroesHandbook-rules__chunk_179 | Vehicle Size Categories |
| HeroesHandbook-rules__chunk_180 | Vehicle Features |
| HeroesHandbook-rules__chunk_181 | Alternate Vehicles |
| HeroesHandbook-rules__chunk_186 | Special Vehicles and HQ introduction |
| HeroesHandbook-rules__chunk_187 | Equipment Cost — HQ size and traits |
| HeroesHandbook-rules__chunk_188 | HQ Features — Defense and Security Systems |
| HeroesHandbook-rules__chunk_191 | Library, Living Space, Self-repairing |
| HeroesHandbook-rules__chunk_192 | Workshop and team HQ |
| HeroesHandbook-rules__chunk_194 | Constructs |
| HeroesHandbook-rules__chunk_195 | Commanding Constructs and repair |
