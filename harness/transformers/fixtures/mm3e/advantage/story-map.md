# Story Map — MM3E Advantage Module (Pass 2)

Deepens `(E) Select Advantages` from the project-level breadth pass to full Level 2 decomposition.
Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).

---

(E) Select Advantages
    (E) Configure Advantage Purchases
        (S) Player --> Purchase Advantage Rank with Power Points
        (S) System --> Enforce Advantage Rank Maximum
        (S) System --> Enforce Power Level Cap on Attack Bonus Advantage
        (S) Player --> Assign Advantage Parameter on Selection
        (S) System --> Persist Advantage Configuration to Character Record
    (E) Apply Attack Trade-off
        (S) Player --> Declare Accurate Attack Trade-off Amount
        (S) Player --> Declare All-out Attack Trade-off Amount
        (S) Player --> Declare Defensive Attack Trade-off Amount
        (S) Player --> Declare Power Attack Trade-off Amount
        (S) System --> Apply Symmetric Trade-off Penalty and Bonus to Attack
    (E) Activate Combat Enhancement
        (S) System --> Apply Improved Initiative Bonus to Initiative Roll
        (S) System --> Evaluate Attack Roll Against Improved Critical Threat Range
        (S) System --> Apply Close Attack Bonus to Close Attack Roll
        (S) System --> Apply Ranged Attack Bonus to Ranged Attack Roll
        (S) Player --> Declare Favored Environment Attack or Defense Bonus
        (S) System --> Apply Favored Environment Circumstance Bonus
    (E) Activate Fortune Effect
        (S) Player --> Re-roll Die Using Luck Rank
        (S) System --> Track Luck Uses Against Session Rank Limit
        (S) System --> Refresh Luck Uses at Adventure Start
        (S) Player --> Spend Hero Point to Inspire Allies
        (S) System --> Apply Inspire Circumstance Bonus to Ally Checks
        (S) Player --> Spend Hero Point to Remove Ally Condition via Leadership
        (S) Player --> Spend Hero Point to Gain Temporary Skill Ranks via Beginner's Luck
        (S) System --> Expire Temporary Skill Ranks at Scene End
    (E) Manage Character Asset
        (S) Player --> Allocate Equipment Points to Gear Items
        (S) System --> Enforce Equipment Point Limit at Rank Times Five
        (S) Player --> Build Minion Character with Rank Times Fifteen Power Points
        (S) System --> Enforce Minion Power Level Limits and Hierarchy Rules
        (S) Player --> Build Sidekick Character with Rank Times Five Power Points
        (S) System --> Enforce Sidekick Point Ceiling Below Owner Total
        (S) Player --> Define Benefit Perquisite with GM Approval
        (S) System --> Validate Benefit Value Does Not Exceed One-Point Threshold
    (E) Apply Skill Enhancement
        (S) Player --> Make Routine Skill Check Under Pressure via Skill Mastery
        (S) System --> Override Routine Check Restriction for Skill Mastery Skill
        (S) Player --> Attempt Untrained Skill Check via Jack of all Trades
        (S) Player --> Apply Favored Foe Bonus to Interaction and Perception Checks
        (S) System --> Apply Favored Foe Circumstance Bonus to Applicable Skill Checks

---

## Consolidation Notes (for AC phase)

### Apply Attack Trade-off (Accurate Attack, All-out Attack, Defensive Attack, Power Attack)
Groups four advantages that share the symmetric exchange mechanic (-N to stat A, +N to stat B, max 5 each direction) into one system story and four distinct player stories. The player stories are distinct because the traded stat pairs differ per variant.

AC must specify per variant:
- Accurate Attack: effect modifier penalty (up to -5), attack bonus gain (up to +5); effect modifier may not go below base
- All-out Attack: active defenses (both Dodge and Parry) penalty (up to -5 each), attack bonus gain (up to +5); defenses reduced toward zero
- Defensive Attack: attack bonus penalty (up to -5), active defenses (both Dodge and Parry) gain (up to +5 each)
- Power Attack: attack bonus penalty (up to -5), effect bonus gain (up to +5)
- System enforcement: penalty amount must equal bonus amount; neither may exceed 5; both adjustments must be applied together

### Apply Symmetric Trade-off Penalty and Bonus to Attack
A single system story handles enforcement logic for all four trade-off advantages — the formula is identical (symmetric -N/+N, max 5) regardless of which stat pair is traded.

AC must specify:
- The system receives the declared trade-off amount N and the variant type
- The system applies -N to the source stat and +N to the target stat for that attack only
- If N > 5 or N < 1, the system rejects the declaration
- Trade-off applies to the single attack action; it does not persist to subsequent attacks

### Activate Fortune Effect (Luck, Inspire, Leadership, Beginner's Luck)
Four fortune advantages share the same activation pattern (consume hero point or fortune-equivalent resource → produce defined benefit) but each produces a distinct benefit type:
- Luck: die re-roll (rank-limited; no HP cost; refreshes at adventure start)
- Inspire: +1/rank circumstance bonus to all ally checks for one round; requires HP spend; once per scene; does not stack
- Leadership: removes one condition (dazed, fatigued, or stunned) from one ally; requires HP spend; standard action
- Beginner's Luck: 5 temporary ranks in chosen skill (≤4 ranks currently); requires HP spend; expires at scene end

AC must specify the activation trigger, resource cost, beneficiary, effect duration, and expiry condition for each variant.

### Manage Character Asset (Equipment, Minion, Sidekick, Benefit)
Four general advantages all grant access to an external resource but with distinct point formulas and constraint rules.

AC must specify per variant:
- Equipment: 5 points × rank available; spending tracked against total; points allocate to gear items
- Minion: rank × 15 PP creates independent follower; no minions of own; no hero points; replaced if lost
- Sidekick: rank × 5 PP creates NPC partner; PP total must be less than owner's total; not subject to minion rules; owner can spend own HP on sidekick's behalf
- Benefit: no point allocation; value must not exceed 1-PP power effect equivalent; GM must approve; can have ranks for improved versions of same benefit

## Context Gaps

- Whether the full MM3E advantage list (33+ advantages in source) is in scope for the tool or only the 26 Core terms from the partition are selectable. The partition names 26 advantages; the source chunks describe additional advantages (Chokehold, Defensive Roll, Evasion, Fast Grab, Grabbing Finesse, Improved Defense, etc.) not included as Core terms.
- Whether Minion and Sidekick character sheets are built within the online tool or treated as references to external character records. If built in-tool, a full character creation flow is needed for dependents.
- Whether Fighting Style combinations (source describes Boxing, Judo, Kung Fu, Sword-fighting, Wrestling as pre-defined advantage sets) are selectable as packages in the tool, or whether players always select advantages individually.
- Whether advantage use during play (applying trade-offs, activating fortune effects, declaring favored environments) is managed by the tool's combat/session tracker or whether only character-creation configuration is in scope for this module.
