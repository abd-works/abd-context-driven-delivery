# Story Map — MM3E Online Holistic [Skill Module]

Pass 2 (Level 2 — full decomposition) of the Manage Skills epic.
Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).

---

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

## Consolidation Notes (for AC phase)

### Assign Skill Ranks
Skill rank purchase follows a fixed 2-ranks-per-PP rate. Ranks may be split freely across any skills. The skill modifier limit (total skill modifier capped at PL + 10) is enforced at build time by Character Construction, not at check time — AC should cover the rank assignment mechanics only, not the limit calculation.

### Enforce Skill Modifier Limit
This is a system enforcement at character construction/advancement time — total skill modifier (rank + ability + misc) may not exceed PL + 10 for any skill. The limit interacts with trade-offs in Character Construction; here it is simply the upper-bound check. AC must specify: what is the total modifier, what is the limit, and what happens if the limit is exceeded.

### Make Skill Check
This is the core resolution story — parameterized across all 16 named skills. AC should cover: formula (d20 + rank + ability + circumstance), DC comparison, success/failure. The per-skill stories (Bluff, Climb, Hide, etc.) specify skill-specific DCs and outcomes. Do not duplicate the core formula in every per-skill story.

### Apply Critical Success on Natural 20
Distinct from degree-of-success arithmetic: a natural 20 triggers a degree increase after normal calculation. AC must specify: when does a natural 20 apply (on any skill check), what happens to the degree, and what is the edge case (already at highest degree).

### Resolve Untrained Skill Attempt
Two distinct behaviors: (1) skills without Trained Only marker — attempt proceeds with rank 0, ability modifier applies; (2) Trained Only skills — attempt automatically fails with no roll. AC must cover both paths.

### Apply Skill Mastery Routine Result
Skill Mastery allows routine check result (bonus + 10) even under stress. AC must specify: which skill is nominated, what is the routine result, when does it apply (replaces a roll the character would otherwise be required to make).

### Enforce Interaction Skill Requirements
Covers the three system-enforced gates before any interaction skill resolves: (1) subject awareness and comprehension (-5 if not met), (2) Intellect minimum (-5 for Int -5, blocked for subjects lacking mental abilities), (3) Immunity power effect (blocked entirely). These are pre-conditions shared by all three interaction skills; AC should use a parameterized structure.

### Feint Opponent with Deception
Distinct from Bluffing — feinting is a combat action (standard action), makes the target vulnerable, and resolves in one round. Bluffing is a social action that changes NPC behavior persistently. AC must cover the vulnerability condition duration (until end of user's next round).

### Intimidate Group of Minions
Distinct from single-target Coerce — uses a single check against a single GM-rolled group resistance; the effect must be identical for all members. AC must cover: same-effect requirement, single-resistance roll, minion definition.

### Detect Illusion Secretly with Insight
GM makes this check on behalf of the character — the player does not decide when to attempt it. Distinct from Detect Outside Influence (which is player-initiated). AC must cover: secret roll, DC (10 + Illusion rank), outcome (success reveals illusion flaw).

### Collect Physical Evidence vs. Analyze Collected Evidence
Two-step process: Gather Evidence (DC 15 check to collect without ruining it) must succeed before Analyze Evidence (DC 15 check to extract information). Failure to gather properly degrades analysis or makes it impossible. AC must cover both steps and their interaction.

### Add Close Combat Rank to Attack Check / Add Ranged Combat Rank to Attack Check
Both follow the same narrow pattern: rank adds only to attack checks for the specific weapon/power named by the skill, not to any other attack, not to defense. These can be written with parallel AC structure. Distinguish from advantage-based bonuses (Close Attack, Ranged Attack) which apply more broadly.

### Perform Jury-Rig Repair
Distinct from standard Repair: DC is 10 lower than building (not just 5 lower), takes a standard action (not hours), fixes only one problem, and lasts only until end of scene. Item cannot be jury-rigged again until fully repaired. AC must cover all four constraints.

### Revive Dazed or Stunned Character
Distinct from Stabilize: removes dazed or stunned conditions (not dying), takes a standard action, leaves other conditions intact. Cannot awaken a dying character without stabilizing first. AC must cover the condition-specificity and the dying character limitation.

## Context Gaps

- **Skill Mastery full definition**: The Skill Mastery advantage definition lives in the Advantages chapter, not Chapter 4. Source chunks confirm it allows routine check results even under stress but do not specify all edge cases (e.g., when exactly a roll is "required" vs. voluntary).
- **Technology Inventing**: The Inventing use of Technology (with Inventor advantage) references page 211 of the source, outside these chunks. The story "Build Technological Item" covers standard building; Inventing creates temporary devices with advantages/powers but the mechanics are not in scope here.
- **Vehicles animal-mount gap**: The Vehicles skill explicitly excludes animal mounts; Expertise: Riding is the correct skill. The GM may allow Athletics with a circumstance penalty. This decision is GM-adjudicated and not source-specified further.
- **Interaction skill group use mechanics**: The source states the GM decides if group use is effective and may apply modifiers depending on the situation; specific group resistance mechanics are not fully specified beyond the minion example.
- **Perception sense types**: All sense types defined in the Powers chapter are valid for Perception checks; the detailed list and modifiers are out of scope here.
