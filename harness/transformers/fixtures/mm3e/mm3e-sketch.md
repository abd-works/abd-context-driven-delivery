fidelity: specification / modules / behavior
scope: Reverse-engineered training sketch of Mutants & Masterminds 3e (MM3E) online rules — checks, hero construction, abilities, skills, advantages, powers, equipment, combat. No grill; source is the mm3e transformer fixtures.
status: training sketch from fixtures; stories deepened with scenarios from acceptance-criteria.md
source: harness/transformers/fixtures/mm3e/{story-map.md, */acceptance-criteria.md, check-resolution/check-resolution-object-model.md}

stories:
Resolve Checks
    Make Check
        Player --> Make Trait Check
            given Hero.nova with Trait.strength.purchasedRank 5
            check succeeds when roll total meets dc
                given DifficultyClass.value 15
                    and Check.circumstanceModifier 0
                when Trait.performCheck dc
                then CheckResult.isSuccess is true
                    and CheckResult.rollTotal includes Trait.effectiveRank
                    and Grade Check Result by Degree
            check fails when roll total is below dc
                given DifficultyClass.value 15
                when Trait.performCheck dc
                then CheckResult.isSuccess is false
            circumstance modifiers add to roll total
                given Check.circumstanceModifier 2
                when Trait.performCheck dc
                then CheckResult.rollTotal includes circumstanceModifier
            missing tools impose minus five
                given required tools are absent
                when Trait.performCheck dc
                then Check.circumstanceModifier is -5
            makeshift tools reduce the penalty to minus two
                given makeshift tools
                when Trait.performCheck dc
                then Check.circumstanceModifier is -2
            natural 20 upgrades degree after grading
                given the d20 face is 20
                when Trait.performCheck dc
                then CheckResult.isCritical is true
                    and GradedCheckResult.degree increases by one after margin
        System --> Grade Check Result by Degree
            given CheckResult from Trait.performCheck
            success grades one degree plus one per full five of margin
                given CheckResult.isSuccess is true
                    and CheckResult.margin 7
                when Check.resolveGraded
                then GradedCheckResult.degree is 2
            failure grades one degree plus one per full five below
                given CheckResult.isSuccess is false
                    and CheckResult.margin -7
                when Check.resolveGraded
                then GradedCheckResult.degree is 2
            four degrees of success is the maximum
                given CheckResult.margin 15
                when Check.resolveGraded
                then GradedCheckResult.degree is 4
            four degrees of failure is the maximum
                given CheckResult.margin -20
                when Check.resolveGraded
                then GradedCheckResult.degree is 4
            natural 20 can flip one degree of failure to success
                given CheckResult.isCritical is true
                    and margin would be one degree of failure
                when Check.resolveGraded
                then CheckResult.isSuccess is true
        Player --> Make Opposed Check Against Opponent
            given Hero.nova and Hero.villain each with a matching Trait
            higher roll total wins
                when OpposedCheck.resolve
                then CheckResult.isSuccess is true for the higher rollTotal
            tie goes to higher trait bonus
                given both rollTotals are equal
                    and Hero.nova.Trait.effectiveRank is higher
                when OpposedCheck.resolve
                then Hero.nova wins
            equal totals and bonuses use tie-break d20
                given both rollTotals and effectiveRanks are equal
                when OpposedCheck.resolve
                then a tie-break d20 awards 1-10 to the active character or 11-20 to the opponent
            passive opposition sets dc to opponent modifier plus ten
                given OpposedCheck.isPassive is true
                when OpposedCheck.resolve
                then DifficultyClass.value is opponent Trait.effectiveRank plus 10
                    but Hero.villain does not roll
        System --> Resolve Comparison Check Without Roll
            given two Traits on Hero.nova and Hero.villain
            higher rank wins without a die
                when ranks are compared
                then the higher Trait.effectiveRank wins
                    but no d20 is rolled
                    but no Circumstance Modifier applies
            equal ranks report a tie
                given both effectiveRanks are equal
                when ranks are compared
                then there is no winner
        Player --> Make Resistance Check Against Effect
            given Hero.nova with Defense.will
                and Effect.rank 8
            resistance uses ten plus effect rank as dc
                when Trait.performCheck DifficultyClass 18
                then Check is a resistance check using Defense.will as modifier
            success applies no condition from this effect
                given CheckResult.isSuccess is true
                then ImposedConditions has no condition from this Effect
            failure maps degree to the effect condition set
                given GradedCheckResult.degree of failure 2
                when ImposedConditions.apply condition source
                then Hero.nova carries the degree-2 Condition
                    and Apply Condition to Character
            same source more severe removes the lesser
                given this Effect already imposed a lesser Condition
                when ImposedConditions.apply more severe Condition
                then the lesser Condition is removed
            same source lesser leaves the more severe unchanged
                given this Effect already imposed a more severe Condition
                when ImposedConditions.apply lesser Condition
                then the active Condition is unchanged
            different source lesser is parked inactive
                given a more severe Condition from another source is active
                when ImposedConditions.apply lesser Condition from this Effect
                then the new ImposedCondition.active is false until the blocker is gone
        Player --> Perform Routine Check
            given Hero.nova Trait.effectiveRank 8
                and DifficultyClass.value 15
            routine substitutes ten for the die
                when RoutineCheck.resolve
                then CheckResult.rollTotal is 10 plus Trait.effectiveRank plus circumstanceModifier
                    and CheckResult.isCritical is false
            insufficient routine total lets the player roll
                given RoutineCheck rollTotal is below DifficultyClass
                then the Player may Trait.performCheck instead
            plus ten against dc 20 succeeds without rolling
                given Trait.effectiveRank 10
                    and DifficultyClass.value 20
                when RoutineCheck.resolve
                then CheckResult.isSuccess is true
        Player --> Lead Team Check with Helpers
            given Hero.nova as leader
                and Helpers each with the same Trait
            helpers check dc 10 then modify the leader
                when TeamCheck.resolve
                then each Helper Trait.performCheck DifficultyClass 10
                    and only the leader CheckResult decides the outcome
            one or two helper successes grant plus two
                given one or two Helper CheckResult.isSuccess
                then leader Check.circumstanceModifier includes 2
            three helper successes grant plus five
                given three Helper CheckResult.isSuccess
                then leader Check.circumstanceModifier includes 5
            helper failure may impose minus two
                given a Helper CheckResult.isSuccess is false
                then leader Check.circumstanceModifier may include -2
    Apply Conditions
        System --> Apply Condition to Character
            given Hero.nova
            basic condition applies its game modifier while active
                given Condition.impaired
                when ImposedConditions.apply Condition source
                then ImposedCondition.active is true
                    and Trait.effectiveRank is reduced by GameModifier.amount 2
            combined condition applies constituents
                given Condition.staggered
                when ImposedConditions.apply Condition source
                then constituents dazed and hindered are present
            multiple active conditions stack
                given Condition.impaired and Condition.hindered both active
                then both GameModifiers apply
            dazed limits the turn to free plus one standard
                given Condition.dazed is active
                then Hero.nova may take free actions and one standard action
            vulnerable halves active defenses rounding up
                given Condition.vulnerable is active
                then Defense.dodge and Defense.parry are halved rounding up
        System --> Supersede Condition in Chain
            given Hero.nova already carries a lesser Condition
            more severe from same chain overrides the lesser
                when ImposedConditions.supersede
                then only the more severe GameModifier applies
            dazed then stunned
                given Condition.dazed is active
                when ImposedConditions.apply Condition.stunned
                then no actions including free actions
            impaired then disabled
                given Condition.impaired is active
                when ImposedConditions.apply Condition.disabled
                then GameModifier.amount is -5
            vulnerable then defenseless
                given Condition.vulnerable is active
                when ImposedConditions.apply Condition.defenseless
                then active defense bonuses are 0
            hindered then immobile
                given Condition.hindered is active
                when ImposedConditions.apply Condition.immobile
                then movement speed is 0
            compelled then controlled
                given Condition.compelled is active
                when ImposedConditions.apply Condition.controlled
                then all actions are dictated by the controller
    Recover from Conditions
        Player --> Roll Resistance Check Against Ongoing Effect to Remove Conditions
            given Hero.nova carries Conditions from an ongoing Effect
            success ends the effect and clears its conditions
                when Trait.performCheck against the Effect
                    and CheckResult.isSuccess is true
                then the Effect ends
                    and ImposedConditions.removeWhenSourceEnds for that Effect
                    and parked Conditions from other sources may become active
                    and Remove Condition When Source Effect Ends
            failure leaves the effect and its conditions
                when CheckResult.isSuccess is false
                then Conditions from the Effect remain
            extra degrees of failure may add conditions
                given GradedCheckResult.degree of failure greater than 1
                when the Effect remains
                then additional Conditions from the effect set are applied
        System --> Remove Condition When Source Effect Ends
            given Hero.nova carries Conditions from Effect.affliction
            source end removes that source only
                when ImposedConditions.removeWhenSourceEnds Effect.affliction
                then Conditions from Effect.affliction are gone
                    but Conditions from other sources remain
            lesser from another still-active source becomes active
                given a lesser ImposedCondition.active is false
                    and the blocking Condition's source ends
                    and the lesser source is still active
                then the lesser ImposedCondition.active is true
            lesser does not return when its source also ended
                given the lesser source has ended
                when the blocking Condition ends
                then the lesser Condition does not re-emerge
        Player --> Roll Fortitude Check to Stabilize While Dying
            given Hero.nova carries Condition.dying
            each round requires fortitude dc 15
                when Defense.fortitude.performCheck DifficultyClass 15
                then accumulated degrees are recorded
            two degrees of success stabilize
                given accumulated success degrees reach 2
                then Condition.dying ends
            three total degrees of failure is death
                given accumulated failure degrees reach 3
                then Hero.nova is dead
            natural 20 accelerates stabilization
                given the Fortitude Check isCritical
                then success degree increases by one after grading
        Player --> Stabilize Dying Ally with Treatment Check
            given Hero.ally carries Condition.dying
                and Hero.nova has Skill.treatment
            treatment check can stabilize the ally
                when Skill.treatment.makeCheck
                then on success Condition.dying ends on Hero.ally
                    but a dying character is not revived without stabilize first
    Translate Rank to Measure
        System --> Translate Trait Rank to Real-World Value
            given Trait.effectiveRank
            lookup returns the named dimension
                when Trait.realWorldValue MEASUREMENT_TYPE.DISTANCE
                then Measurement.lookup rank type returns the table value
            negative rank halves the previous measure
                given a lower Rank
                then the measure is half the rank above
            ranks are never added as integers
                when two ranks must combine
                then convert through Measurement then convert back
        System --> Derive Measurement from Rank Formula
            given Time Rank and Speed Rank
            travel distance is time plus speed through measures
                when Measurement.travelDistanceRank timeRank speedRank
                then the result is looked up as distance
            travel time is distance minus speed through measures
                when Measurement.travelTimeRank distanceRank speedRank
                then the result is looked up as time
            throwing distance is strength minus mass through measures
                when Measurement.throwingDistanceRank strengthRank massRank
                then the result is looked up as distance
~> Increment 1: d20 vs DC, graded resistance, conditions: Make Trait Check, Grade Check Result by Degree, Apply Condition to Character

Construct Hero
    Allocate Resources
        GM --> Set Series Power Level
            given a Series with no PowerLevel
            series pl caps every player hero
                when GM sets PowerLevel 10
                then Hero.nova.powerLevel is 10
                    and startingPowerPoints is 150
                    and each limit pair ceiling is 20
                    but a Player cannot set a personal PowerLevel
            missing pl blocks construction
                given PowerLevel is unset
                when the Player starts hero design
                then construction steps are blocked
        System --> Derive Starting Power Points from Power Level
            given PowerLevel 10
            table default is pl times fifteen
                when PowerLevel.startingPowerPoints is derived
                then Hero.nova.powerPoints budget is 150
            gm adjustment changes budget not pl
                given GM sets starting PP 165
                then Hero.nova.powerPoints budget is 165
                    but PowerLevel remains 10
        Player --> Spend Power Points on Trait Ranks
            given Hero.nova with remaining powerPoints
            ability ranks cost two each
                when Hero.spendOn Ability.strength plus 1
                then powerPoints decrease by 2
            defense ranks cost one above ability base
                when Hero.spendOn Defense.dodge plus 1
                then powerPoints decrease by 1
            skill ranks cost one per two ranks
                when Hero.spendOn Skill.perception plus 2
                then powerPoints decrease by 1
            advantages cost one per rank
                when Hero.spendOn Advantage plus 1
                then powerPoints decrease by 1
            powers use the effect cost formula
                when Hero.spendOn Power
                then cost is (base plus extras minus flaws) times rank plus flat
            insufficient points reject the spend
                given remaining powerPoints below the cost
                when Hero.spendOn trait
                then the trait is unchanged
                    and powerPoints are unchanged
        System --> Validate Power Points Total Balance
            given Hero.nova allocations
            spent equals starting budget
                when Hero.validateBalance
                then remaining powerPoints is 0 or the leftover is shown
            overspend is rejected
                given spent exceeds startingPowerPoints
                when Hero.validateBalance
                then the hero is not valid
    Enforce Power Level Limits
        System --> Enforce Limit Pair Cap
            given PowerLevel 10
            attack and effect pair
                given attack bonus plus effect rank would exceed 20
                when Hero.enforceLimitPair
                then the allocation is rejected
            dodge and toughness pair
                given Dodge plus Toughness would exceed 20
                when Hero.enforceLimitPair
                then the allocation is rejected
            parry and toughness pair
                given Parry plus Toughness would exceed 20
                when Hero.enforceLimitPair
                then the allocation is rejected
            fortitude and will pair
                given Fortitude plus Will would exceed 20
                when Hero.enforceLimitPair
                then the allocation is rejected
            skill modifier cap
                given Skill modifier would exceed PowerLevel plus 10
                when Hero.enforceLimitPair
                then the allocation is rejected
        Player --> Apply Trade-Off within Limit Pair
            given a pair at the 2 times PL ceiling
            trade-off keeps the pair sum
                when Player applies TradeOff.amount
                then one side decreases by amount
                    and the other increases by amount
                    and the pair still equals 2 times PowerLevel
    Define Hero Identity
        Player --> Develop Hero Concept
            given Hero.nova under construction
            concept is recorded
                when the Player records the concept
                then Hero.nova identity includes the concept
        Player --> Choose Hero Origin
            when the Player chooses an origin
            then Hero.nova origin is stored
        Player --> Record Hero Background Details
            when the Player records background
            then Hero.nova background is stored
        Player --> Design Hero Costume
            when the Player designs a costume
            then Hero.nova costume is stored
    Choose Complications
        Player --> Choose Motivation Complication
            given Hero.nova
            motivation is required
                when the Player chooses Complication.type motivation
                then Hero.nova.complications includes motivation
        Player --> Choose Complication
            given a non-motivation non-weakness type
            player defines narrative detail
                when the Player chooses Complication.type enemy or identity or responsibility or relationship or secret or power loss
                then the Complication is stored
                    but the GM may overrule
        Player --> Specify Weakness Trigger and Effect with GM
            when the Player and GM specify Weakness trigger and effect
            then Complication.weakness is stored with trigger
        System --> Validate Minimum Complication Requirement
            given Hero.nova
            missing motivation fails
                given complications has no motivation
                when the system validates
                then the hero is not valid
        Player --> Evolve Complication over Series
            given an existing Complication
            when the Player evolves it during the series
            then the stored Complication updates
    Approve and Finalize Hero
        GM --> Review Hero Power Points Allocation
            given Hero.nova allocations
            when the GM reviews
            then spent versus startingPowerPoints is visible
        GM --> Verify Hero Follows Power Level Guidelines
            given Hero.nova
            when the GM verifies
            then each limit pair is at or under 2 times PowerLevel
        GM --> Approve Completed Hero for Play
            given reviews pass
            when the GM approves
            then Hero.nova is available for play
            given the GM has not approved
            when play starts
            then Hero.nova is not available for play
    Advance Hero
        GM --> Award Power Points after Adventure
            when the GM awards PP
            then Hero.nova unspent powerPoints increase
        Player --> Spend Earned Power Points on Traits
            given awarded unspent PP
            when Hero.spendOn trait
            then ranks increase using the same cost formulas
        System --> Enforce Power Level Limits on Earned Spending
            given earned spend would break a limit pair
            when Hero.enforceLimitPair
            then the spend is rejected
        GM --> Raise Series Power Level
            given about 15 extra PP since last increase
            when the GM raises PowerLevel by 1
            then cap headroom increases
                and heroes may spend on formerly maxed traits
        Player --> Reallocate Power Points via Transformation
            given GM permission
            when the Player reallocates via transformation
            then trait ranks change
                and Hero.validateBalance still holds
~> Increment 1: PL, starting PP, spend, balance: Set Series Power Level, Spend Power Points on Trait Ranks, Validate Power Points Total Balance

Assign Abilities
    Configure Ability Scores
        Player --> Set Ability Rank
            given Hero.nova Ability.strength at 0
                and remaining powerPoints
            raise costs two points
                when Ability.setRank 1
                then Ability.purchasedRank is 1
                    and powerPoints decrease by 2
                    and Cascade Trait Changes on Ability Rank Alteration
            reduce below zero refunds two per rank
                when Ability.setRank -3
                then powerPoints increase by 6
            voluntary floor is minus five
                when Ability.setRank -5
                then Ability.purchasedRank is -5
            below minus five is rejected
                when Ability.setRank -6
                then Ability.purchasedRank is unchanged
                    and powerPoints are unchanged
        Player --> Designate Ability Rank Portion as Enhanced
            given Ability.agility purchasedRank 5
            partial enhanced keeps natural
                when the Player designates enhancedRank 3
                then naturalRank is 2
                    and total modifier is 5
            nullify removes only enhanced
                when Nullify targets the enhanced portion
                then naturalRank remains
        System --> Cascade Trait Changes on Ability Rank Alteration
            given Ability.agility changes
            dependents update in the same operation
                when Ability.cascadeDependents
                then linked Skill modifiers update
                    and Defense.dodge base updates
                    and attack modifiers from that ability update
                    but no extra powerPoints move
        System --> Enforce Ability Rank Ceiling per Power Level
            given PowerLevel 10
            when Ability.setRank would exceed the PL ceiling
            then the set is rejected
    Configure Derived Defenses
        System --> Derive Base Defense Rank from Ability
            given Ability.agility rank 4
            when Defense.dodge.deriveBase
            then Defense.dodge base equals Ability.agility rank
        Player --> Increase Defense Rank Above Ability Base
            given Defense.dodge base 4
            when Hero.spendOn Defense.dodge plus 2
            then purchasedAboveBase is 2
                and total Dodge rank is 6
        System --> Enforce Toughness Increase Restriction
            given Defense.toughness base from Stamina
            when the Player buys Toughness above that base
            then the purchase is rejected
        System --> Derive Initiative Modifier from Agility
            given Ability.agility rank 3
            when initiative modifier is derived
            then it includes Ability.agility rank
    Handle Absent Ability
        System --> Apply Absent Ability Capability Restrictions
            given an absent Ability
            no strength cannot exert force
                when Ability.strength is absent
                then Athletics and strength-based attacks auto-fail
            no stamina treats damage as an object
                when Ability.stamina is absent
                then there is no Fortitude defense
            absence is not rank minus five
                then the Ability is not debilitated from -5
        System --> Grant Bonus Power Points for Absent Ability
            when an Ability is absent
            then bonus powerPoints are granted for that absence
        GM --> Authorize Hero to Have Absent Ability
            given a Player requests absence
            when the GM has not authorized
            then the absence is not applied
            when the GM authorizes
            then Apply Absent Ability Capability Restrictions
    Handle Debilitated Ability
        System --> Apply Debilitated Ability Condition Effects
            given Ability rank drops below -5 from an effect
            str agl or dex collapse
                then defenseless plus immobile plus stunned
            stamina dying plus extra fortitude penalty
                then Condition.dying applies
            fighting dazed plus defenseless
                then close attacks are blocked
            int awe or pre unaware
                then unaware until rank recovers
        System --> Prevent Further Rank Reduction When Debilitated
            given Ability is debilitated
            when a further reduction is attempted
            then rank does not drop further
        System --> Clear Debilitated State When Ability Rank Recovers
            given Ability was below -5
            when rank returns to -5 or above
            then debilitated state clears

Manage Skills
    Configure Skill Ranks
        Player --> Assign Skill Ranks
            given Hero.nova remaining powerPoints
            two ranks per power point
                when Skill.assignRanks plus 2
                then Skill.purchasedRank increases by 2
                    and powerPoints decrease by 1
        System --> Enforce Skill Modifier Limit
            given PowerLevel 10
            total modifier cannot exceed pl plus ten
                given Skill rank plus Ability plus misc would exceed 20
                when the system enforces
                then the assignment is rejected
    Resolve Skill Checks
        Player --> Make Skill Check
            given Skill.perception with linked Ability.awareness
            success when total meets dc
                when Skill.makeCheck
                then total is d20 plus rank plus Ability plus circumstance
                    and CheckResult.isSuccess when total meets DifficultyClass
            trained only at rank zero fails without a roll
                given Skill.trainedOnly
                    and Skill.purchasedRank 0
                when Skill.makeCheck
                then CheckResult.isSuccess is false
                    but no d20 is rolled
        System --> Apply Critical Success on Natural 20
            given Skill.makeCheck with d20 face 20
            when Check.resolveGraded
            then degree of success increases by one after margin
        System --> Resolve Untrained Skill Attempt
            given Skill.purchasedRank 0
            untrained allowed uses ability only
                given Skill.trainedOnly is false
                when Skill.resolveUntrained
                then the check proceeds at rank 0 with Ability
            trained only auto-fails
                given Skill.trainedOnly is true
                when Skill.resolveUntrained
                then the attempt fails without a roll
        System --> Apply Skill Mastery Routine Result
            given Advantage.skillMastery on this Skill
            routine under pressure
                when the Player would be required to roll
                then RoutineCheck.resolve is allowed
        System --> Apply Circumstance Modifier to Skill Check
            given a minor or major circumstance
            when Skill.makeCheck
            then Check.circumstanceModifier is 2 or 5 in the named direction
    Use Interaction Skills
        System --> Enforce Interaction Skill Requirements
            given an interaction Skill
            unaware or non-comprehending subject
                then a -5 applies or the attempt is blocked
            intellect minus five
                then a -5 applies
            subject lacking mental abilities
                then the attempt is blocked
            immunity to interaction
                then the attempt is blocked
        Player --> Use Interaction Skill Against Target
            given interaction requirements pass
            deception intimidation persuasion or insight
                when Skill.makeCheck against the target
                then the named social or insight outcome is applied
                    and Feint makes the target Condition.vulnerable until end of the user's next turn
    Use Physical Skills
        Player --> Use Physical Skill
            given Skill.acrobatics or athletics or stealth
            when Skill.makeCheck
            then the physical outcome for that skill use is applied
        System --> Apply Fall Damage to Character
            given a fall Distance Rank
            when falling damage is applied
            then Toughness resistance uses the distance-derived Damage
    Use Combat Skills
        Player --> Add Close Combat Rank to Attack Check
            given Skill.closeCombat named for a weapon or power
            when an Attack is made with that subject
            then attackBonus includes Skill.closeCombat rank
                but other attacks are unchanged
        Player --> Add Ranged Combat Rank to Attack Check
            given Skill.rangedCombat named for a weapon or power
            when an Attack is made with that subject
            then attackBonus includes Skill.rangedCombat rank
    Use Manipulation Skills
        Player --> Use Manipulation Skill
            given Sleight of Hand Treatment Technology or Vehicles
            when Skill.makeCheck
            then the manipulation outcome is applied
                and jury-rig repair is DC 10 lower, one standard action, one problem, until end of scene
    Use Knowledge and Awareness Skills
        Player --> Use Knowledge Skill
            given Expertise Investigation or Perception
            when Skill.makeCheck
            then the knowledge or awareness outcome is applied
        GM --> Resolve Expert Knowledge Check Secretly
            when the GM makes the Expertise check
            then Hero.nova does not choose to attempt it
        GM --> Make Secret Perception Check for Character
            when the GM makes Skill.perception secretly
            then the Player does not declare the attempt

Select Advantages
    Acquire Advantage
        Player --> Purchase Advantage Rank
            given remaining powerPoints
            ranked advantage costs one per rank
                when Advantage.purchase rank 2
                then powerPoints decrease by 2
            non-ranked is once at rank 1
                when Advantage.purchase a non-ranked Advantage
                then powerPoints decrease by 1
                    but a second purchase of the same Advantage is rejected
        System --> Validate Power Point Cost for Advantage
            given the purchase cost
            when remaining powerPoints are insufficient
            then Advantage.purchase is rejected
        System --> Enforce Power Level Cap on Attack Advantage Bonus
            given Close Attack or Ranged Attack ranks
            when attackBonus plus those ranks would exceed the PL cap
            then the excess is not applied
        System --> Cap Luck Maximum Rank at Half Power Level
            given PowerLevel 10
            when Luck rank would exceed 5
            then the purchase is rejected
    Apply Combat Advantage
        Player --> Execute Attack Trade-Off Maneuver
            given Accurate All-out Defensive or Power Attack
            declare equal penalty and bonus up to five
                when AttackTradeOff.amount 3 is declared before the roll
                then the penalty stat drops by 3
                    and the bonus stat rises by 3
                    but neither side exceeds 5
        System --> Adjust Attack and Defense Values by Trade-Off Amount
            given a declared AttackTradeOff
            when the Attack resolves
            then attackBonus and defenses use the adjusted values
        System --> Apply Ranked Attack Bonus to Close or Ranged Attack Check
            given Advantage.closeAttack rank 2
            when a close Attack resolves
            then attackBonus includes 2
                but ranged Attacks are unchanged
        System --> Apply Initiative Bonus from Improved Initiative
            when ActionRound.rollInitiative
            then initiative modifier includes Improved Initiative rank
        System --> Apply Extended Critical Threat Range via Improved Critical
            given Improved Critical rank
            when Attack.confirmCritical
            then threat range is extended by that rank
        Player --> Declare Favored Environment Bonus Allocation
            when the Player declares Favored Environment this round
            then the allocation is recorded
        System --> Apply Favored Environment Circumstance Bonus
            given the declared environment matches
            when a qualifying check resolves
            then Check.circumstanceModifier includes the favored bonus
    Activate Fortune Advantage
        Player --> Re-Roll Die Using Luck Rank
            given Luck.usesThisSession remaining
            when Luck.reRoll
            then the die is re-rolled
                and usesThisSession decreases by 1
        System --> Enforce Luck Session-Use Limit and Refresh at Adventure Start
            given usesThisSession is 0
            when Luck.reRoll
            then the re-roll is rejected
            when a new adventure starts
            then Luck.refresh restores uses
        Player --> Inspire Allies with Hero Point
            when the Player spends a HeroPoint plus a standard action
            then allies gain the inspiration bonus
        System --> Apply Inspiration Bonus Ignoring Power Level Cap
            given inspiration is active
            then the bonus is not limited by PowerLevel
        Player --> Remove Ally Condition via Leadership
            given Hero.ally has a removable Condition
            when Leadership is used with a HeroPoint
            then that Condition is removed from Hero.ally
        Player --> Gain Temporary Skill Ranks via Beginner's Luck
            when Beginner's Luck is used with a HeroPoint
            then temporary Skill ranks are granted
    Use Skill Advantage
        Player --> Use Any Skill Untrained via Jack of All Trades
            given Jack of All Trades
                and a trained-only Skill at rank 0
            when Skill.makeCheck
            then Resolve Untrained Skill Attempt proceeds instead of auto-fail
        Player --> Make Routine Skill Check Under Pressure via Skill Mastery
            given Skill Mastery on the nominated Skill
            when the check is under pressure
            then RoutineCheck.resolve is allowed
        System --> Apply Favored Foe Circumstance Bonus to Qualifying Checks
            given the target is the favored foe
            when a qualifying check resolves
            then Check.circumstanceModifier includes 2
    Manage Character Resources
        Player --> Allocate Equipment Points to Gear
            given Equipment Advantage ranks
            when equipment points are allocated
            then Equip Hero Configure Equipment Pool
        Player --> Configure Minion Traits Within Power Point Budget
            given Minion Advantage
            when minion traits are set
            then minion PP stay within the minion budget
                and minion PowerLevel limits are enforced
        Player --> Configure Sidekick Traits Within Power Point Budget
            given Sidekick Advantage
            when sidekick traits are set
            then sidekick PP total is below the owner's total
        Player --> Propose Benefit to GM
            when the Player proposes a Benefit
            then the GM approves or rejects the definition
    Maintain Advantage State
        System --> Persist Advantage Selections on Character Sheet
            when Advantage.purchase completes
            then the Advantage remains on Hero.nova
        System --> Track Luck Rank Uses per Session
            when Luck.reRoll succeeds
            then usesThisSession is persisted
        System --> Refresh Luck Ranks at Start of Adventure
            when the adventure starts
            then Luck.refresh

Configure Powers
    Configure Attack Effect
        Player --> Select Attack Effect
            given remaining powerPoints
            affliction requires three conditions in degree order
                when the Player selects Affliction
                then Condition set has exactly three degrees
                    and resistance type is Fortitude or Will
                    but fewer than three conditions is rejected
            blast is damage plus ranged
                when the Player selects Blast
                then cost per rank is 2
                    and the attack check is ranged vs Dodge
        System --> Resolve Attack Effect Resistance Check
            given Effect.rank
            when the target Defense.performCheck DifficultyClass 10 plus Effect.rank
            then GradedCheckResult maps to the effect Condition set
                and Make Resistance Check Against Effect
        System --> Recover from Attack Effect Condition
            given Affliction conditions from this Effect
            when end of turn resistance succeeds
            then those Conditions are removed
    Configure Defense Effect
        Player --> Select Defense Effect
            when the Player selects Protection Immunity Regeneration or Immortality
            then the Effect uses that type's defaults
        System --> Apply Immunity Check Against Matching Power Descriptor
            given Immunity covering a descriptor
            when an incoming Effect descriptor matches
            then the Effect is ignored or halved for partial Immunity
        System --> Recover via Regeneration or Immortality
            given Regeneration
            when the recovery phase runs
            then Toughness penalty or Damage Condition is reduced
            given Immortality
            when the time rank 19 minus Immortality rank elapses
            then the character recovers from death
    Configure Mobility Effect
        Player --> Select Mobility Effect
            when the Player selects Flight Speed Burrowing Swimming Leaping Teleport or Movement
            then the Effect is configured with that mode
        System --> Calculate Movement Rank from Effect Rank
            when Flight or Burrowing or Leaping rank is applied
            then speed or jump Distance Rank is derived from Effect.rank
        System --> Validate Teleport Destination as Known or Accurately Sensed
            given Teleport
            when the destination is not known or sensed
            then Teleport is rejected
    Configure Sensory Effect
        Player --> Select Sensory Effect
            when the Player selects Senses Concealment Remote Sensing Mind Reading Communication or Comprehend
            then the Effect is configured
        System --> Grant Total Concealment Against Chosen Sense Type
            given Concealment for a sense
            then observers using that sense have total concealment
        System --> Resolve Mind Reading Opposed Check Against Will Defense
            when Mind Reading is used
            then an OpposedCheck vs Will resolves
                and success on the target's Will breaks contact
    Configure Control Effect
        Player --> Select Control Effect
            when the Player selects Create Move Object Environment Illusion Luck Control Summon or Transform
            then the Effect is configured
        System --> Enforce Created Object Volume and Toughness from Effect Rank
            given Create
            then volume and Toughness come from Effect.rank
        System --> Resolve Control Effect Check
            given Move Object Summon Illusion or Transform
            when the Effect resolves
            then the matching Strength Insight or Fortitude check runs
    Configure General Effect
        Player --> Select General Effect
            when the Player selects Variable Growth Shrinking Insubstantial Enhanced Trait Healing Elongation Quickness or Feature
            then the Effect is configured
        System --> Enforce Variable Pool Size as Rank Times Five Points
            given Variable
            then the pool is Effect.rank times 5
                and built effects still honor PowerLevel
        System --> Apply Healing Check and Remove Damage Condition from Most Severe
            when Healing resolves
            then the most severe Damage Condition is removed
                but the same target cannot be healed again this scene
    Apply Per-Rank Modifiers
        System --> Set Default Action Range Duration for Effect Type
            when an Effect type is selected
            then action range and duration defaults are set
        System --> Calculate Base Cost per Rank from Effect Definition
            when cost is calculated
            then baseCostPerRank comes from the Effect type
        Player --> Apply Per-Rank Extra or Flaw
            when Extra or Flaw is applied per rank
            then cost per rank rises or falls
        System --> Enforce Minimum One Point per Rank Floor After Flaws
            given flaws would drop cost below 1 per rank
            when cost is calculated
            then the floor is 1 PP per rank or fractional ranks
    Apply Flat Modifiers
        Player --> Apply Flat Extra or Flaw
            when Accurate Penetrating Activation Check Required Limited or Removable is applied
            then flat cost adjusts
        System --> Calculate Final Power Cost with Flat Modifier Adjustments
            when Power.cost is calculated
            then per-rank total plus flats is the cost
        System --> Enforce Minimum One Point Total Power Cost After Flat Flaws
            given flats would drop total below 1
            then Power.cost is at least 1
    Assign Power Descriptors
        Player --> Assign Descriptor to Power
            when origin source or result descriptor is assigned
            then Power.descriptors includes it
        System --> Match Power Descriptor Against Immunity or Nullify
            when an incoming Effect is compared
            then matching uses descriptor names
        GM --> Approve Descriptor Interaction Between Powers
            when descriptors are flexible
            then the GM is the final match
    Organize Power Arrays
        Player --> Build Power Array with Base Effect
            when Array.baseEffect is set
            then the array pool equals that effect's cost
        Player --> Add Alternate Effect to Array
            when an alternate's full cost is at or under the primary
            then it is added
                but a permanent Effect cannot be an alternate
        Player --> Switch Active Effect in Array as Free Action
            when Array.switchActive
            then only the chosen non-dynamic effect is available
        System --> Enforce Array Mutual Exclusivity Rule for Non-Dynamic Effects
            given a non-dynamic Array
            then sibling alternates are not usable together
            given a dynamic Array
            when Array.reallocate
            then combined allocation cannot exceed the pool

Equip Hero
    Configure Equipment Pool
        Player --> Acquire Equipment Advantage Ranks
            given Hero.nova
            rank 1 grants five equipment points
                when Equipment Advantage rank 1 is purchased
                then Equipment.equipmentPoints is 5
            zero ranks grant no points
                given Equipment Advantage rank 0
                then Equipment.equipmentPoints is 0
        System --> Derive Equipment Point Budget from Advantage Ranks
            given Equipment Advantage ranks
            when the budget is derived
            then Equipment.equipmentPoints matches all purchased ranks
        Player --> Pay Equipment Points for Item
            given remaining equipmentPoints
            when Equipment.payFor item
            then equipmentPoints decrease by the item cost
        System --> Enforce Equipment Point Budget Limit
            given remaining equipmentPoints below the item cost
            when Equipment.payFor item
            then the purchase is rejected
        System --> Enforce Equipment Bonus Non-stacking
            given two armor equipment bonuses
            when both are worn
            then only the higher equipment bonus applies
                but Protection from a Device stacks
        Player --> Build Alternate Equipment Array
            when alternate equipment is built
            then only one item in the array is active
    Acquire Weapons
        Player --> Select Weapon
            given melee ranged grenade or explosive
            when the Player selects the weapon
            then the item is in Equipment.items
        System --> Add Wielder Strength to Melee Damage
            given a Strength-based melee weapon
            when Damage is resolved
            then Damage rank includes wielder Strength
                but a chainsaw does not add Strength
        System --> Apply Area Weapon Effect
            given a grenade or explosive
            when it detonates
            then Burst or Cloud area uses Dodge DC
    Acquire Defensive Gear
        Player --> Select Armor or Shield
            when the Player selects armor or a shield
            then the item is in Equipment.items
        System --> Enforce Armor Bonus Non-stacking Rule
            given two armors
            then only the higher armor bonus applies
        System --> Cap Equipment Toughness at Power Level
            given equipment Toughness would exceed PowerLevel
            then the excess is not applied
    Acquire General Gear
        Player --> Purchase General Gear
            when communications surveillance transport or tools are purchased
            then Equipment.payFor item
        Player --> Build Utility Belt Array
            when a utility belt array is built
            then alternate-equipment exclusivity applies
    Build Device
        Player --> Designate Power as Removable Device
            when Removable or Easily Removable is applied
            then Device cost drops by the flaw
        System --> Calculate Reduced Cost from Removable Flaw
            given Removable Easily Removable and optional Indestructible
            when Device cost is calculated
            then the combined flaw math applies
        Player --> Build Specialized Device
            when battlesuit costume or enhanced equipment is built
            then Device powers are assigned
        System --> Remove Powers When Device Taken Away
            given the Device is taken away
            then those Power effects are unavailable
                and a permanently lost Device may be replaced
    Invent Temporary Device
        Player --> Define Invention Effect and Point Cost
            when the Player defines the invention
            then design DC comes from the PP cost
        Player --> Complete Construction Check
            when Skill.technology construction check succeeds
            then the invention exists
        Player --> Use Invention for One Scene
            when the invention is used
            then it lasts one scene
                and a HeroPoint reuses it
                and spending PP makes it permanent
        Player --> Jury-Rig Device by Spending Hero Point
            when a HeroPoint is spent to jury-rig
            then design is skipped
                and construction is compressed to rounds with a DC penalty
    Design Vehicle
        Player --> Select Vehicle Size Category
            when size is selected
            then base vehicle traits are derived from size
        System --> Derive Base Vehicle Traits from Size
            given a large size
            then a defense penalty applies
        Player --> Add Vehicle Feature or Power Effect
            when a feature or power effect is added
            then vehicle power effects cost one-fifth
    Design Headquarters
        Player --> Select Headquarters Size Category
            when size is selected
            then base Toughness is derived from size
        Player --> Add Headquarters Feature
            when a feature is added
            then feature power effects cost one-fifth
                and feature power effects cap at twice HQ PowerLevel
        System --> Allow Rebuild of Destroyed Headquarters
            given the HQ is destroyed
            then it may be rebuilt
    Build Construct
        Player --> Choose Construct Ability Profile
            given Minion Advantage for a construct
            when the profile is chosen
            then Stamina is none
                and Immunity to Fortitude is granted
        System --> Verify Zero Net Cost for Standard Construct Traits
            when standard construct traits are applied
            then net PP is 0
                but the package cannot be split
        Player --> Issue Order to Construct on Move Action
            when the Player issues an order
            then the Construct executes it
                and without a new order the last order continues

Conduct Combat
    Manage Turn Order
        System --> Roll Initiative Check
            given a Conflict begins
            when ActionRound.rollInitiative
            then each participant rolls d20 plus initiative modifier
                and Improved Initiative is included before the roll
        System --> Determine Turn Order from Initiative Results
            given all initiative results
            when turn order is built
            then Turn slots are descending initiative
                then Dodge then Agility on ties
                and the order persists for the conflict
            delay or ready updates only that participant
                when a Turn slot changes
                then other slots stay
        Player --> Delay Turn to Later Initiative Position
            when the Player delays
            then their Turn slot moves later
        Player --> Ready Action for Trigger Condition
            when the Player readies
            then the action waits for the trigger
                and taking it is a Reaction
    Manage Action Economy
        Player --> Take Standard Action on Turn
            given the Turn still has a standard action
            when the Player takes it
            then the standard action is consumed
        Player --> Take Move Action on Turn
            given the Turn still has a move action
            when the Player takes it
            then the move action is consumed
        Player --> Exchange Standard Action for Additional Move Action
            given a remaining standard action
            when it is exchanged
            then an extra move action is available
                but the standard action is gone
        Player --> Take Free Action During Turn
            when a free action is taken
            then it does not consume standard or move
                but Condition.stunned blocks even free actions
        Player --> Take Reaction Outside Turn
            when a trigger occurs off-turn
            then a Reaction may resolve
    Execute Attacks
        Player --> Make Attack Check Against Defense
            given a close or ranged Attack
            close targets Parry
                when Attack.resolve against Defense.parry
                then the check is d20 plus attackBonus vs Parry class
            ranged targets Dodge
                when Attack.resolve against Defense.dodge
                then distance penalty applies
        System --> Resolve Attack Check Against Defense Class
            given Attack vs defense class
            when the check resolves
            then a natural 1 is an automatic miss
                and Make Trait Check is not a second engine
        System --> Determine Critical Hit When Total Meets Defense
            given d20 face 20
            when rollTotal also meets defense class
            then Attack.confirmCritical is true
            given face 20 but total below defense class
            then it is a hit that is not a confirmed critical
        Player --> Apply Critical Hit Effect Choice
            given a confirmed critical
            when the Player chooses Increased Added or Alternate Effect
            then that option applies
                and minion Increased Effect bypasses extra
                and Alternate Effect does not cause ExtraEffort fatigue
        System --> Bypass Attack Check for Area or Perception Effect
            given an area or perception Effect
            when it is used
            then Attack.resolve is skipped
                but concealment and cover do not apply to an attack check
    Apply Aim and Charge
        Player --> Aim for Attack Bonus
            when the Player aims
            then attackBonus increases
                and Condition.vulnerable applies during the aim
        Player --> Execute Charge Attack with Penalty
            when the Player charges
            then the attack is made with the charge penalty
        Player --> Execute Slam Attack During Charge
            given a charge
            when slam is chosen
            then the attacker also makes a Toughness check
    Perform Combat Maneuvers
        Player --> Defend Against Incoming Attacks
            when the Player defends
            then active defenses increase and attacks against them are harder
        Player --> Execute Grab Attempt
            when grab is attempted
            then an attack check then grab resistance vs Strength or Dodge
                and maintain is a free action
                and damage on a later turn is a standard action
                and escape is Athletics or Acrobatics as a move action
        Player --> Execute Disarm Attempt
            when disarm is attempted
            then an opposed check resolves
                and the loser of a melee disarm may Counter-Disarm as a Reaction
        Player --> Execute Trip Attempt
            when trip is attempted
            then an opposed check resolves
                and the loser may Counter-Trip as a Reaction
        Player --> Execute Feint with Deception Check
            when Skill.deception feints
            then the target is Condition.vulnerable until end of the user's next turn
    Resolve Damage and Recovery
        System --> Resolve Toughness Resistance Check Against Damage
            given incoming Damage
            when Defense.toughness.performCheck
            then GradedCheckResult drives damage conditions
        System --> Apply Damage Condition by Degree of Failure
            given Toughness failure
            one degree is a cumulative Toughness penalty
                then no named Condition change
            two degrees is dazed plus penalty
            three degrees is staggered plus penalty
            four degrees is incapacitated
            minion any failure
                then the minion is defeated
        Player --> Recover from Damage in Conflict
            when Recover is taken once this conflict
            then a Damage Condition is improved
                and a plus 2 defense bonus applies
        System --> Resolve Ongoing Effect Resistance Check at End of Turn
            when the turn ends
            then success ends the Effect and its Conditions
                and failure leaves them
    Handle Tactical Environment
        System --> Apply Concealment or Cover Penalty to Attack Check
            given concealment or cover
            when Attack.resolve
            then attackBonus is penalized
                and cover also bonuses Dodge vs area
        GM --> Apply Surprise Round Rules
            when surprise applies
            then surprised characters are Condition.surprised
        Player --> Execute Team Attack with Coordinated Attackers
            when multiple attackers hit
            then the team-attack bonus is applied from combined hits
    Handle Hazards and Objects
        System --> Apply Falling Damage by Distance Rank
            given a fall Distance Rank
            when falling damage is applied
            then Toughness resists that Damage
        System --> Apply Suffocation Sequence
            when suffocation continues
            then the suffocation Condition sequence advances
        Player --> Attack or Smash Object
            when an object is attacked
            then object Toughness including Material Toughness is checked
    Use Hero Resources
        Player --> Spend Hero Point
            re-roll treats 1-10 as 11
                when HeroPoint.spend for a re-roll
                then a result of 1 through 10 becomes 11
                    but it must be spent before the GM announces the outcome
            recover a condition immediately
                when HeroPoint.spend to recover
                then the named Condition is removed
            heroic feat
                when HeroPoint.spend for a feat
                then the Advantage is gained this action
                    but fortune Advantages are excluded
            edit scene or instant counter
                when HeroPoint.spend
                then the named scene or counter outcome applies
        Player --> Declare Extra Effort for Combat Benefit
            given ExtraEffort not yet used this turn
            when ExtraEffort.declareBenefit
            then the chosen combat benefit applies
                and fatigue is pending
        Player --> Activate Power Stunt via Extra Effort
            given an existing non-permanent Power
            when ExtraEffort activates a stunt
            then the stunt lasts until end of scene
        System --> Apply Extra Effort Fatigue at Start of Next Turn
            given ExtraEffort was declared
            when the next Turn starts
            then fatigue is applied
            given a HeroPoint spent at the start of that turn
            then the fatigue is removed

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
