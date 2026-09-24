# Story Map — MM3E [Combat] Module (Pass 2)

Actors: **Player** (human playing a hero), **GM** (Gamemaster), **System** (rules engine / application).
Module: deepens the `(E) Conduct Combat` epic from the holistic story map to full Pass 2 decomposition.

---

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

---

## Consolidation Notes (for AC phase)

### Execute Attacks
`Make Close Attack Check Against Parry` and `Make Ranged Attack Check Against Dodge` share the same resolution formula (d20 + attack bonus vs. defense class) but differ in which defense is targeted and what range penalties apply. AC must specify both separately with range-penalty details for ranged and the parry-target rule for close.

`Detect Natural 20 as Potential Critical Hit` and `Determine Critical Hit When Total Meets Defense` are two distinct steps in the critical hit determination. AC must specify the two-step check: roll = 20 → automatic hit + threat check → total ≥ defense class → confirmed critical.

`Apply Critical Hit Effect Choice` covers three mutually exclusive options (Increased Effect, Added Effect, Alternate Effect). AC must specify each option separately including the minion bypass rule for Increased Effect and the no-fatigue rule for Alternate Effect.

`Bypass Attack Check for Area or Perception Effect` negates all attack-check modifiers (concealment, cover, maneuvers, aim bonus). AC must confirm that area and perception effects automatically hit and cannot crit or miss.

### Perform Combat Maneuvers
`Execute Grab Attempt` and `Resolve Grab Resistance Check` are sequential — AC for the grab story must cover both the attack check and the resistance check against Strength or Dodge.

`Maintain Grab Hold as Free Action` and `Damage Grabbed Target on Subsequent Turn` are separate stories with separate AC: maintaining a hold (free action, attacker hindered+vulnerable) vs. choosing to deal damage (standard action, only after hold established on a prior turn).

`Escape from Grab` uses Athletics or Acrobatics vs. routine check result of opponent's Strength or grab rank — this is a move action, separate AC needed to distinguish from the grab's resistance check.

`Counter-Disarm as Reaction` and `Counter-Trip as Reaction` only trigger when specific conditions are met (melee disarm lost; trip check lost) — AC must specify the triggering precondition.

### Resolve Damage and Recovery
`Apply Damage Condition by Degree of Failure` covers four degrees with different outcomes:
- 1 degree: −1 cumulative Toughness penalty (no condition change)
- 2 degrees: dazed + −1 penalty
- 3 degrees: staggered + −1 penalty (if already staggered → 4th degree)
- 4 degrees: incapacitated

`Recover from Damage in Conflict` (standard action, once per conflict) vs. `Remove Damage Condition After Rest` (automatic, 1 condition per minute) are distinct recovery paths. AC must specify once-per-conflict constraint and the +2 defense bonus granted by Recover action.

`Resolve Ongoing Effect Resistance Check at End of Turn` is automatic — no action required. AC must specify that success ends the effect and removes its conditions; failure leaves conditions in place.

### Use Hero Resources
`Spend Hero Point to Re-Roll Die` has the special floor rule: re-roll of 1–10 adds 10, making the floor 11. AC must specify the must-spend-before-GM-announces constraint.

`Spend Hero Point for Heroic Feat Advantage` excludes fortune advantages and requires meeting prerequisites. AC must specify these constraints.

`Declare Extra Effort for Combat Benefit` covers eight benefit options — AC must specify each as a distinct variant with the once-per-turn constraint and the fatigue cost.

`Activate Power Stunt via Extra Effort` requires an existing power as the base; permanent effects excluded; lasts until end of scene. AC must specify the base-power requirement and scene-duration rule.

`Spend Hero Point to Remove Extra Effort Fatigue` must be spent at the START of the turn after extra effort — not immediately after. AC must specify the timing constraint.

---

## Context Gaps

- Maneuver interaction with power effects: when a power effect duplicates a maneuver (e.g., a Snare effect that restrains like a grab), the interaction between the power effect's resistance check and the maneuver's resolution chain is not fully specified in the source. Flag for AC phase.
- Area effect concealment/cover interaction: source states area/perception effects bypass attack checks, but the cover bonus to Dodge resistance checks against area effects (equal to cover penalty to attacks) introduces a residual concealment question — does concealment from dim light also grant any Dodge bonus vs. area effects? Source does not specify.
- Finishing Attack against defenseless targets: the Finishing Attack maneuver (routine check or normal check for auto-crit) is referenced in the feint/defending objects chunks but not listed as its own story; it is implicit in attacking defenseless targets. AC phase should cover it under `Attack or Smash Object` and `Defend` stories.
- Recover action and extra effort interaction: a character can use extra effort to gain an additional resistance check (separate from the Recover action's additional check); whether both can be used in the same turn is not explicitly stated. Assumed yes — extra effort is a free action before or after the Recover action.
- Initiative for characters with the same Dodge and Agility after two tie-breaker steps: source says "each tied player should roll a die" but an application must decide how to handle GM-controlled NPCs in this scenario.
