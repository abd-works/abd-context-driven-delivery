fidelity: discovery / modules / behavior
scope: Reverse-engineered training sketch of Mutants & Masterminds 3e (MM3E) online rules — checks, hero construction, abilities, skills, advantages, powers, equipment, combat. No grill; source is the mm3e transformer fixtures.
status: training sketch from fixtures; not a live engagement
source: harness/transformers/fixtures/mm3e/{story-map.md, modules/*, *-module-partition.md, *-domain-sketch.md, check-resolution/check-resolution-object-model.md}

stories:
Resolve Checks
    * approx 14-16 confirming stories after parameterized grouping
    Make Check
        Player --> Make Trait Check
        System --> Grade Check Result by Degree
        Player --> Make Opposed Check Against Opponent
        System --> Resolve Comparison Check Without Roll
        Player --> Make Resistance Check Against Effect
        Player --> Perform Routine Check
        Player --> Lead Team Check with Helpers
    Apply Conditions
        System --> Apply Condition to Character
        System --> Supersede Condition in Chain
    Recover from Conditions
        Player --> Roll Resistance Check Against Ongoing Effect to Remove Conditions
        System --> Remove Condition When Source Effect Ends
        Player --> Roll Fortitude Check to Stabilize While Dying
        Player --> Stabilize Dying Ally with Treatment Check
    Translate Rank to Measure
        System --> Translate Trait Rank to Real-World Value
        System --> Derive Measurement from Rank Formula
~> Increment 1: d20 vs DC, graded resistance, conditions: Make Trait Check, Grade Check Result by Degree, Apply Condition to Character

Construct Hero
    * approx 18-22 confirming stories
    Allocate Resources
        GM --> Set Series Power Level
        System --> Derive Starting Power Points from Power Level
        Player --> Spend Power Points on Trait Ranks
        System --> Validate Power Points Total Balance
    Enforce Power Level Limits
        System --> Enforce Limit Pair Cap
        Player --> Apply Trade-Off within Limit Pair
    Define Hero Identity
        Player --> Develop Hero Concept
        Player --> Choose Hero Origin
        Player --> Record Hero Background Details
        Player --> Design Hero Costume
    Choose Complications
        Player --> Choose Motivation Complication
        Player --> Choose Complication
        Player --> Specify Weakness Trigger and Effect with GM
        System --> Validate Minimum Complication Requirement
        Player --> Evolve Complication over Series
    Approve and Finalize Hero
        GM --> Review Hero Power Points Allocation
        GM --> Verify Hero Follows Power Level Guidelines
        GM --> Approve Completed Hero for Play
    Advance Hero
        GM --> Award Power Points after Adventure
        Player --> Spend Earned Power Points on Traits
        System --> Enforce Power Level Limits on Earned Spending
        GM --> Raise Series Power Level
        Player --> Reallocate Power Points via Transformation
~> Increment 1: PL, starting PP, spend, balance: Set Series Power Level, Spend Power Points on Trait Ranks, Validate Power Points Total Balance

Assign Abilities
    * approx 12-14 confirming stories
    Configure Ability Scores
        Player --> Set Ability Rank
        Player --> Designate Ability Rank Portion as Enhanced
        System --> Cascade Trait Changes on Ability Rank Alteration
        System --> Enforce Ability Rank Ceiling per Power Level
    Configure Derived Defenses
        System --> Derive Base Defense Rank from Ability
        Player --> Increase Defense Rank Above Ability Base
        System --> Enforce Toughness Increase Restriction
        System --> Derive Initiative Modifier from Agility
    Handle Absent Ability
        System --> Apply Absent Ability Capability Restrictions
        System --> Grant Bonus Power Points for Absent Ability
        GM --> Authorize Hero to Have Absent Ability
    Handle Debilitated Ability
        System --> Apply Debilitated Ability Condition Effects
        System --> Prevent Further Rank Reduction When Debilitated
        System --> Clear Debilitated State When Ability Rank Recovers

Manage Skills
    * approx 16-20 confirming stories after parameterized uses
    Configure Skill Ranks
        Player --> Assign Skill Ranks
        System --> Enforce Skill Modifier Limit
    Resolve Skill Checks
        Player --> Make Skill Check
        System --> Apply Critical Success on Natural 20
        System --> Resolve Untrained Skill Attempt
        System --> Apply Skill Mastery Routine Result
        System --> Apply Circumstance Modifier to Skill Check
    Use Interaction Skills
        System --> Enforce Interaction Skill Requirements
        Player --> Use Interaction Skill Against Target
    Use Physical Skills
        Player --> Use Physical Skill
        System --> Apply Fall Damage to Character
    Use Combat Skills
        Player --> Add Close Combat Rank to Attack Check
        Player --> Add Ranged Combat Rank to Attack Check
    Use Manipulation Skills
        Player --> Use Manipulation Skill
    Use Knowledge and Awareness Skills
        Player --> Use Knowledge Skill
        GM --> Resolve Expert Knowledge Check Secretly
        GM --> Make Secret Perception Check for Character

Select Advantages
    * approx 16-18 confirming stories
    Acquire Advantage
        Player --> Purchase Advantage Rank
        System --> Validate Power Point Cost for Advantage
        System --> Enforce Power Level Cap on Attack Advantage Bonus
        System --> Cap Luck Maximum Rank at Half Power Level
    Apply Combat Advantage
        Player --> Execute Attack Trade-Off Maneuver
        System --> Adjust Attack and Defense Values by Trade-Off Amount
        System --> Apply Ranked Attack Bonus to Close or Ranged Attack Check
        System --> Apply Initiative Bonus from Improved Initiative
        System --> Apply Extended Critical Threat Range via Improved Critical
        Player --> Declare Favored Environment Bonus Allocation
        System --> Apply Favored Environment Circumstance Bonus
    Activate Fortune Advantage
        Player --> Re-Roll Die Using Luck Rank
        System --> Enforce Luck Session-Use Limit and Refresh at Adventure Start
        Player --> Inspire Allies with Hero Point
        System --> Apply Inspiration Bonus Ignoring Power Level Cap
        Player --> Remove Ally Condition via Leadership
        Player --> Gain Temporary Skill Ranks via Beginner's Luck
    Use Skill Advantage
        Player --> Use Any Skill Untrained via Jack of All Trades
        Player --> Make Routine Skill Check Under Pressure via Skill Mastery
        System --> Apply Favored Foe Circumstance Bonus to Qualifying Checks
    Manage Character Resources
        Player --> Allocate Equipment Points to Gear
        Player --> Configure Minion Traits Within Power Point Budget
        Player --> Configure Sidekick Traits Within Power Point Budget
        Player --> Propose Benefit to GM
    Maintain Advantage State
        System --> Persist Advantage Selections on Character Sheet
        System --> Track Luck Rank Uses per Session
        System --> Refresh Luck Ranks at Start of Adventure

Configure Powers
    * approx 22-28 confirming stories after effect-family grouping
    Configure Attack Effect
        Player --> Select Attack Effect
        System --> Resolve Attack Effect Resistance Check
        System --> Recover from Attack Effect Condition
    Configure Defense Effect
        Player --> Select Defense Effect
        System --> Apply Immunity Check Against Matching Power Descriptor
        System --> Recover via Regeneration or Immortality
    Configure Mobility Effect
        Player --> Select Mobility Effect
        System --> Calculate Movement Rank from Effect Rank
        System --> Validate Teleport Destination as Known or Accurately Sensed
    Configure Sensory Effect
        Player --> Select Sensory Effect
        System --> Grant Total Concealment Against Chosen Sense Type
        System --> Resolve Mind Reading Opposed Check Against Will Defense
    Configure Control Effect
        Player --> Select Control Effect
        System --> Enforce Created Object Volume and Toughness from Effect Rank
        System --> Resolve Control Effect Check
    Configure General Effect
        Player --> Select General Effect
        System --> Enforce Variable Pool Size as Rank Times Five Points
        System --> Apply Healing Check and Remove Damage Condition from Most Severe
    Apply Per-Rank Modifiers
        System --> Set Default Action Range Duration for Effect Type
        System --> Calculate Base Cost per Rank from Effect Definition
        Player --> Apply Per-Rank Extra or Flaw
        System --> Enforce Minimum One Point per Rank Floor After Flaws
    Apply Flat Modifiers
        Player --> Apply Flat Extra or Flaw
        System --> Calculate Final Power Cost with Flat Modifier Adjustments
        System --> Enforce Minimum One Point Total Power Cost After Flat Flaws
    Assign Power Descriptors
        Player --> Assign Descriptor to Power
        System --> Match Power Descriptor Against Immunity or Nullify
        GM --> Approve Descriptor Interaction Between Powers
    Organize Power Arrays
        Player --> Build Power Array with Base Effect
        Player --> Add Alternate Effect to Array
        Player --> Switch Active Effect in Array as Free Action
        System --> Enforce Array Mutual Exclusivity Rule for Non-Dynamic Effects

Equip Hero
    * approx 18-22 confirming stories after catalog grouping
    Configure Equipment Pool
        Player --> Acquire Equipment Advantage Ranks
        System --> Derive Equipment Point Budget from Advantage Ranks
        Player --> Pay Equipment Points for Item
        System --> Enforce Equipment Point Budget Limit
        System --> Enforce Equipment Bonus Non-stacking
        Player --> Build Alternate Equipment Array
    Acquire Weapons
        Player --> Select Weapon
        System --> Add Wielder Strength to Melee Damage
        System --> Apply Area Weapon Effect
    Acquire Defensive Gear
        Player --> Select Armor or Shield
        System --> Enforce Armor Bonus Non-stacking Rule
        System --> Cap Equipment Toughness at Power Level
    Acquire General Gear
        Player --> Purchase General Gear
        Player --> Build Utility Belt Array
    Build Device
        Player --> Designate Power as Removable Device
        System --> Calculate Reduced Cost from Removable Flaw
        Player --> Build Specialized Device
        System --> Remove Powers When Device Taken Away
    Invent Temporary Device
        Player --> Define Invention Effect and Point Cost
        Player --> Complete Construction Check
        Player --> Use Invention for One Scene
        Player --> Jury-Rig Device by Spending Hero Point
    Design Vehicle
        Player --> Select Vehicle Size Category
        System --> Derive Base Vehicle Traits from Size
        Player --> Add Vehicle Feature or Power Effect
    Design Headquarters
        Player --> Select Headquarters Size Category
        Player --> Add Headquarters Feature
        System --> Allow Rebuild of Destroyed Headquarters
    Build Construct
        Player --> Choose Construct Ability Profile
        System --> Verify Zero Net Cost for Standard Construct Traits
        Player --> Issue Order to Construct on Move Action

Conduct Combat
    * approx 20-24 confirming stories after maneuver grouping
    Manage Turn Order
        System --> Roll Initiative Check
        System --> Determine Turn Order from Initiative Results
        Player --> Delay Turn to Later Initiative Position
        Player --> Ready Action for Trigger Condition
    Manage Action Economy
        Player --> Take Standard Action on Turn
        Player --> Take Move Action on Turn
        Player --> Exchange Standard Action for Additional Move Action
        Player --> Take Free Action During Turn
        Player --> Take Reaction Outside Turn
    Execute Attacks
        Player --> Make Attack Check Against Defense
        System --> Resolve Attack Check Against Defense Class
        System --> Determine Critical Hit When Total Meets Defense
        Player --> Apply Critical Hit Effect Choice
        System --> Bypass Attack Check for Area or Perception Effect
    Apply Aim and Charge
        Player --> Aim for Attack Bonus
        Player --> Execute Charge Attack with Penalty
        Player --> Execute Slam Attack During Charge
    Perform Combat Maneuvers
        Player --> Defend Against Incoming Attacks
        Player --> Execute Grab Attempt
        Player --> Execute Disarm Attempt
        Player --> Execute Trip Attempt
        Player --> Execute Feint with Deception Check
    Resolve Damage and Recovery
        System --> Resolve Toughness Resistance Check Against Damage
        System --> Apply Damage Condition by Degree of Failure
        Player --> Recover from Damage in Conflict
        System --> Resolve Ongoing Effect Resistance Check at End of Turn
    Handle Tactical Environment
        System --> Apply Concealment or Cover Penalty to Attack Check
        GM --> Apply Surprise Round Rules
        Player --> Execute Team Attack with Coordinated Attackers
    Handle Hazards and Objects
        System --> Apply Falling Damage by Distance Rank
        System --> Apply Suffocation Sequence
        Player --> Attack or Smash Object
    Use Hero Resources
        Player --> Spend Hero Point
        Player --> Declare Extra Effort for Combat Benefit
        Player --> Activate Power Stunt via Extra Effort
        System --> Apply Extra Effort Fatigue at Start of Next Turn

ce:
checks/                              // Trait, Check, Condition, Measurement
  // seam: resolve a trait check; apply and supersede conditions; look up rank as measure
  // constraint: only Check owns d20 + modifier vs DC; other modules ask Trait.performCheck
  // standalone: Character, Effect rank, and action-round enforcement are neighbors — this module takes a Character token, an integer effect rank, and named conditions; it does not import those modules
  Trait
    character
    traitName
    purchasedRank
    effectiveRank
    realWorldValue type
    addRank other type
    performCheck dc
       -> Measurement.lookup
       -> Check.resolve
  Measurement
    lookup rank type
    rankFor measure type
    throwingDistanceRank strengthRank massRank
    travelDistanceRank timeRank speedRank
    travelTimeRank distanceRank speedRank
  Check
    trait
    dc
    circumstanceModifier
    resolve
    resolveGraded
       -> Trait.effectiveRank
  CheckResult
    rollTotal
    dc
    isSuccess
    margin
    isCritical
  GradedCheckResult : CheckResult
    degree
    resultingCondition
  DifficultyClass
    value
  OpposedCheck : Check
    opponent
    isPassive
    resolve
  RoutineCheck : Check
    resolve
  TeamCheck : Check
    helpers
    resolve
  Condition
    name
    gameModifier
    supersedes
    supersededBy
    constituents
  ImposedCondition
    condition
    source
    active
  ImposedConditions
    apply condition source
    supersede
    removeWhenSourceEnds
    activeConditions
  // invariant: ranks never added as integers — convert through Measurement
  // invariant: only active conditions apply modifiers
  // invariant: same-source supersession removes lesser; different-source parks inactive

character-construction/              // Hero, PowerLevel, PowerPoints, Complication, TradeOff
  // seam: set series PL; spend PP; enforce limit pairs; complications; GM approve
  // constraint: this module owns PP currency and PL caps; Ability/Skill/Advantage/Power do not invent a second budget
  // dep -> ability (ability rank cost 2 PP; defenses)
  // dep -> skill (2 ranks per PP; PL+10 modifier cap)
  // dep -> advantage (1 PP per rank)
  // dep -> power (effect cost formula)
  Hero
    powerLevel
    powerPoints
    complications
    spendOn trait
    validateBalance
    enforceLimitPair
  PowerLevel
    startingPowerPoints
  Complication
    type
    trigger
  TradeOff
    pair
    amount

ability/                             // Ability, Defense
  // seam: set eight ability ranks; cascade derived traits; absent vs debilitated
  // constraint: Ability is a Trait; Check Resolution owns the check formula
  // dep -> checks (Trait)
  // dep -> character-construction (PP spend, PL ceiling, GM authorize absent)
  Ability : Trait
    naturalRank
    enhancedRank
    setRank
    cascadeDependents
    applyAbsentRestrictions
    applyDebilitated
  Defense : Trait
    sourceAbility
    purchasedAboveBase
    deriveBase
  // invariant: voluntary rank never below -5; below -5 is debilitated from an effect
  // invariant: absent is not rank -5
  // invariant: Toughness cannot be bought above Stamina base

skill/                               // Skill
  // seam: assign ranks; make skill check; trained-only; interaction gates
  // constraint: skill check is Trait.performCheck — do not fork a second d20 engine
  // dep -> checks
  // dep -> ability (linked ability rank)
  // dep -> character-construction (PL+10 skill modifier cap)
  Skill : Trait
    linkedAbility
    trainedOnly
    assignRanks
    makeCheck
    resolveUntrained

advantage/                           // Advantage
  // seam: purchase advantage; apply combat/fortune/skill advantage effects
  // constraint: Equipment/Minion/Sidekick budgets live with Equipment; Luck uses live here
  // dep -> checks
  // dep -> character-construction (PP, PL cap on attack bonus)
  // dep -> combat (trade-off on attack/defense; hero point for Inspire/Leadership)
  Advantage : Trait
    category
    rank
    purchase
    apply
  AttackTradeOff
    penaltyStat
    bonusStat
    amount
  Luck
    usesThisSession
    reRoll
    refresh

power/                               // Power, Effect, Extra, Flaw, Descriptor, Array
  attack
  defense
  mobility
  sensory
  control
  general
  extras
  flaws
  // seam: select effect; cost = (base + extras − flaws) × rank + flat; resolve via checks
  // constraint: Effect rank is a Trait rank; resistance DC is 10 + effect rank in checks
  // dep -> checks (resistance, opposed, conditions)
  // dep -> ability (Enhanced Trait portion)
  // dep -> character-construction (PP, PL on built effects)
  Power
    descriptors
    array
    cost
  Effect : Trait
    action
    range
    duration
    baseCostPerRank
    resolve
  Extra
    perRank
  Flaw
    perRank
    removable
  Array
    baseEffect
    alternates
    dynamic
    switchActive
    reallocate
  // invariant: after flaws, at least 1 PP per rank (or fractional ranks) and at least 1 PP total
  // invariant: non-dynamic array effects are mutually exclusive

equipment/                           // Equipment, Device, Vehicle, Headquarters, Construct
  weapons
  armor
  vehicles
  headquarters
  constructs
  // seam: spend equipment points; removable device cost; invent; vehicle/HQ size traits
  // constraint: equipment bonus does not stack with same-type equipment bonus; Protection from a device is not equipment bonus
  // dep -> advantage (Equipment ranks → EP budget; Minion for construct)
  // dep -> power (device is a power with Removable; vehicle/HQ power effects at 1/5)
  // dep -> checks (design/construction checks; Technology repair)
  Equipment
    equipmentPoints
    items
    payFor item
  Device : Power
    removable
    easilyRemovable
    indestructible
  Vehicle
    size
    features
  Headquarters
    size
    features
  Construct
    abilityProfile
    issueOrder

combat/                              // ActionRound, Attack, Damage, HeroPoint, ExtraEffort
  turns
  actions
  maneuvers
  // seam: initiative; action economy; attack vs defense class; damage degrees; hero point; extra effort
  // constraint: attack check is a Check against Parry or Dodge class; damage is a graded Toughness resistance
  // dep -> checks (Check, GradedCheckResult, Condition)
  // dep -> ability (defenses, initiative from Agility)
  // dep -> skill (Close Combat, Ranged Combat, Deception feint)
  // dep -> advantage (trade-offs, Improved Critical)
  // dep -> power (area/perception bypass attack check)
  ActionRound
    turnOrder
    rollInitiative
  Turn
    standardAction
    moveAction
    freeAction
    reaction
  Attack
    attackBonus
    defenseClass
    resolve
    confirmCritical
  Damage
    toughnessResistance
    applyDegree
  HeroPoint
    spend
  ExtraEffort
    declareBenefit
    applyFatigue

build-order: checks → character-construction → ability → skill → advantage → power → equipment → combat

bdd:
a trait on a hero
  that has a purchased rank
    it should supply that rank as the check modifier
    with an active condition targeting the trait
      it should reduce effective rank by the condition game modifier
    that converts rank to a real-world value
      it should look up the measurement table for the named dimension
    that combines two ranks
      it should convert to measures, add or subtract, then convert back to a rank

a check of a trait
  that is resolved against a difficulty class
    it should succeed when roll total meets or exceeds the difficulty class
    it should fail when roll total is below the difficulty class
    with a natural 20
      it should increase degree of success by one after normal grading
  that is graded
    it should count one degree per full five points of margin
  that is opposed
    with an actively contesting opponent
      it should compare both roll totals
    with passive opposition
      it should set difficulty class to opposing modifier plus ten
    that is a comparison without a roll
      it should award the higher rank
  that is routine
    it should substitute ten for the die
  that is a team check
    it should apply helper circumstance to the leader check only

a resistance check against an effect
  that uses a defense bonus
    it should set difficulty class to ten plus effect rank
    with degrees of failure
      it should map each degree to the effect condition set

a condition on a hero
  that is basic
    it should apply its single game modifier only while active
  that is combined
    it should bundle named basic constituents
    that has one constituent resolved
      it should leave remaining constituents in place
  that is superseded by a more severe condition from the same source
    it should remove the lesser condition
  that is imposed from a different source while a more severe condition is active
    it should stay inactive until the blocking condition is gone
  that has its source effect end
    it should be removed whether active or inactive

a hero under construction
  that has a series power level
    it should derive starting power points from that power level
  that spends power points on traits
    it should charge ability ranks at two points per rank
    it should charge skill ranks at one point per two ranks
    it should charge advantages at one point per rank
    it should charge powers from the effect cost formula
  that exceeds a limit pair
    it should reject the allocation unless a trade-off keeps the pair at twice power level
  that lacks a motivation complication
    it should fail the minimum complication requirement
  that the gamemaster has not approved
    it should not be available for play

an ability rank
  that changes
    it should cascade skills, defenses, and attack modifiers in the same operation
  that includes an enhanced portion
    it should keep the natural portion when the enhanced portion is nullified
  that is absent
    it should apply that ability's capability restrictions
    it should not treat absence as rank minus five
  that drops below minus five
    it should apply the debilitated condition set for that ability group
    it should block further rank reduction
  that recovers to minus five or above
    it should clear the debilitated state
  that is Toughness
    it should refuse a purchase above the Stamina base

a skill
  that has assigned ranks
    it should keep total modifier at or below power level plus ten
  that is used for a check
    it should use d20 plus rank plus ability plus circumstance
  that is trained only and used untrained
    it should fail without a roll
  that is not trained only and used untrained
    it should proceed at rank zero with ability
  that has Skill Mastery
    it should allow the routine result under pressure
  that is an interaction skill
    with a subject that cannot comprehend
      it should apply the interaction requirement penalty or block

an advantage
  that is purchased
    it should cost one power point per rank
  that is an attack trade-off
    it should apply equal penalty and bonus up to five
  that is Close Attack or Ranged Attack
    it should add rank to matching attack checks within the power level cap
  that is Luck
    it should consume one session use per re-roll
    that starts a new adventure
      it should refresh luck uses
  that is Jack of All Trades
    it should allow untrained use of trained-only skills

a power effect
  that is configured
    it should use the effect type default action, range, and duration
    it should cost base plus extras minus flaws times rank plus flat modifiers
  that has flaws that would drop cost below one point per rank
    it should keep the one point per rank floor
  that is an affliction
    it should require exactly three conditions in degree order
  that is in a non-dynamic array
    it should be mutually exclusive with sibling alternates
  that is a dynamic array member
    it should share the array pool without exceeding it
  that has descriptors
    it should match immunity and nullify by descriptor

equipment on a hero
  that is paid from equipment points
    it should reject a purchase past the Equipment advantage budget
  that stacks two armor bonuses
    it should apply only the higher equipment bonus
  that is a removable device
    it should reduce power cost by the removable flaw
    that is taken away
      it should remove the device powers
  that is a standard construct
    it should keep absent Stamina plus Fortitude immunity at zero net cost

a combat turn
  that has initiative results
    it should order turns by initiative then Dodge then Agility
  that still has a standard action
    it should allow a close attack against Parry or a ranged attack against Dodge
  that rolls a natural 20 that also meets defense class
    it should confirm a critical hit
  that uses an area or perception effect
    it should skip the attack check
  that fails a Toughness resistance
    it should apply damage condition by degree of failure
  that spends a hero point to re-roll
    it should treat a re-roll of one through ten as eleven
  that declared extra effort
    it should apply fatigue at the start of the next turn
