# Story Map — MM3E Online Holistic

Consolidated Pass 2 — breadth-pass backbone merged with all 7 module story maps.
Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).

---

(E) Resolve Checks
    (E) Make Check
        (S) Player --> Make Trait Check
        (S) System --> Grade Check Result by Degree
        (S) Player --> Make Opposed Check Against Opponent
        (S) System --> Resolve Comparison Check Without Roll
        (S) Player --> Make Resistance Check Against Effect
        (S) Player --> Perform Routine Check
        (S) Player --> Lead Team Check with Helpers
    (E) Apply Conditions
        (S) System --> Apply Condition to Character
        (S) System --> Supersede Condition in Chain
    (E) Recover from Conditions
        (S) Player --> Roll Resistance Check Against Ongoing Effect to Remove Conditions
        (S) System --> Remove Condition When Source Effect Ends
        (S) Player --> Roll Fortitude Check to Stabilize While Dying
        (S) Player --> Stabilize Dying Ally with Treatment Check

(E) Translate Rank to Measure
    (S) System --> Translate Trait Rank to Real-World Value
    (S) System --> Derive Measurement from Rank Formula

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

(E) Assign Abilities
    (E) Configure Ability Scores
        (S) Player --> Set Ability Rank
        (S) Player --> Designate Ability Rank Portion as Enhanced
        (S) System --> Cascade Trait Changes on Ability Rank Alteration
        (S) System --> Enforce Ability Rank Ceiling per Power Level
    (E) Configure Derived Defenses
        (S) System --> Derive Base Defense Rank from Ability
        (S) Player --> Increase Defense Rank Above Ability Base
        (S) System --> Enforce Toughness Increase Restriction
        (S) System --> Derive Initiative Modifier from Agility
    (E) Handle Absent Ability
        (S) System --> Apply Absent Ability Capability Restrictions
        (S) System --> Grant Bonus Power Points for Absent Ability
        (S) GM --> Authorize Hero to Have Absent Ability
    (E) Handle Debilitated Ability
        (S) System --> Apply Debilitated Ability Condition Effects
        (S) System --> Prevent Further Rank Reduction When Debilitated
        (S) System --> Clear Debilitated State When Ability Rank Recovers

(E) Manage Skills
    (E) Configure Skill Ranks
        (S) Player --> Assign Skill Ranks
        (S) System --> Enforce Skill Modifier Limit
    (E) Resolve Skill Checks
        (S) Player --> Make Skill Check
        (S) System --> Apply Critical Success on Natural 20
        (S) System --> Resolve Untrained Skill Attempt
        (S) System --> Apply Skill Mastery Routine Result
        (S) System --> Apply Circumstance Modifier to Skill Check
    (E) Use Interaction Skills
        (S) System --> Enforce Interaction Skill Requirements
        (S) Player --> Bluff Target with Deception
        (S) Player --> Create Disguise with Deception
        (S) Player --> Feint Opponent with Deception
        (S) Player --> Send Innuendo Message with Deception
        (S) Player --> Trick Target into Danger with Deception
        (S) Player --> Coerce Target with Intimidation
        (S) Player --> Demoralize Opponent with Intimidation
        (S) Player --> Intimidate Group of Minions
        (S) Player --> Improve NPC Attitude with Persuasion
        (S) Player --> Conduct Opposed Negotiation with Persuasion
        (S) Player --> Resist Interaction Skill with Insight
        (S) GM --> Detect Illusion Secretly with Insight
        (S) Player --> Detect Outside Influence with Insight
        (S) Player --> Evaluate Trustworthiness with Insight
    (E) Use Physical Skills
        (S) Player --> Balance on Precarious Surface
        (S) Player --> Perform Acrobatic Maneuver
        (S) Player --> Rise from Prone as Free Action
        (S) Player --> Reduce Fall Damage with Tumbling
        (S) Player --> Climb Surface with Athletics
        (S) Player --> Jump with Athletics
        (S) Player --> Sprint to Increase Speed
        (S) Player --> Swim with Athletics
        (S) System --> Apply Fall Damage to Character
        (S) Player --> Hide from Observer with Stealth
        (S) Player --> Tail Subject Undetected with Stealth
    (E) Use Combat Skills
        (S) Player --> Add Close Combat Rank to Attack Check
        (S) Player --> Add Ranged Combat Rank to Attack Check
    (E) Use Manipulation Skills
        (S) Player --> Conceal Object on Person with Sleight of Hand
        (S) Player --> Escape Restraints with Sleight of Hand
        (S) Player --> Perform Legerdemain with Sleight of Hand
        (S) Player --> Plant Object on Person with Sleight of Hand
        (S) Player --> Steal Object from Person with Sleight of Hand
        (S) Player --> Contort Through Tight Space with Sleight of Hand
        (S) Player --> Operate Unfamiliar Technological Device
        (S) Player --> Build Technological Item
        (S) Player --> Repair Damaged Technological Item
        (S) Player --> Perform Jury-Rig Repair
        (S) Player --> Place Demolitions Charge with Technology
        (S) Player --> Defeat Security Device with Technology
        (S) Player --> Diagnose Injuries and Ailments
        (S) Player --> Provide Long-Term Patient Care
        (S) Player --> Revive Dazed or Stunned Character
        (S) Player --> Stabilize Dying Character with Treatment
        (S) Player --> Treat Disease or Poison
        (S) Player --> Operate Vehicle Under Stress
    (E) Use Knowledge and Awareness Skills
        (S) Player --> Apply Professional Expertise
        (S) GM --> Resolve Expert Knowledge Check Secretly
        (S) Player --> Search Area for Clues with Investigation
        (S) Player --> Collect Physical Evidence with Investigation
        (S) Player --> Analyze Collected Evidence
        (S) Player --> Gather Information through Contacts
        (S) Player --> Conduct Surveillance on Subject
        (S) GM --> Make Secret Perception Check for Character
        (S) Player --> Detect Disguise with Perception
        (S) Player --> Notice Concealed Object with Perception

(E) Select Advantages
    (E) Acquire Advantage
        (S) Player --> Purchase Advantage Rank
        (S) System --> Validate Power Point Cost for Advantage
        (S) System --> Enforce Power Level Cap on Attack Advantage Bonus
        (S) System --> Cap Luck Maximum Rank at Half Power Level
    (E) Apply Combat Advantage
        (E) Execute Attack Trade-Off Maneuver
            (S) Player --> Execute Attack Trade-Off Maneuver (accurate, all-out, defensive, power)
            (S) System --> Adjust Attack and Defense Values by Trade-Off Amount
        (E) Apply Passive Combat Bonus
            (S) System --> Apply Ranked Attack Bonus to Close or Ranged Attack Check
            (S) System --> Apply Initiative Bonus from Improved Initiative
            (S) System --> Apply Extended Critical Threat Range via Improved Critical
        (E) Apply Situational Combat Bonus
            (S) Player --> Declare Favored Environment Bonus Allocation
            (S) System --> Apply Favored Environment Circumstance Bonus
    (E) Activate Fortune Advantage
        (S) Player --> Re-Roll Die Using Luck Rank
        (S) System --> Enforce Luck Session-Use Limit and Refresh at Adventure Start
        (S) Player --> Inspire Allies with Hero Point
        (S) System --> Apply Inspiration Bonus Ignoring Power Level Cap
        (S) Player --> Remove Ally Condition via Leadership
        (S) Player --> Gain Temporary Skill Ranks via Beginner's Luck
    (E) Use Skill Advantage
        (S) Player --> Use Any Skill Untrained via Jack of All Trades
        (S) Player --> Make Routine Skill Check Under Pressure via Skill Mastery
        (S) System --> Apply Favored Foe Circumstance Bonus to Qualifying Checks
    (E) Manage Character Resources
        (E) Configure Equipment
            (S) Player --> Allocate Equipment Points to Gear
            (S) System --> Enforce Equipment Point Budget from Rank
        (E) Manage Minion
            (S) Player --> Configure Minion Traits Within Power Point Budget
            (S) System --> Enforce Minion Power Level Limits
            (S) System --> Replace Lost Minion Between Adventures
            (S) Player --> Spend Power Points to Improve Minion Rank
        (E) Manage Sidekick
            (S) Player --> Configure Sidekick Traits Within Power Point Budget
            (S) System --> Enforce Sidekick Power Point Total Below Owner Total
            (S) Player --> Spend Hero Point on Sidekick's Behalf
            (S) Player --> Spend Power Points to Improve Sidekick Rank
        (E) Establish Benefit
            (S) Player --> Propose Benefit to GM
            (S) GM --> Approve or Reject Benefit Definition
    (E) Maintain Advantage State
        (S) System --> Persist Advantage Selections on Character Sheet
        (S) System --> Track Luck Rank Uses per Session
        (S) System --> Refresh Luck Ranks at Start of Adventure

(E) Configure Powers
    (E) Configure Attack Effect
        (S) Player --> Select Affliction Effect and Configure Condition Set
        (S) Player --> Select Damage Effect for Close Combat
        (S) Player --> Select Blast Effect for Ranged Energy Attack
        (S) Player --> Select Deflect Effect for Ranged Protection
        (S) Player --> Select Nullify Effect and Define Target Descriptor
        (S) Player --> Select Weaken Effect and Define Target Trait
        (S) System --> Resolve Affliction Resistance Check and Apply Condition Degree
        (S) System --> Recover from Affliction Condition at End of Turn
        (S) System --> Resolve Damage Resistance Check and Apply Damage Condition
        (S) System --> Resolve Weaken Resistance Check and Reduce Target Trait
        (S) System --> Recover Weakened Trait at One Point per Round
        (S) System --> Resolve Nullify Opposed Check Against Target Effect Rank
    (E) Configure Defense Effect
        (S) Player --> Select Protection Effect for Toughness Bonus
        (S) Player --> Select Immunity Effect and Define Covered Effect Set
        (S) Player --> Configure Partial Immunity for Half-Effect Protection
        (S) Player --> Select Regeneration Effect for Progressive Damage Recovery
        (S) Player --> Select Immortality Effect for Death Recovery
        (S) System --> Apply Immunity Check Against Matching Power Descriptor
        (S) System --> Remove Toughness Penalty via Regeneration Recovery Phase
        (S) System --> Remove Damage Condition via Regeneration Condition Phase
        (S) System --> Recover from Death via Immortality After Time Elapses
    (E) Configure Mobility Effect
        (S) Player --> Select Flight Effect for Aerial Movement
        (S) Player --> Select Speed Effect for Ground Velocity Enhancement
        (S) Player --> Select Burrowing Effect for Underground Movement
        (S) Player --> Select Swimming Effect for Aquatic Movement
        (S) Player --> Select Leaping Effect for Extended Jumping
        (S) Player --> Select Teleport Effect for Instantaneous Relocation
        (S) Player --> Select Movement Effect and Choose Special Movement Mode
        (S) System --> Calculate Flight Speed Rank from Effect Rank
        (S) System --> Calculate Burrowing Speed Rank with Terrain Penalty
        (S) System --> Calculate Jump Distance Rank from Leaping Rank
        (S) System --> Validate Teleport Destination as Known or Accurately Sensed
    (E) Configure Sensory Effect
        (S) Player --> Select Senses Effect and Allocate Sense Enhancements
        (S) Player --> Select Concealment Effect and Choose Hidden Sense Type
        (S) Player --> Select Remote Sensing Effect for Displaced Perception
        (S) Player --> Select Mind Reading Effect for Mental Contact
        (S) Player --> Select Communication Effect and Choose Sense Type Medium
        (S) Player --> Select Comprehend Effect and Choose Communication Type
        (S) System --> Grant Total Concealment Against Chosen Sense Type
        (S) System --> Suppress Normal Senses During Remote Sensing
        (S) System --> Mark Character as Vulnerable During Remote Sensing
        (S) System --> Resolve Mind Reading Opposed Check Against Will Defense
        (S) System --> Break Mind Reading Contact on Target Will Check Success
    (E) Configure Control Effect
        (S) Player --> Select Create Effect and Set Volume Parameters
        (S) Player --> Select Move Object Effect for Telekinetic Manipulation
        (S) Player --> Select Environment Effect and Choose Environmental Changes
        (S) Player --> Select Illusion Effect and Choose Sense Type Coverage
        (S) Player --> Select Luck Control Effect and Define Hero Point Capability
        (S) Player --> Select Summon Effect and Define Minion Parameters
        (S) Player --> Select Transform Effect and Set Transformation Scope
        (S) System --> Enforce Created Object Volume and Toughness from Effect Rank
        (S) System --> Dissolve Created Object When Effect is Not Maintained
        (S) System --> Resolve Move Object Strength Check for Resisting Targets
        (S) System --> Resolve Insight Check to Detect Illusion
        (S) System --> Apply Summon Dazed Condition on Minion Arrival
        (S) System --> Dismiss Summon When Minion is Incapacitated
        (S) System --> Resolve Transform Fortitude Resistance for Living Targets
        (S) System --> Revert Transformation When Sustained Effect Ends
    (E) Configure General Effect
        (S) Player --> Select Variable Effect and Define Effect Type Pool
        (S) Player --> Select Growth Effect for Physical Size Increase
        (S) Player --> Select Shrinking Effect for Physical Size Reduction
        (S) Player --> Select Insubstantial Effect and Choose Physical Form
        (S) Player --> Select Enhanced Trait Effect and Choose Target Trait
        (S) Player --> Select Healing Effect for Damage Condition Removal
        (S) Player --> Select Elongation Effect for Extended Reach
        (S) Player --> Select Quickness Effect for Task Time Reduction
        (S) Player --> Select Feature Effect and Define Minor Game Capability
        (S) System --> Apply Growth Ability and Size Bonuses and Penalties per Rank
        (S) System --> Apply Shrinking Defense and Stealth Bonuses and Penalties per Rank
        (S) System --> Enforce Variable Pool Size as Rank Times Five Points
        (S) System --> Enforce PL Limits on Variable-Built Effects
        (S) System --> Apply Healing Check and Remove Damage Condition from Most Severe
        (S) System --> Block Healing Reuse on Same Target Within Scene
    (E) Apply Per-Rank Modifiers
        (S) System --> Set Default Action, Range, Duration for Effect Type
        (S) System --> Calculate Base Cost per Rank from Effect Definition
        (S) Player --> Apply Per-Rank Extra to Raise Cost per Rank
        (S) Player --> Apply Per-Rank Flaw to Lower Cost per Rank
        (S) System --> Enforce Minimum One Point per Rank Floor After Flaws
        (S) Player --> Apply Area Extra to Replace Attack Check with Dodge Save
        (S) System --> Apply Area Dodge Save DC as Ten Plus Effect Rank
        (S) System --> Reduce Area Effect to Half Rank on Dodge Save Success
        (S) Player --> Apply Multiattack Extra for Multiple Target Coverage
        (S) System --> Apply Multiattack Bonus DC on Multiple Success Degrees
    (E) Apply Flat Modifiers
        (S) Player --> Apply Accurate Extra for Attack Check Bonus
        (S) Player --> Apply Penetrating Extra to Overcome Impervious Defense
        (S) Player --> Apply Activation Flaw to Require Power Preparation
        (S) Player --> Apply Check Required Flaw to Gate Effect on Skill Check
        (S) Player --> Apply Limited Flaw to Restrict Effect Circumstances
        (S) Player --> Apply Removable Flaw to Convert Power to Device
        (S) System --> Calculate Final Power Cost with Flat Modifier Adjustments
        (S) System --> Enforce Minimum One Point Total Power Cost After Flat Flaws
        (S) System --> Apply Penetrating Rank Against Impervious Toughness Threshold
        (S) System --> Require Activation Action Before Power Effects Become Available
        (S) System --> Gate Effect Activation on Check Required Skill Check Success
        (S) System --> Allow Removal of Device When Character is Stunned and Defenseless
    (E) Assign Power Descriptors
        (S) Player --> Assign Origin Descriptor to Power Set
        (S) Player --> Assign Source Descriptor to Power Effect
        (S) Player --> Assign Result Descriptor to Power Effect
        (S) System --> Match Power Descriptor Against Immunity Effect Coverage
        (S) System --> Match Power Descriptor Against Nullify Effect Target
        (S) GM --> Approve Descriptor Interaction Between Powers
    (E) Organize Power Arrays
        (S) Player --> Build Power Array with Base Effect
        (S) Player --> Add Alternate Effect to Array within Primary Effect Cost Limit
        (S) Player --> Add Dynamic Alternate Effect for Simultaneous Use
        (S) Player --> Switch Active Effect in Array as Free Action
        (S) System --> Enforce Array Mutual Exclusivity Rule for Non-Dynamic Effects
        (S) System --> Propagate Array Disable Equally to All Alternate Effects
        (S) System --> Reallocate Power Points Among Dynamic Array Effects per Turn
        (S) System --> Enforce Dynamic Effect Point Total Against Array Pool Size

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

(E) Conduct Combat
    (E) Manage Turn Order
        (S) System --> Roll Initiative Check
        (S) System --> Determine Turn Order from Initiative Results
        (S) System --> Break Initiative Ties by Dodge then Agility
        (S) GM --> Roll Single Initiative for Minion Group
        (S) Player --> Enter Conflict Mid-Round
        (S) Player --> Delay Turn to Later Initiative Position
        (S) Player --> Ready Action for Trigger Condition
        (S) Player --> Take Readied Action as Reaction
    (E) Manage Action Economy
        (S) Player --> Take Standard Action on Turn
        (S) Player --> Take Move Action on Turn
        (S) Player --> Exchange Standard Action for Additional Move Action
        (S) Player --> Take Free Action During Turn
        (S) Player --> Take Reaction Outside Turn
    (E) Execute Attacks
        (S) Player --> Make Close Attack Check Against Parry
        (S) Player --> Make Ranged Attack Check Against Dodge
        (S) System --> Apply Ranged Attack Distance Penalty
        (S) System --> Resolve Attack Check Against Defense Class
        (S) System --> Register Natural 1 as Automatic Miss
        (S) System --> Detect Natural 20 as Potential Critical Hit
        (S) System --> Determine Critical Hit When Total Meets Defense
        (S) Player --> Apply Critical Hit Effect Choice
        (S) System --> Bypass Attack Check for Area or Perception Effect
    (E) Apply Aim and Charge
        (S) Player --> Aim for Attack Bonus
        (S) System --> Apply Vulnerable Condition During Aim
        (S) Player --> Execute Charge Attack with Penalty
        (S) Player --> Execute Slam Attack During Charge
        (S) System --> Apply Attacker Toughness Check from Slam
    (E) Perform Combat Maneuvers
        (S) Player --> Defend Against Incoming Attacks
        (S) Player --> Execute Grab Attempt
        (S) System --> Resolve Grab Resistance Check
        (S) Player --> Maintain Grab Hold as Free Action
        (S) Player --> Damage Grabbed Target on Subsequent Turn
        (S) Player --> Drag Restrained or Bound Target
        (S) Player --> Escape from Grab
        (S) Player --> Execute Disarm Attempt
        (S) System --> Resolve Disarm Opposed Check
        (S) Player --> Counter-Disarm as Reaction
        (S) Player --> Execute Trip Attempt
        (S) System --> Resolve Trip Opposed Check
        (S) Player --> Counter-Trip as Reaction
        (S) Player --> Execute Feint with Deception Check
    (E) Resolve Damage and Recovery
        (S) System --> Resolve Toughness Resistance Check Against Damage
        (S) System --> Apply Cumulative Toughness Penalty
        (S) System --> Apply Damage Condition by Degree of Failure
        (S) System --> Transition Incapacitated Target to Dying
        (S) System --> Apply Minion Defeat Rule on Any Resistance Failure
        (S) Player --> Recover from Damage in Conflict
        (S) System --> Remove Damage Condition After Rest
        (S) System --> Resolve Ongoing Effect Resistance Check at End of Turn
    (E) Handle Tactical Environment
        (S) System --> Apply Concealment Penalty to Attack Check
        (S) System --> Apply Cover Penalty to Attack Check
        (S) System --> Apply Cover Bonus Against Area Effect
        (S) GM --> Apply Surprise Round Rules
        (S) System --> Apply Vulnerable to Surprised Characters
        (S) Player --> Execute Team Attack with Coordinated Attackers
        (S) System --> Resolve Team Attack Bonus from Combined Hits
    (E) Handle Hazards and Objects
        (S) System --> Apply Falling Damage by Distance Rank
        (S) Player --> Catch Falling Target with Dexterity Check
        (S) System --> Apply Suffocation Sequence
        (S) System --> Apply Environmental Hazard Check
        (S) Player --> Attack or Smash Object
        (S) System --> Resolve Object Toughness Check and Break Result
        (S) System --> Apply Material Toughness Rating to Object
    (E) Use Hero Resources
        (S) Player --> Spend Hero Point to Re-Roll Die
        (S) Player --> Spend Hero Point to Recover Condition Immediately
        (S) Player --> Spend Hero Point for Heroic Feat Advantage
        (S) Player --> Spend Hero Point to Edit Scene Detail
        (S) Player --> Spend Hero Point for Instant Counter
        (S) Player --> Declare Extra Effort for Combat Benefit
        (S) Player --> Activate Power Stunt via Extra Effort
        (S) Player --> Spend Hero Point to Remove Extra Effort Fatigue
        (S) System --> Apply Extra Effort Fatigue at Start of Next Turn

## Consolidation Notes (for AC phase)

### Resolve Checks

#### Apply Condition to Character (basic: dazed, stunned, vulnerable, defenseless, impaired, disabled, weakened, hindered, immobile, compelled, controlled, debilitated, fatigued, transformed, unaware, normal; combined: staggered, incapacitated, dying, exhausted, asleep, blind, bound, deaf, entranced, paralyzed, prone, restrained, surprised)
Groups 16 basic and 13 combined conditions into one parameterized story — all follow the same "apply condition modifiers to character" pattern. Basic conditions impose a single modifier; combined conditions bundle multiple basic conditions under one name (constituents can be superseded or resolved independently of each other while the combined condition persists).
AC must specify per basic condition:
- dazed: limit to free actions + one standard action; superseded by stunned
- stunned: no actions including free actions
- vulnerable: halve active defenses; superseded by defenseless
- defenseless: active defense bonuses become 0; attackers may use routine checks; forgoing routine makes any hit critical
- impaired: −2 circumstance penalty on checks; superseded by disabled
- disabled: −5 circumstance penalty on checks; superseded by debilitated
- weakened: temporary power point loss in a trait; superseded by debilitated
- hindered: half speed (−1 speed rank); superseded by immobile
- immobile: no movement speed
- compelled: free + one standard per turn, both chosen by controller; superseded by controlled
- controlled: all actions dictated by another character
- fatigued: hindered; recovers after one hour rest
- transformed: traits altered by outside agency; power points cannot increase
- unaware: cannot make interaction or Perception checks

AC must specify per combined condition:
- staggered: dazed + hindered
- incapacitated: defenseless + stunned + unaware; generally fall prone
- dying: incapacitated + near death; Fortitude DC 15 each round; two degrees of success stabilizes; three total degrees of failure = death
- exhausted: impaired + hindered; recovers after one hour rest
- asleep: defenseless + stunned + unaware; hearing check (3+ degrees) or shaking wakes
- blind: hindered + visually unaware + vulnerable; may also be impaired or disabled for vision-dependent activities
- bound: defenseless + immobile + impaired
- deaf: auditory concealment from the character; may allow surprise attacks
- entranced: stunned; obvious threat breaks trance; ally can free with interaction check (DC 10 + effect rank)
- paralyzed: defenseless + immobile + physically stunned; aware; purely mental actions allowed
- prone: −5 close attack penalty; opponents +5 close / −5 ranged; hindered; standing is move action
- restrained: hindered + vulnerable; if anchored, immobile instead of hindered
- surprised: stunned + vulnerable

#### Supersede Condition in Chain
Five supersession chains; AC must specify behavior per chain:
- dazed → stunned
- impaired → disabled → debilitated
- vulnerable → defenseless
- hindered → immobile
- compelled → controlled
Recovery note: supersession overrides while the more severe condition is present; removing the more severe condition reveals the lesser if its source effect is still active.

#### Derive Measurement from Rank Formula (distance, time, throwing distance)
Groups three rank-derivation formulas into one parameterized story — all follow the same "perform rank arithmetic then look up result in measurement table" pattern.
AC must specify per variant:
- distance: add Time Rank + Speed Rank, look up result as distance value
- time: subtract Speed Rank from Distance Rank, look up result as time value
- throwing distance: subtract object Mass Rank from thrower's Strength Rank, look up result as distance value

#### Moved to other modules
- Hero point, extra effort, power stunt, reaction → Combat module (per module partitioning)

### Character Construction

#### Spend Power Points on X Ranks (Ability, Defense, Skill, Advantages, Powers)
Groups five distinct trait-category spend stories. Each uses the same "allocate PP at stated cost" pattern but has a different cost formula and different rules.
AC must specify per variant:
- Ability Ranks: 2 PP per ability rank; 8 ability scores (STR, STA, AGL, DEX, FGT, INT, AWE, PRE)
- Defense Ranks: 1 PP per rank above the base value provided by the related ability
- Skill Ranks: 1 PP per 2 total skill ranks (rounded down for odd totals)
- Advantages: 1 PP per advantage or per rank in a ranked advantage
- Powers: ((base effect cost + extras minus flaws) x rank) + flat modifiers; cost varies by chosen effect

#### Choose Complication
Consolidates enemy, identity, responsibility, relationship, secret, power loss, and any other non-Motivation, non-Weakness complication type. All share the construction-time pattern: Player chooses type, defines narrative detail, GM may overrule.
AC must specify per variant:
- Enemy: define adversary identity and nature of enmity (one-sided or mutual); GM introduces enemy in play when it causes specific harm to earn hero point
- Identity: choose public identity (reveal real name, live in public eye) or secret identity (maintain dual life, protect loved ones from knowledge); dual-identity heroes must track two personas
- Responsibility: define obligations (family, professional, civic) that compete with heroic duties; earning hero point requires responsibility to be visibly neglected or conflicted
- Relationship: define key people in hero's life (loved ones, mentors, rivals); if in the know about hero identity, they are danger targets; if not, hero must manage the dual life
- Secret: specify what is hidden and from whom (true identity, dark past, secret weakness); earning hero point requires active threat of exposure
- Power Loss: define triggering circumstances (specific substance, condition, location, or wavering motivation); earning hero point requires powers to actually fail due to trigger

#### Enforce Power Level Limits (Attack & Effect, Dodge & Toughness, Parry & Toughness, Fortitude & Will)
Groups four PL cap pairs that share the same rule shape: sum of both traits in pair must not exceed 2 x series power level. Each pair governs different traits.
AC must specify per pair:
- Attack & Effect: attack bonus + effect rank of that attack <= 2xPL; if effect allows resistance check but no attack check, effect rank alone <= PL
- Dodge & Toughness: Dodge + Toughness <= 2xPL; Dodge is active defense (purchased), Toughness is passive
- Parry & Toughness: Parry + Toughness <= 2xPL; Parry is close-combat active defense; Toughness shared with Dodge pair
- Fortitude & Will: Fortitude + Will <= 2xPL; both are resistance defenses, not active defenses

#### Raise Series Power Level
Consolidates the two outcomes of a PL increase: heroes gain cap headroom to spend PP on previously-maxed traits; GM reevaluates NPC challenge ratings.
AC must specify:
- Trigger: heroes have accumulated approximately 15 additional PP since series start or last PL increase
- Effect on heroes: PL raises by +1; heroes may now spend accumulated PP on traits that exceeded the old cap
- Effect on NPCs: GM reviews villain traits and may increase some to maintain challenge; no PP accounting required for NPCs

### Ability

#### Set Ability Rank
Groups buying-up and reducing-below-0 into one parameterized story. The 2 power point per rank formula applies in both directions. AC must specify per direction:
- Buying up (rank 0 → positive): spend 2 pp per +1 rank; each +1 raises ability from current value; cannot exceed power level cap.
- Reducing below 0 (rank 0 → negative): gain 2 pp per −1 rank; cannot go below −5 voluntarily.
- Applies to all eight named abilities (STR, STA, AGL, DEX, FGT, INT, AWE, PRE) with identical formula.

#### Apply Absent Ability Capability Restrictions
Groups per-ability absence effects into one parameterized story. All share "automatic fail on related checks" but have distinct capability losses per ability. AC must specify per ability:
- No Strength: cannot exert physical force; auto-fail Athletics, strength-based attack checks.
- No Stamina: no living-body mechanics; damage/recovery as inanimate object; immune to fatigue; no Fortitude defense.
- No Dexterity: cannot manipulate objects; no physical attacks; auto-fail Dexterity checks.
- No Agility: no self-propelled movement; no Dodge defense; auto-fail Agility checks.
- No Fighting: no close attacks; auto-fail close attack checks.
- No Intellect: automaton; immune to mental effects and interaction skills; no Will defense.
- No Awareness: completely unaware; also no Presence automatically; immune to mental effects; treated as inanimate object.
- No Presence: cannot interact; immune to interaction skills; no Will defense.

#### Apply Debilitated Ability Condition Effects
Groups four distinct condition sets by ability grouping into one parameterized story. Trigger is the same (rank drops below −5) but outcomes differ by ability. AC must specify per group:
- STR, AGL, or DEX: collapse — defenseless + immobilized + stunned (conscious and aware).
- STA: dying condition + additional −5 modifier on Fortitude checks to avoid death.
- FGT: dazed + defenseless; cannot make close attacks.
- INT, AWE, or PRE: unaware; persists until ability restored to at least −5.

#### Passive vs Active Runtime Analysis (Ability)
- Set Ability Rank → character creation / advancement time; no runtime story needed beyond cascade.
- Designate Ability Rank Portion as Enhanced → character creation time; runtime story is nullification (owned by Power module).
- Cascade Trait Changes → passive system behavior at the moment a rank changes; maps as a system story.
- Derive Base Defense Rank from Ability → passive derivation; automatic at character creation and on any rank change; mapped as system story.
- Apply Absent Ability Capability Restrictions → character design time; applied at creation; no separate runtime story for ongoing enforcement (the restrictions are always in effect).
- Apply Debilitated Ability Condition Effects → runtime (occurs when rank is reduced below −5 by a game effect); maps as system story.
- Clear Debilitated State When Ability Rank Recovers → runtime (recovery when rank returns to −5 or above); maps as system story.

### Skill

#### Assign Skill Ranks
Skill rank purchase follows a fixed 2-ranks-per-PP rate. Ranks may be split freely across any skills. The skill modifier limit (total skill modifier capped at PL + 10) is enforced at build time by Character Construction, not at check time — AC should cover the rank assignment mechanics only, not the limit calculation.

#### Enforce Skill Modifier Limit
This is a system enforcement at character construction/advancement time — total skill modifier (rank + ability + misc) may not exceed PL + 10 for any skill. The limit interacts with trade-offs in Character Construction; here it is simply the upper-bound check. AC must specify: what is the total modifier, what is the limit, and what happens if the limit is exceeded.

#### Make Skill Check
This is the core resolution story — parameterized across all 16 named skills. AC should cover: formula (d20 + rank + ability + circumstance), DC comparison, success/failure. The per-skill stories (Bluff, Climb, Hide, etc.) specify skill-specific DCs and outcomes. Do not duplicate the core formula in every per-skill story.

#### Apply Critical Success on Natural 20
Distinct from degree-of-success arithmetic: a natural 20 triggers a degree increase after normal calculation. AC must specify: when does a natural 20 apply (on any skill check), what happens to the degree, and what is the edge case (already at highest degree).

#### Resolve Untrained Skill Attempt
Two distinct behaviors: (1) skills without Trained Only marker — attempt proceeds with rank 0, ability modifier applies; (2) Trained Only skills — attempt automatically fails with no roll. AC must cover both paths.

#### Apply Skill Mastery Routine Result
Skill Mastery allows routine check result (bonus + 10) even under stress. AC must specify: which skill is nominated, what is the routine result, when does it apply (replaces a roll the character would otherwise be required to make).

#### Enforce Interaction Skill Requirements
Covers the three system-enforced gates before any interaction skill resolves: (1) subject awareness and comprehension (-5 if not met), (2) Intellect minimum (-5 for Int -5, blocked for subjects lacking mental abilities), (3) Immunity power effect (blocked entirely). These are pre-conditions shared by all three interaction skills; AC should use a parameterized structure.

#### Feint Opponent with Deception
Distinct from Bluffing — feinting is a combat action (standard action), makes the target vulnerable, and resolves in one round. Bluffing is a social action that changes NPC behavior persistently. AC must cover the vulnerability condition duration (until end of user's next round).

#### Intimidate Group of Minions
Distinct from single-target Coerce — uses a single check against a single GM-rolled group resistance; the effect must be identical for all members. AC must cover: same-effect requirement, single-resistance roll, minion definition.

#### Detect Illusion Secretly with Insight
GM makes this check on behalf of the character — the player does not decide when to attempt it. Distinct from Detect Outside Influence (which is player-initiated). AC must cover: secret roll, DC (10 + Illusion rank), outcome (success reveals illusion flaw).

#### Collect Physical Evidence vs. Analyze Collected Evidence
Two-step process: Gather Evidence (DC 15 check to collect without ruining it) must succeed before Analyze Evidence (DC 15 check to extract information). Failure to gather properly degrades analysis or makes it impossible. AC must cover both steps and their interaction.

#### Add Close Combat Rank to Attack Check / Add Ranged Combat Rank to Attack Check
Both follow the same narrow pattern: rank adds only to attack checks for the specific weapon/power named by the skill, not to any other attack, not to defense. These can be written with parallel AC structure. Distinguish from advantage-based bonuses (Close Attack, Ranged Attack) which apply more broadly.

#### Perform Jury-Rig Repair
Distinct from standard Repair: DC is 10 lower than building (not just 5 lower), takes a standard action (not hours), fixes only one problem, and lasts only until end of scene. Item cannot be jury-rigged again until fully repaired. AC must cover all four constraints.

#### Revive Dazed or Stunned Character
Distinct from Stabilize: removes dazed or stunned conditions (not dying), takes a standard action, leaves other conditions intact. Cannot awaken a dying character without stabilizing first. AC must cover the condition-specificity and the dying character limitation.

### Advantage

#### Execute Attack Trade-Off Maneuver (accurate, all-out, defensive, power)
Groups four attack modifier advantages into one parameterized story — all share the "declare penalty of up to −5 on one stat, add same value up to +5 to another stat" pattern, activated during the relevant maneuver type.
AC must specify per variant:
- Accurate Attack: penalty on effect modifier (−1 to −5), matching bonus to attack check bonus (up to +5); cannot exceed the penalty taken
- All-out Attack: penalty on active defenses — Dodge and Parry (−1 to −5), matching bonus to attack check bonus (up to +5)
- Defensive Attack: penalty on attack check bonus (−1 to −5), matching bonus to both active defenses — Dodge and Parry (up to +5)
- Power Attack: penalty on attack check bonus (−1 to −5), matching bonus to effect bonus of the attack (up to +5)
All variants: the penalty and bonus are equal in magnitude; neither can exceed 5; the pair is declared before the attack roll.

#### Apply Ranked Attack Bonus to Close or Ranged Attack Check (Close Attack, Ranged Attack)
Groups two ranked attack bonus advantages that share the same "+1 to attack checks per rank, capped by power level" pattern, differentiated only by attack type (close vs. ranged).
AC must specify per variant:
- Close Attack: applies to all close attack checks (armed and unarmed); total bonus still subject to power level cap
- Ranged Attack: applies to all ranged attack checks; total bonus still subject to power level cap
Both variants: the bonus is passive (always applies to the relevant attack type); separate from the Close Combat or Ranged Combat skill.

#### Passive vs Active Runtime Analysis (Combat Advantages)
- Accurate Attack → active (player declares maneuver per attack; needs an Execute story)
- All-out Attack → active (player declares per attack; same Execute story)
- Defensive Attack → active (player declares per attack; same Execute story)
- Power Attack → active (player declares per attack; same Execute story)
- Close Attack → passive (system applies flat bonus to every close attack; system story)
- Ranged Attack → passive (system applies flat bonus to every ranged attack; system story)
- Improved Initiative → passive (system applies bonus to every initiative roll; system story)
- Improved Critical → passive (system extends threat range on every attack; system story)
- Favored Environment → semi-active (player chooses allocation at start of each round; both a player declaration and a system application story)

#### Passive vs Active Runtime Analysis (Fortune Advantages)
- Luck → active (player declares re-roll on a specific roll, consumes one rank use)
- Inspire → active (player spends hero point + standard action; system applies to allies)
- Leadership → active (player spends hero point + standard action to remove condition from ally)
- Beginner's Luck → active (player spends hero point; system grants temp ranks)

#### Passive vs Active Runtime Analysis (Skill Advantages)
- Jack of all Trades → passive (system removes untrained restriction automatically when advantage is held)
- Skill Mastery → passive (system removes pressure restriction on routine checks for chosen skill)
- Favored Foe → passive (system applies +2 circumstance when qualifying checks against favored foe occur)

#### Passive vs Active Runtime Analysis (General Advantages — no runtime stories needed)
- Equipment → static (converts to equipment points; no runtime story beyond Equipment module)
- Minion → active during character management (configure, improve, replace); no in-combat advantage runtime story
- Sidekick → active during character management (configure, improve); hero-point proxy story captured
- Benefit → narrative (defined with GM; no runtime application story)

### Power

#### Configure Attack Effect
- **Select Affliction Effect and Configure Condition Set** / **Resolve Affliction Resistance Check and Apply Condition Degree** / **Recover from Affliction Condition at End of Turn**: These three stories form a natural cluster — acquisition, resolution, and recovery. AC must cover: condition set definition at acquisition (exactly 3 conditions in degree order), attack check prerequisite, resistance type choice (Fort vs Will), degree of failure mapping, end-of-turn recovery check, and third-degree special recovery rule (1 minute after effect ends).
- **Select Blast Effect** is mechanically identical to Damage + Ranged extra. AC must confirm the 2 pp/rank cost is already calculated (base 1 + Ranged 1) and that the attack check uses Ranged vs Dodge.
- **Resolve Nullify Opposed Check**: AC must specify both branches — success (effect countered, target can reactivate) and failure (effect continues). Also specify what "countered" means for sustained vs permanent effects.

#### Configure Defense Effect
- **Configure Partial Immunity**: Half-rank immunity costs half the full rank cost. AC must specify that partial immunity reduces the effect rank by half (round down) against the covered effect, not that it provides a bonus.
- **Recover from Death via Immortality**: AC must specify the time-rank formula (19 − Immortality rank) and the edge case at rank 20 (recover at start of each action round).

#### Configure Mobility Effect
- **Select Movement Effect and Choose Special Movement Mode**: Each mode (Dimension Travel, Wall-Crawling, etc.) has sub-rules. AC can parametrize by mode or write per-mode AC. Consolidation note: pass 2 groups all Movement modes under one story; AC phase should expand per mode if distinct behavior is needed.

#### Configure Control Effect
- **Select Create Effect** / **Enforce Created Object Volume and Toughness from Effect Rank** / **Dissolve Created Object**: AC must specify permanence option (spend PP equal to rank).
- **Select Summon Effect** / **Apply Summon Dazed Condition** / **Dismiss Summon**: AC must cover PP = rank × 15, PL ≤ rank, dazed on arrival, directing = move action, and disappearance on incapacitation.

#### Configure General Effect
- **Select Insubstantial Effect**: 4 ranks at 5 pp/rank each — AC must confirm cost per form rank and rules per form (especially rank 4 Incorporeal interaction with physical world).
- **Select Variable Effect**: AC must cover pool size = rank × 5, standard action to reallocate, PL limits on built effects, and pool reset when effect not maintained.

#### Apply Per-Rank Modifiers
- **Enforce Minimum One Point per Rank Floor**: Edge case when flaws reduce cost to fractional — at this point each extra flaw grants ranks at ratio (e.g., 1:2 = 1 pp per 2 ranks). AC must specify the fractional cost progression.

#### Assign Power Descriptors
- **Match Power Descriptor Against Immunity / Nullify**: AC must specify matching logic — descriptors are intentionally flexible (lightning matches electricity); GM is final arbitrator.

#### Organize Power Arrays
- **Add Alternate Effect within Primary Effect Cost Limit**: AC must confirm: (a) total cost including all extras and flaws on the alternate, not just rank × cost, must be ≤ primary; (b) permanent effects cannot be alternates.
- **Reallocate Power Points Among Dynamic Array Effects**: AC must confirm: reallocation once per turn as free action; points not allocated = inactive at that rank; combined allocation cannot exceed total pool.

### Equipment

#### Configure Equipment Pool — Equipment Bonus Non-stacking
Groups the non-stacking rule across all equipment categories (weapons, armor, shields). The rule applies to the same mechanic: only the highest bonus of the same type applies. AC must specify:
- armor bonus capped at highest: wearing two armors gives only the benefit of the better one
- bonus types that do stack (Protection from a device is not equipment bonus — it stacks)
- equipment bonus vs. power bonus vs. circumstance bonus distinction

#### Acquire Weapons — Area Weapons
Grenades and explosives share the Burst/Cloud Area mechanic with a Dodge DC. AC must specify:
- Burst Area: all in range affected, DC 15 resistance check for half
- Cloud Area: lingering, maintains each round
- Grenade vs. explosive: thrown vs. placed/delivered

#### Select Exotic Melee Weapon
Each exotic weapon type has a unique mechanic beyond Strength-based Damage:
- Chain and whip: Reach + Improved Grab + Improved Trip
- Chainsaw: non-Strength-based Damage (fixed damage rank)
- Nunchaku: standard but with specific handling
- Whip: Reach 3 + Improved Grab + Improved Trip (longer reach than chain)
AC for exotic weapons must specify the unique mechanical property, not just the damage.

#### Build Device — Cost Calculations
Removable vs Easily Removable and Indestructible interact on the same device. AC must specify:
- Removable flaw: -1 cost per rank (minimum cost applies)
- Easily Removable flaw: greater reduction (per Powers chapter formula)
- Indestructible: reverses some of the flaw cost reduction
- Combined: Removable + Indestructible is a specific cost point

#### Invent Temporary Device — Time Reduction Trade-off
Reducing design or construction time applies a -5 check penalty per time rank reduced. This same mechanic applies to both normal inventing and ritual performance. AC must specify:
- Time rank table reference for design (hour → 1 hr/pp) and construction (4 hr/pp)
- Jury-rigging bypasses this trade-off entirely (different sub-epic, same hero point currency)

#### Design Vehicle — Shared Feature Pattern with Headquarters
Vehicle features and HQ features both: cost 1 point each, have power effects charged at 1/5 normal. AC for each must confirm the one-fifth cost applies to vehicle/HQ power effects but not to normal equipment items.

#### Build Construct — Zero Net Cost Invariant
The construct traits package (-30 pp from absent abilities + 30 pp Immunity to Fortitude) is neutral. AC must verify the net cost calculation is enforced and that constructs cannot selectively drop only some of the abilities (it is always one pair or the other).

### Combat

#### Execute Attacks
`Make Close Attack Check Against Parry` and `Make Ranged Attack Check Against Dodge` share the same resolution formula (d20 + attack bonus vs. defense class) but differ in which defense is targeted and what range penalties apply. AC must specify both separately with range-penalty details for ranged and the parry-target rule for close.

`Detect Natural 20 as Potential Critical Hit` and `Determine Critical Hit When Total Meets Defense` are two distinct steps in the critical hit determination. AC must specify the two-step check: roll = 20 → automatic hit + threat check → total ≥ defense class → confirmed critical.

`Apply Critical Hit Effect Choice` covers three mutually exclusive options (Increased Effect, Added Effect, Alternate Effect). AC must specify each option separately including the minion bypass rule for Increased Effect and the no-fatigue rule for Alternate Effect.

`Bypass Attack Check for Area or Perception Effect` negates all attack-check modifiers (concealment, cover, maneuvers, aim bonus). AC must confirm that area and perception effects automatically hit and cannot crit or miss.

#### Perform Combat Maneuvers
`Execute Grab Attempt` and `Resolve Grab Resistance Check` are sequential — AC for the grab story must cover both the attack check and the resistance check against Strength or Dodge.

`Maintain Grab Hold as Free Action` and `Damage Grabbed Target on Subsequent Turn` are separate stories with separate AC: maintaining a hold (free action, attacker hindered+vulnerable) vs. choosing to deal damage (standard action, only after hold established on a prior turn).

`Escape from Grab` uses Athletics or Acrobatics vs. routine check result of opponent's Strength or grab rank — this is a move action, separate AC needed to distinguish from the grab's resistance check.

`Counter-Disarm as Reaction` and `Counter-Trip as Reaction` only trigger when specific conditions are met (melee disarm lost; trip check lost) — AC must specify the triggering precondition.

#### Resolve Damage and Recovery
`Apply Damage Condition by Degree of Failure` covers four degrees with different outcomes:
- 1 degree: −1 cumulative Toughness penalty (no condition change)
- 2 degrees: dazed + −1 penalty
- 3 degrees: staggered + −1 penalty (if already staggered → 4th degree)
- 4 degrees: incapacitated

`Recover from Damage in Conflict` (standard action, once per conflict) vs. `Remove Damage Condition After Rest` (automatic, 1 condition per minute) are distinct recovery paths. AC must specify once-per-conflict constraint and the +2 defense bonus granted by Recover action.

`Resolve Ongoing Effect Resistance Check at End of Turn` is automatic — no action required. AC must specify that success ends the effect and removes its conditions; failure leaves conditions in place.

#### Use Hero Resources
`Spend Hero Point to Re-Roll Die` has the special floor rule: re-roll of 1–10 adds 10, making the floor 11. AC must specify the must-spend-before-GM-announces constraint.

`Spend Hero Point for Heroic Feat Advantage` excludes fortune advantages and requires meeting prerequisites. AC must specify these constraints.

`Declare Extra Effort for Combat Benefit` covers eight benefit options — AC must specify each as a distinct variant with the once-per-turn constraint and the fatigue cost.

`Activate Power Stunt via Extra Effort` requires an existing power as the base; permanent effects excluded; lasts until end of scene. AC must specify the base-power requirement and scene-duration rule.

`Spend Hero Point to Remove Extra Effort Fatigue` must be spent at the START of the turn after extra effort — not immediately after. AC must specify the timing constraint.

## Context Gaps

### Resolve Checks
- No GM-facing campaign/adventure management context in source — scope is hero and rules mechanics only.
- Construct behavior at runtime (animated objects, robots acting independently) — source describes stats and commanding but runtime autonomy is unclear for an online tool.
- Condition-specific recovery triggers (entranced broken by obvious threat or ally interaction check DC 10 + effect rank; asleep broken by hearing Perception check 3+ degrees or shaking) — mapped as general recovery; AC phase must specify per-condition recovery paths.
- Condition enforcement across modules: conditions define game modifiers (action restrictions, check penalties, defense reductions) but enforcement lives in consuming modules (Combat for action limits, Check Resolution for check penalties). Cross-module wiring not yet mapped as stories.

### Character Construction
- Complication activation during play (GM introduces complication, player goes along, earns hero point) is a runtime behavior owned by the Check Resolution module — not represented in this construction map.
- Online tool persistence and versioning of hero sheets is outside the source scope; no stories mapped.
- Team/party construction coordination (ensuring heroes complement each other) is addressed informally in source ("consult fellow players") with no formal construction steps — not mapped.
- Quickstart Character Generator (page 54 reference) is mentioned in source as an alternative to full hero design; scope and mechanic not described in available chunks — flagged as context gap.

### Ability
- **GM authorization workflow for absent abilities**: Source requires GM permission for heroes to lack an ability but does not specify whether an online tool prompts for approval, logs a flag, or blocks the action outright — UX and workflow decision needed.
- **Enhanced ability nullification interaction**: When an enhanced ability rank is nullified, the base (natural) portion of the rank should remain — the exact system behavior for partial nullification (which portion is reduced and in what order) requires clarification from the Power module.
- **Debilitation recovery source**: The specific game effect (power, healing, time) that restores a debilitated ability rank is owned by the module that caused the debilitation — the Ability module detects when rank recovers to ≥ −5 and clears the debilitated state, but does not itself initiate the recovery.
- **Defense class display vs. calculation separation**: Whether the online tool derives and displays defense class (Dodge + 10 etc.) as a separate computed field on the character sheet, or only exposes raw defense ranks, is a UI/product decision.

### Skill
- **Skill Mastery full definition**: The Skill Mastery advantage definition lives in the Advantages chapter, not Chapter 4. Source chunks confirm it allows routine check results even under stress but do not specify all edge cases (e.g., when exactly a roll is "required" vs. voluntary).
- **Technology Inventing**: The Inventing use of Technology (with Inventor advantage) references page 211 of the source, outside these chunks. The story "Build Technological Item" covers standard building; Inventing creates temporary devices with advantages/powers but the mechanics are not in scope here.
- **Vehicles animal-mount gap**: The Vehicles skill explicitly excludes animal mounts; Expertise: Riding is the correct skill. The GM may allow Athletics with a circumstance penalty. This decision is GM-adjudicated and not source-specified further.
- **Interaction skill group use mechanics**: The source states the GM decides if group use is effective and may apply modifiers depending on the situation; specific group resistance mechanics are not fully specified beyond the minion example.
- **Perception sense types**: All sense types defined in the Powers chapter are valid for Perception checks; the detailed list and modifiers are out of scope here.

### Advantage
- Favored Environment auto-detection: whether the online tool tracks environmental context (air, water, space, etc.) automatically or requires the player to manually declare "I am in my favored environment" at the start of a round is not specified in the source — affects whether the Declare story is player-driven or system-driven.
- Benefit storage: Benefit is cooperatively defined between player and GM with no mechanical formula; the online tool likely needs a free-text narrative field, but the interface for GM approval/rejection of benefit text is not specified.
- Minion and Sidekick as full characters: whether the online tool creates a full character sheet for minions and sidekicks (with the ability to apply conditions, track damage, etc.) or represents them as simplified stat blocks is not specified — affects the depth of the Configure Minion and Configure Sidekick stories.

### Power
- **Morph effect**: Referenced in source chunks (chunk_121) as a distinct named effect but not included in the module partition's core terms list. Potentially belongs in this module or a separate "Form Change" module.
- **Mind Control**: Referenced in source (chunk_120) as a significant effect but not in the partition's core terms. May be in scope — partition may under-represent Affliction-based control.
- **Mental Blast**: Referenced in source (chunk_117). May be Damage (Perception range) preconfiguration — not in partition.
- **Extra Limbs**: Referenced in source (chunk_104). Not in partition core terms — may be a Feature instance rather than a standalone effect.
- **Element Control and Energy Control**: Referenced in source (chunks 100, 103) as power families rather than individual effects. Not in partition — context only.
- **Force Field**: Referenced in source (chunk_107) as a named configuration (Protection + Sustained extra). Not in partition.
- **Full Extras/Flaws catalog**: Only the 8 most common extras and flaws are in the partition. The full catalog includes Increased Duration, Extended Range, Increased Action, Secondary Effect, Variable Descriptor, Side Effect, and many others. AC phase should note these as out-of-scope for MVP but available via the Modifier KA pattern.
- **Routine effect checks**: Chunk_086 covers routine use of effects. Not mapped as a story — may need a story under Configure Attack Effect or Configure General Effect if the application builds an "auto-resolve" feature.
- **Countering effects**: Chunk_088 (N-W table section) mentions countering in the same section as power effect summaries. Countering as a combat mechanic (not Nullify) may need a story under Combat module.

### Equipment
- Construct size variation: the source says constructs larger/smaller than Medium pay power points for Innate/Permanent Growth or Shrinking, but does not specify when/how the GM adjudicates this in the application — flagged for GM-tools phase.
- Alternate Equipment hero-point stunt: the GM rules whether having an item "on-hand" is possible. The decision criteria are unspecified in source — AC should note this is GM discretion, not a system-enforced rule.
- Vehicle multi-mode movement: the source states Alternate Effects for multiple movement modes but does not specify how the application handles mode switching in play — may require combat sub-system integration.
- Ritual mishap details: 3+ degrees of failure on a ritual research check "may result in a mishap" but no mishap table or severity rules are given in the equipment chapter (cross-reference to GM section needed).
- Team equipment point pooling enforcement: the source says teams may divide cost "however they wish, usually as evenly as possible" — no system enforcement described; AC must treat this as player/GM agreement, not enforced limit.

### Combat
- Maneuver interaction with power effects: when a power effect duplicates a maneuver (e.g., a Snare effect that restrains like a grab), the interaction between the power effect's resistance check and the maneuver's resolution chain is not fully specified in the source. Flag for AC phase.
- Area effect concealment/cover interaction: source states area/perception effects bypass attack checks, but the cover bonus to Dodge resistance checks against area effects (equal to cover penalty to attacks) introduces a residual concealment question — does concealment from dim light also grant any Dodge bonus vs. area effects? Source does not specify.
- Finishing Attack against defenseless targets: the Finishing Attack maneuver (routine check or normal check for auto-crit) is referenced in the feint/defending objects chunks but not listed as its own story; it is implicit in attacking defenseless targets. AC phase should cover it under `Attack or Smash Object` and `Defend` stories.
- Recover action and extra effort interaction: a character can use extra effort to gain an additional resistance check (separate from the Recover action's additional check); whether both can be used in the same turn is not explicitly stated. Assumed yes — extra effort is a free action before or after the Recover action.
- Initiative for characters with the same Dodge and Agility after two tie-breaker steps: source says "each tied player should roll a die" but an application must decide how to handle GM-controlled NPCs in this scenario.
