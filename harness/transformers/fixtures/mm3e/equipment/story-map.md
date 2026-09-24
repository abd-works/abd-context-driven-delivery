# Story Map — Equipment Module (Pass 2)

Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).
Source epic in global map: `(E) Equip Hero` — fully decomposed here to Pass 2 depth.

---

(E) Equip Hero
    (E) Configure Equipment Pool
        (S) Player --> Acquire Equipment Advantage Ranks
        (S) System --> Derive Equipment Point Budget from Advantage Ranks
        (S) Player --> Pay Equipment Points for Item
        (S) System --> Enforce Equipment Point Budget Limit
        (S) System --> Enforce Equipment Bonus Non-stacking
        (S) Player --> Build Alternate Equipment Array
        (S) System --> Restrict Alternate Equipment to One Active Item
        (S) Player --> Access On-Hand Item with Hero Point
        (S) Player --> Pool Equipment Points with Team Members
    (E) Acquire Weapons
        (E) Select Melee Weapon
            (S) Player --> Select Simple Melee Weapon
            (S) Player --> Select Archaic Melee Weapon
            (S) Player --> Select Exotic Melee Weapon
            (S) Player --> Extend Weapon Critical Threat Range
            (S) System --> Add Wielder Strength to Melee Damage
            (S) System --> Break Weapon on Strength Excess
        (E) Select Ranged Weapon
            (S) Player --> Select Projectile Weapon
            (S) Player --> Select Energy Weapon
            (S) Player --> Select Heavy Weapon
            (S) Player --> Select Thrown Weapon
            (S) Player --> Add Weapon Accessory
        (E) Use Area Weapons
            (S) Player --> Select Grenade Type
            (S) System --> Apply Grenade Burst Area Effect
            (S) System --> Apply Grenade Cloud Area Effect
            (S) Player --> Place Explosive Device
            (S) System --> Apply Explosive Burst Area Damage
            (S) System --> Scale Explosive Damage by Quantity
    (E) Acquire Defensive Gear
        (S) Player --> Select Archaic Armor Type
        (S) Player --> Select Modern Armor Type
        (S) System --> Restrict Modern Armor Bonus to Ballistic
        (S) Player --> Select Shield Type
        (S) System --> Apply Active Defense Bonus from Shield
        (S) System --> Enforce Armor Bonus Non-stacking Rule
        (S) System --> Cap Equipment Toughness at Power Level
    (E) Acquire General Gear
        (S) Player --> Purchase Communications Device
        (S) Player --> Purchase Surveillance Equipment
        (S) Player --> Purchase Transportation Device
        (S) Player --> Purchase Professional Tools
        (S) Player --> Build Utility Belt Array
    (E) Build Device
        (E) Define Device Type
            (S) Player --> Designate Power as Removable Device
            (S) Player --> Designate Power as Easily Removable Device
            (S) Player --> Mark Device as Indestructible
            (S) System --> Calculate Reduced Cost from Removable Flaw
            (S) System --> Calculate Reduced Cost from Easily Removable Flaw
            (S) System --> Adjust Cost for Indestructible Modifier
        (E) Build Specialized Device
            (S) Player --> Build Battlesuit Power Armor Device
            (S) Player --> Assign Battlesuit Protection Powers
            (S) Player --> Assign Battlesuit Attack Powers
            (S) Player --> Assign Battlesuit Movement Powers
            (S) Player --> Assign Battlesuit Sensor Powers
            (S) Player --> Build Costume Device
            (S) Player --> Build Enhanced Equipment Device
        (E) Use Device in Play
            (S) Player --> Use Device Temporarily Without Power Points
            (S) GM --> Require Hero Point to Borrow Another Hero's Device
            (S) System --> Remove Powers When Device Taken Away
            (S) System --> Allow Replacement of Permanently Lost Device
    (E) Invent Temporary Device
        (E) Design Invention
            (S) Player --> Define Invention Effect and Point Cost
            (S) GM --> Make Design Check in Secret
            (S) System --> Set Design Check DC from Invention Cost
            (S) System --> Flag Design as Flawed at 3 Degrees Failure
            (S) Player --> Reduce Design Time with Check Penalty
        (E) Construct Invention
            (S) Player --> Complete Construction Check
            (S) System --> Set Construction Check DC from Invention Cost
            (S) System --> Calculate Construction Time from Invention Cost
            (S) Player --> Reduce Construction Time with Check Penalty
        (E) Use Invention
            (S) Player --> Use Invention for One Scene
            (S) Player --> Reuse Invention with Hero Point
            (S) Player --> Make Invention Permanent with Power Points
        (E) Emergency Inventing
            (S) Player --> Jury-Rig Device by Spending Hero Point
            (S) System --> Skip Design Phase for Jury-Rigged Device
            (S) System --> Apply Construction DC Penalty for Jury-Rig
            (S) System --> Compress Construction to Rounds for Jury-Rig
            (S) Player --> Perform Magical Ritual
            (S) Player --> Jury-Rig Magical Ritual
    (E) Design Vehicle
        (E) Configure Vehicle Traits
            (S) Player --> Select Vehicle Size Category
            (S) System --> Derive Base Vehicle Traits from Size
            (S) System --> Apply Defense Penalty for Large Vehicle
            (S) Player --> Set Vehicle Strength Above Size Default
            (S) Player --> Select Vehicle Speed Effect
            (S) Player --> Set Vehicle Toughness
            (S) Player --> Buy Off Vehicle Defense Penalty
        (E) Add Vehicle Features and Powers
            (S) Player --> Add Standard Vehicle Feature
            (S) Player --> Add Vehicle Armor Power Effect
            (S) Player --> Add Vehicle Cloaking Device Feature
            (S) Player --> Add Vehicle Weapon Effect
            (S) Player --> Add Vehicle Smokescreen Feature
            (S) System --> Calculate Vehicle Power Effect at One-Fifth Cost
        (E) Manage Vehicle Ownership
            (S) Player --> Pool Equipment Points for Team Vehicle
            (S) Player --> Set Up Alternate Vehicles Array
            (S) Player --> Access Non-Primary Vehicle with Hero Point
    (E) Design Headquarters
        (E) Configure Headquarters Structure
            (S) Player --> Select Headquarters Size Category
            (S) System --> Derive Base Toughness from Size
            (S) Player --> Set Headquarters Toughness Above Default
        (E) Add Headquarters Features
            (S) Player --> Add Communications Feature
            (S) Player --> Add Defense System Feature
            (S) Player --> Add Security System Feature
            (S) Player --> Add Holding Cells Feature
            (S) Player --> Add Workshop or Laboratory Feature
            (S) Player --> Add Living Space Feature
            (S) Player --> Add Power System Feature
            (S) Player --> Add Self-Repairing Feature
            (S) System --> Cap Feature Power Effect at Twice HQ Power Level
            (S) System --> Set Defense System Attack Bonus to HQ Power Level
        (E) Manage Headquarters Ownership
            (S) Player --> Pool Equipment Points for Team Headquarters
            (S) Player --> Set Up Alternate Headquarters Array
            (S) System --> Allow Rebuild of Destroyed Headquarters
    (E) Build Construct
        (E) Create Construct Character
            (S) Player --> Acquire Minion Advantage for Construct
            (S) Player --> Choose Construct Ability Profile
            (S) System --> Set Construct Stamina to None
            (S) System --> Grant Construct Immunity to Fortitude Effects
            (S) Player --> Assign Construct Powers Skills and Advantages
            (S) System --> Verify Zero Net Cost for Standard Construct Traits
        (E) Operate Construct
            (S) Player --> Issue Order to Construct on Move Action
            (S) System --> Execute Last Order When No New Command Given
            (S) Player --> Repair Damaged Construct with Technology Check
            (S) System --> Block Construct Recovery Without Repair

---

## Consolidation Notes (for AC phase)

### Configure Equipment Pool — Equipment Bonus Non-stacking
Groups the non-stacking rule across all equipment categories (weapons, armor, shields). The rule applies to the same mechanic: only the highest bonus of the same type applies. AC must specify:
- armor bonus capped at highest: wearing two armors gives only the benefit of the better one
- bonus types that do stack (Protection from a device is not equipment bonus — it stacks)
- equipment bonus vs. power bonus vs. circumstance bonus distinction

### Acquire Weapons — Area Weapons
Grenades and explosives share the Burst/Cloud Area mechanic with a Dodge DC. AC must specify:
- Burst Area: all in range affected, DC 15 resistance check for half
- Cloud Area: lingering, maintains each round
- Grenade vs. explosive: thrown vs. placed/delivered

### Select Exotic Melee Weapon
Each exotic weapon type has a unique mechanic beyond Strength-based Damage:
- Chain and whip: Reach + Improved Grab + Improved Trip
- Chainsaw: non-Strength-based Damage (fixed damage rank)
- Nunchaku: standard but with specific handling
- Whip: Reach 3 + Improved Grab + Improved Trip (longer reach than chain)
AC for exotic weapons must specify the unique mechanical property, not just the damage.

### Build Device — Cost Calculations
Removable vs Easily Removable and Indestructible interact on the same device. AC must specify:
- Removable flaw: -1 cost per rank (minimum cost applies)
- Easily Removable flaw: greater reduction (per Powers chapter formula)
- Indestructible: reverses some of the flaw cost reduction
- Combined: Removable + Indestructible is a specific cost point

### Invent Temporary Device — Time Reduction Trade-off
Reducing design or construction time applies a -5 check penalty per time rank reduced. This same mechanic applies to both normal inventing and ritual performance. AC must specify:
- Time rank table reference for design (hour → 1 hr/pp) and construction (4 hr/pp)
- Jury-rigging bypasses this trade-off entirely (different sub-epic, same hero point currency)

### Design Vehicle — Shared Feature Pattern with Headquarters
Vehicle features and HQ features both: cost 1 point each, have power effects charged at 1/5 normal. AC for each must confirm the one-fifth cost applies to vehicle/HQ power effects but not to normal equipment items.

### Build Construct — Zero Net Cost Invariant
The construct traits package (-30 pp from absent abilities + 30 pp Immunity to Fortitude) is neutral. AC must verify the net cost calculation is enforced and that constructs cannot selectively drop only some of the abilities (it is always one pair or the other).

---

## Context Gaps

- Construct size variation: the source says constructs larger/smaller than Medium pay power points for Innate/Permanent Growth or Shrinking, but does not specify when/how the GM adjudicates this in the application — flagged for GM-tools phase.
- Alternate Equipment hero-point stunt: the GM rules whether having an item "on-hand" is possible. The decision criteria are unspecified in source — AC should note this is GM discretion, not a system-enforced rule.
- Vehicle multi-mode movement: the source states Alternate Effects for multiple movement modes but does not specify how the application handles mode switching in play — may require combat sub-system integration.
- Ritual mishap details: 3+ degrees of failure on a ritual research check "may result in a mishap" but no mishap table or severity rules are given in the equipment chapter (cross-reference to GM section needed).
- Team equipment point pooling enforcement: the source says teams may divide cost "however they wish, usually as evenly as possible" — no system enforcement described; AC must treat this as player/GM agreement, not enforced limit.
