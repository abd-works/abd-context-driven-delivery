# Acceptance Criteria — MM3E Online Holistic [Skill Module]

Pass 2 story map — covers all stories in docs/skill/story-map.md.
Actors: **Player** (human building/playing a hero), **GM** (Gamemaster), **System** (rules engine / application).

---

## Epic: Manage Skills

---

### Sub-Epic: Configure Skill Ranks

---

## Story: Assign Skill Ranks

**Story type:** user

### Domain terms

- *Skill Rank* — numeric investment in a skill; bonus added to skill checks
- *Power Point (PP)* — character-building currency; 1 PP buys 2 skill ranks
- *Trained Status* — active when rank ≥ 1; gates Trained Only skills
- *Skill Modifier Limit* — maximum total modifier = PL + 10; enforced at build time

### Acceptance criteria

1. **WHEN** *Player* allocates skill ranks during character creation or advancement  
   **THEN** the system records each rank against the nominated skill  
   **AND** deducts 1 *Power Point* per 2 ranks allocated  
   **AND** activates *Trained Status* on any skill that receives at least 1 rank  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — "Ch4 Skills" skill-rank definition, lines 2689–2735

2. **WHEN** *Player* splits 1 PP across two skills (1 rank each)  
   **THEN** both skills receive exactly 1 rank  
   **AND** both skills gain *Trained Status*  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

3. **WHEN** *Player* attempts to assign ranks that would bring any skill's total modifier above PL + 10  
   **THEN** the system blocks the assignment  
   **AND** shows the current modifier and the limit for that skill  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735; HeroesHandbook-rules__chunk_024.md — PL limits

4. **WHEN** *Player* leaves a skill at 0 ranks  
   **THEN** the skill remains untrained  
   **AND** the ability modifier still applies to any check for that skill (if not Trained Only)  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — "Skill Basics" untrained description, lines 2736–2796

5. **BUT** allocating ranks to one skill does not automatically reduce ranks on another skill  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

---

## Story: Enforce Skill Modifier Limit

**Story type:** system

### Domain terms

- *Skill Modifier Limit* — total skill modifier (rank + ability + misc) may not exceed PL + 10
- *Power Level (PL)* — GM-set campaign power ceiling
- *Circumstance Modifier* — situational bonus or penalty applied at check time, not build time

### Acceptance criteria

1. **WHEN** any skill's total modifier reaches PL + 10 + 1  
   **THEN** the system rejects further rank allocation to that skill  
   **AND** reports the current total and the limit  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

2. **WHEN** GM increases campaign PL  
   **THEN** the system recalculates the limit (new PL + 10) for every skill  
   **AND** unlocks previously capped rank allocations  
   **Evidence:** HeroesHandbook-rules__chunk_024.md — "Gamemaster Approval" PL scope, lines 1650–1767

3. **WHEN** a circumstance bonus temporarily pushes a check total above the limit  
   **THEN** the system applies it for that single check  
   **BUT** does not alter the recorded skill rank or the stored modifier  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

4. **BUT** the limit applies per-skill independently — it is not a cumulative cap across all skills  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

---

### Sub-Epic: Resolve Skill Checks

---

## Story: Make Skill Check

**Story type:** user

### Domain terms

- *Skill Check* — d20 + skill rank + ability modifier + circumstance modifiers vs DC
- *d20 Roll* — the die result before modifiers
- *Difficulty Class (DC)* — threshold set by GM or rule; equal or above = success
- *Degree of Success* — (total − DC) ÷ 5 rounded down, min 0
- *Degree of Failure* — (DC − total) ÷ 5 rounded down, min 0

### Acceptance criteria

1. **WHEN** *Player* declares a skill use and the GM sets (or rules specify) a DC  
   **THEN** the system computes total = d20 + skill rank + ability modifier + circumstance modifiers  
   **AND** compares to the DC  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735; HeroesHandbook-rules__chunk_042.md — lines 2736–2796

2. **WHEN** total equals or exceeds DC  
   **THEN** the system records success  
   **AND** calculates *Degree of Success* = (total − DC) ÷ 5 (integer division, minimum 0)  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

3. **WHEN** total falls below DC  
   **THEN** the system records failure  
   **AND** calculates *Degree of Failure* = (DC − total) ÷ 5 (integer division, minimum 0)  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

4. **WHEN** the skill is Trained Only and *Player* has rank 0  
   **THEN** the attempt automatically fails  
   **AND** no d20 is rolled  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

5. **BUT** a single DC applies to the entire check — the system does not split the check against multiple DCs simultaneously  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

---

## Story: Apply Critical Success on Natural 20

**Story type:** system

### Domain terms

- *Natural 20* — the d20 die face showing 20, before modifiers
- *Critical Success* — degree increase of +1 applied after normal degree calculation
- *Degree of Success* — graded result measuring how well the check succeeded

### Acceptance criteria

1. **WHEN** the d20 result is exactly 20 (natural 20)  
   **THEN** the system calculates the normal degree result first  
   **AND** then increases that degree by one (critical success)  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

2. **WHEN** a natural 20 occurs on a check that would already be maximum degree  
   **THEN** the system keeps the degree at the maximum defined for that skill  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

3. **WHEN** a natural 20 occurs on a check that fails (total < DC)  
   **THEN** the system applies the degree-increase after failure calculation  
   **AND** may convert the result from a failure to a success if the degree boost crosses zero  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

4. **BUT** a natural 20 is not an automatic success regardless of degree — degree math still runs first  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

---

## Story: Resolve Untrained Skill Attempt

**Story type:** system

### Domain terms

- *Trained Only* — skill flag; rank 0 = automatic failure
- *Untrained* — character has rank 0 in the skill
- *Ability Modifier* — always applies, even at rank 0

### Acceptance criteria

1. **WHEN** *Player* attempts a Trained Only skill with rank 0  
   **THEN** the system automatically fails the attempt  
   **AND** no roll is made  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

2. **WHEN** *Player* attempts a skill without the Trained Only flag with rank 0  
   **THEN** the system computes total = d20 + 0 + ability modifier + circumstance modifiers  
   **AND** resolves normally against the DC  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

3. **WHEN** a skill has distinct trained and untrained aspects  
   **THEN** untrained characters may attempt only the explicitly listed untrained aspects  
   **AND** the system blocks attempts at trained-only aspects of that skill  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

4. **BUT** the automatic failure for Trained Only does not reduce the character to a -5 or "attempt at penalty" result — it is a hard block  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

---

## Story: Apply Skill Mastery Routine Result

**Story type:** system

### Domain terms

- *Skill Mastery* — advantage granting routine check result without rolling
- *Routine Check Result* — skill modifier + 10
- *Nominated Skill* — the specific skill the Skill Mastery advantage is assigned to
- *Stress* — conditions (combat, pressure) that would otherwise require a roll

### Acceptance criteria

1. **WHEN** *Player* has Skill Mastery for a specific skill and attempts a check for that skill under stress  
   **THEN** the system returns routine check result (skill modifier + 10) without rolling  
   **Evidence:** HeroesHandbook-rules__chunk_043.md — lines 2797–2849 (skill benchmarks and Skill Mastery reference)

2. **WHEN** Skill Mastery applies  
   **THEN** the routine result is final; no roll is permitted to improve it  
   **Evidence:** HeroesHandbook-rules__chunk_043.md — lines 2797–2849

3. **WHEN** the Skill Mastery skill would require a check in combat  
   **THEN** Skill Mastery applies and the character need not roll  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826 (Stealth + Skill Mastery example)

4. **BUT** Skill Mastery does not apply to skills other than the specifically nominated one  
   **Evidence:** HeroesHandbook-rules__chunk_043.md — lines 2797–2849

5. **BUT** the routine result still uses the capped skill modifier (PL + 10 limit) — Skill Mastery does not bypass the modifier limit  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

---

## Story: Apply Circumstance Modifier to Skill Check

**Story type:** system

### Domain terms

- *Circumstance Modifier* — situational bonus (+) or penalty (−) added to a skill check
- *Circumstance Bonus* — favorable condition; adds to modifier
- *Circumstance Penalty* — unfavorable condition; reduces modifier
- *Requires Tools* — skill flag; lacking tools applies −5

### Acceptance criteria

1. **WHEN** a favorable condition applies at the time of a skill check  
   **THEN** the system adds the circumstance bonus to the check total before comparing to the DC  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

2. **WHEN** required tools are absent for a Requires Tools skill  
   **THEN** the system applies a −5 circumstance penalty to the check  
   **Evidence:** HeroesHandbook-rules__chunk_043.md — lines 2797–2849 (Manipulation Skills, Requires Tools)

3. **WHEN** multiple circumstance modifiers apply simultaneously  
   **THEN** all stack additively into the check total  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

4. **BUT** circumstance modifiers at check time do not permanently alter the skill rank or ability modifier  
   **Evidence:** HeroesHandbook-rules__chunk_041.md — lines 2689–2735

---

### Sub-Epic: Use Interaction Skills

---

## Story: Enforce Interaction Skill Requirements

**Story type:** system

### Domain terms

- *Interaction Skill* — social-influence skill category (Deception, Intimidation, Persuasion, Insight)
- *Subject Awareness* — target must be aware of and able to understand the user
- *Intellect Rank* — measure of mental capacity; subjects with rank −5 impose penalty; absent rank = blocked
- *Immunity (power effect)* — renders target immune to interaction skills

### Acceptance criteria

1. **WHEN** *Player* attempts an interaction skill on a subject who cannot hear or understand  
   **THEN** the system applies a −5 circumstance penalty to the check  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

2. **WHEN** the target has Intellect rank −5  
   **THEN** the system applies a −5 circumstance penalty to the check  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

3. **WHEN** the target lacks any mental abilities  
   **THEN** the system blocks the interaction skill attempt entirely  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

4. **WHEN** the target has the Immunity power effect active against interaction skills  
   **THEN** the system blocks the attempt entirely  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

5. **WHEN** *Player* targets a group with one interaction skill check  
   **THEN** the result applies uniformly to all group members  
   **BUT** the system does not permit different results for different members in the same check  
   **Evidence:** HeroesHandbook-rules__chunk_042.md — lines 2736–2796

---

## Story: Bluff Target with Deception

**Story type:** user

### Domain terms

- *Bluff* — Deception use to make a false statement believable
- *Believability Modifier* — circumstance modifier from −5 (target wants to believe) to +20 (outrageous claim)
- *Standard Action* — default time cost; or move action at −5

### Acceptance criteria

1. **WHEN** *Player* bluffs a target using Deception  
   **THEN** the system resolves Deception check opposed by target's Deception or Insight (whichever is higher)  
   **AND** applies believability circumstance modifier before the comparison  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

2. **WHEN** the Deception check result exceeds the target's resistance  
   **THEN** the target believes the false statement for the purposes of the scene  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

3. **WHEN** *Player* bluffs as a move action instead of a standard action  
   **THEN** the system applies an additional −5 circumstance penalty to Deception  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

4. **WHEN** the Deception check fails  
   **THEN** the target is not deceived  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

5. **BUT** bluff effects do not persist beyond the scene unless the GM rules the target has integrated the belief  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

---

## Story: Create Disguise with Deception

**Story type:** user

### Domain terms

- *Disguise* — Deception use to impersonate a person or disguise appearance
- *Disguise Check Result* — becomes the DC observers must beat with Perception
- *Observer Bonus* — Perception bonus for associates (+2 regular, +5 friend, +10 intimate)

### Acceptance criteria

1. **WHEN** *Player* creates a disguise using Deception  
   **THEN** the check result becomes the DC observers must beat with Perception to see through it  
   **AND** the GM makes the observation check secretly  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225; HeroesHandbook-rules__chunk_050.md — lines 3226–3283

2. **WHEN** an observer is a regular associate of the impersonated person  
   **THEN** the observer gains +2 to Perception when checking the disguise  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

3. **WHEN** an observer is a close friend of the impersonated person  
   **THEN** the observer gains +5 to Perception  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

4. **WHEN** an observer is intimate with the impersonated person  
   **THEN** the observer gains +10 to Perception  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

5. **BUT** the Perception roll against the disguise is made secretly by the GM — the player does not know if their disguise was seen through unless behavior changes  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

---

## Story: Feint Opponent with Deception

**Story type:** user

### Domain terms

- *Feint* — Deception use to make an opponent vulnerable in combat
- *Vulnerable Condition* — target is at a disadvantage until end of user's next round
- *Standard Action* — time cost for feinting in combat

### Acceptance criteria

1. **WHEN** *Player* feints using Deception (standard action in combat)  
   **THEN** the system resolves Deception check opposed by target's Deception or Insight  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

2. **WHEN** the Deception check succeeds  
   **THEN** the target gains the *Vulnerable Condition* against the user's next attack  
   **AND** the vulnerable condition expires at the end of the user's next round  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

3. **WHEN** the feint check fails by more than one degree  
   **THEN** the user gains the *Vulnerable Condition* instead (exposed by the failed attempt)  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

4. **BUT** feinting does not replace the attack — it only sets up the vulnerability for the next attack roll  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

---

## Story: Send Innuendo Message with Deception

**Story type:** user

### Domain terms

- *Innuendo* — Deception use to embed a hidden message in apparent normal conversation
- *Innuendo DC* — 10 (basic), 15 (complex), 20 (new information)
- *Recipient Insight Check* — required to interpret the message at the same DC

### Acceptance criteria

1. **WHEN** *Player* sends innuendo using Deception  
   **THEN** the system requires a Deception check against the Innuendo DC (10/15/20 by complexity)  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

2. **WHEN** the Deception check succeeds  
   **THEN** the intended recipient must make an Insight check at the same DC to understand the message  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

3. **WHEN** the Deception check fails by more than one degree  
   **THEN** the message is misinterpreted — the sender communicated something unintended  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

4. **WHEN** the recipient's Insight check fails by more than one degree  
   **THEN** the recipient misunderstands the hidden message  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

5. **BUT** observers not targeted by the innuendo cannot attempt an Insight check to interpret it  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

---

## Story: Trick Target into Danger with Deception

**Story type:** user

### Domain terms

- *Trick* — Deception use to mislead a target into a dangerous or disadvantageous action
- *Opposed Check* — Deception vs target's Deception or Insight
- *Vulnerable Condition* — penalty on the user if the trick fails badly

### Acceptance criteria

1. **WHEN** *Player* tricks a target using Deception  
   **THEN** the system resolves Deception opposed by target's Deception or Insight  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

2. **WHEN** the Deception check succeeds  
   **THEN** the target acts on the misleading information, taking the action the user intended  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

3. **WHEN** the Deception check fails by more than one degree  
   **THEN** the user gains the *Vulnerable Condition* (target sees through the attempt and the user is exposed)  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

4. **BUT** tricking requires a plausible narrative; the GM may impose circumstance penalties for outlandish scenarios  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

---

## Story: Coerce Target with Intimidation

**Story type:** user

### Domain terms

- *Coerce* — Intimidation use to force compliance through threat
- *Insight / Will Defense* — whichever is higher resists coercion
- *Hostile Attitude* — target's true attitude after coercion attempt regardless of outcome

### Acceptance criteria

1. **WHEN** *Player* coerces a target using Intimidation  
   **THEN** the system resolves Intimidation opposed by target's Insight or Will defense (higher value)  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

2. **WHEN** the Intimidation check succeeds  
   **THEN** the target treats the user as friendly while in the user's presence  
   **AND** the target's true attitude becomes hostile after the attempt  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

3. **WHEN** the Intimidation check fails by more than one degree  
   **THEN** the opposite effect occurs — the target becomes more resistant and hostile  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

4. **BUT** coerced cooperation only holds while the user is present — the target reverts when the user leaves  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

5. **BUT** the target's attitude always becomes hostile after the attempt, even if coercion succeeded  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

---

## Story: Demoralize Opponent with Intimidation

**Story type:** user

### Domain terms

- *Demoralize* — Intimidation use in combat to impose a penalty condition
- *Impaired Condition* — −2 on checks; imposed on success
- *Disabled Condition* — −5 on checks; imposed on 4+ degrees of success

### Acceptance criteria

1. **WHEN** *Player* demoralizes an opponent using Intimidation (standard action in combat)  
   **THEN** the system resolves Intimidation vs DC (opponent's resistance or rule-specified)  
   **AND** on success applies *Impaired Condition* (−2) until end of user's next round  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

2. **WHEN** the Intimidation check succeeds by four or more degrees  
   **THEN** the system applies *Disabled Condition* (−5) instead of Impaired until end of user's next round  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

3. **WHEN** the Intimidation check fails  
   **THEN** no condition is imposed on the target  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

4. **BUT** the demoralize condition expires at end of user's next round regardless of subsequent actions  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

---

## Story: Intimidate Group of Minions

**Story type:** user

### Domain terms

- *Group Intimidation* — single Intimidation check against a visible, audible group
- *Group Resistance Roll* — single GM roll representing the group's collective resistance
- *Uniform Effect* — the same result must apply to every member

### Acceptance criteria

1. **WHEN** *Player* uses Intimidation against a group of minions who can all see and hear  
   **THEN** the system compares a single Intimidation check against a single GM-rolled resistance result  
   **Evidence:** HeroesHandbook-rules__chunk_054.md — lines 3485–3527

2. **WHEN** the Intimidation check exceeds the group resistance  
   **THEN** the system applies the same effect to every group member uniformly  
   **Evidence:** HeroesHandbook-rules__chunk_054.md — lines 3485–3527

3. **WHEN** the effect cannot be the same for all members (e.g., some members are immune)  
   **THEN** those members are excluded from the effect  
   **Evidence:** HeroesHandbook-rules__chunk_054.md — lines 3485–3527

4. **BUT** group intimidation cannot produce different results for individual members in the same check  
   **Evidence:** HeroesHandbook-rules__chunk_054.md — lines 3485–3527

---

## Story: Improve NPC Attitude with Persuasion

**Story type:** user

### Domain terms

- *Attitude* — five-step NPC disposition scale: Hostile → Unfavorable → Indifferent → Favorable → Helpful
- *Persuasion Check* — Presence-based check against DC 15 to shift attitude
- *Degree Bonus* — +1 attitude step per two degrees of success beyond the first

### Acceptance criteria

1. **WHEN** *Player* uses Persuasion to improve an NPC's attitude (standard action minimum)  
   **THEN** a DC 15 Persuasion check is required  
   **AND** on success the NPC's attitude improves by one step  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

2. **WHEN** the Persuasion check succeeds by two extra degrees (e.g., total 5 over DC)  
   **THEN** the attitude improves by one additional step for every two degrees beyond the first  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

3. **WHEN** the Persuasion check fails by more than one degree  
   **THEN** the NPC's attitude worsens by one step  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

4. **WHEN** *Player* attempts the same argument again after failure in the same scene  
   **THEN** the system blocks or penalizes the attempt unless the situation has changed  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

5. **BUT** attitude cannot be improved beyond Helpful regardless of degree of success  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

---

## Story: Conduct Opposed Negotiation with Persuasion

**Story type:** user

### Domain terms

- *Negotiation* — competitive Persuasion where multiple parties advocate to a third party
- *Opposed Persuasion Check* — all parties roll; highest result gains advocacy advantage

### Acceptance criteria

1. **WHEN** multiple parties negotiate before a neutral party using Persuasion  
   **THEN** all parties roll Persuasion simultaneously  
   **AND** the party with the highest result is judged most persuasive  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

2. **WHEN** there is a tie in Persuasion results  
   **THEN** the outcome is inconclusive; the GM resolves any tie  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

3. **BUT** negotiation outcome does not necessarily change the third party's attitude — it only determines whose argument was more compelling  
   **Evidence:** HeroesHandbook-rules__chunk_058.md — lines 3683–3761

---

## Story: Resist Interaction Skill with Insight

**Story type:** user

### Domain terms

- *Resist Influence* — Insight use to block or negate interaction skill effects
- *Insight Check* — Awareness-based; compared against the incoming skill check result
- *Free Action* — Insight resistance is typically a free or reactive action

### Acceptance criteria

1. **WHEN** *Player* uses Insight to resist an incoming interaction skill effect  
   **THEN** the system compares the Insight check result against the incoming skill check result  
   **AND** if Insight equals or exceeds the incoming result the character is unaffected  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

2. **WHEN** Insight result falls below the incoming skill check result  
   **THEN** the interaction skill effect proceeds normally  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

3. **WHEN** Insight is used reactively  
   **THEN** it counts as a free action and does not cost the character's action for the round  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

4. **BUT** Insight resistance applies only to interaction skills (Deception, Intimidation, Persuasion) — it does not block mind-control powers  
   **Evidence:** HeroesHandbook-rules__chunk_053.md — lines 3441–3484

---

## Story: Detect Illusion Secretly with Insight

**Story type:** system (GM-initiated)

### Domain terms

- *Detect Illusion* — Insight use to sense the flaw in an Illusion effect
- *Illusion Rank* — power effect rank; DC = 10 + Illusion rank
- *Secret Check* — GM rolls on behalf of the character without player notification

### Acceptance criteria

1. **WHEN** a character with Insight comes into sensory contact with an active Illusion effect  
   **THEN** the GM makes a secret Insight check for the character against DC 10 + Illusion rank  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

2. **WHEN** the secret Insight check succeeds  
   **THEN** the character notices a flaw or wrongness in the illusion  
   **AND** the GM reveals that something is off without necessarily identifying the illusion  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

3. **WHEN** the secret Insight check fails  
   **THEN** the character perceives the illusion as real  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

4. **BUT** the player is not told that a check was made — only the result affects the scene  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

---

## Story: Detect Outside Influence with Insight

**Story type:** user

### Domain terms

- *Detect Influence* — Insight use to identify a subject acting under mental control or compulsion
- *Influence Rank* — rank of the affecting effect; DC = 10 + rank
- *Degrees of Success* — three or more degrees give a general idea of the source

### Acceptance criteria

1. **WHEN** *Player* uses Insight to check whether a subject is under outside influence  
   **THEN** the Insight check is against DC 10 + rank of the affecting effect or skill  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

2. **WHEN** Insight check succeeds  
   **THEN** the character notices the subject is acting under outside influence  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

3. **WHEN** Insight check succeeds by three or more degrees  
   **THEN** the character gains a general idea of the nature or source of the influence  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

4. **BUT** Insight identifies that influence exists — it does not automatically identify the source or remove the effect  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

---

## Story: Evaluate Trustworthiness with Insight

**Story type:** user

### Domain terms

- *Evaluate* — Insight use to assess honesty or social situation mood
- *Opposed Deception Check* — Insight vs Deception to assess trustworthiness
- *Social Situation DC* — DC 20 to evaluate group mood

### Acceptance criteria

1. **WHEN** *Player* evaluates a subject's trustworthiness using Insight  
   **THEN** Insight check is opposed by the subject's Deception check  
   **AND** on success the character gains an accurate read of honesty  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

2. **WHEN** *Player* evaluates a social situation's mood  
   **THEN** Insight check is against DC 20  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

3. **WHEN** Insight fails by two or more degrees  
   **THEN** the character misreads the situation (believes a liar, misjudges mood)  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

4. **BUT** the evaluation tells the character their read of the situation — the GM reveals whether it is accurate through the consequences of acting on it  
   **Evidence:** HeroesHandbook-rules__chunk_052.md — lines 3374–3440

---

### Sub-Epic: Use Physical Skills

---

## Story: Balance on Precarious Surface

**Story type:** user

### Domain terms

- *Balance Check* — Acrobatics check vs surface-specific DC
- *Vulnerable Condition* — applied while balancing unless DC voluntarily increased by +5
- *Reactive Balance Check* — triggered when character fails a resistance check while balancing

### Acceptance criteria

1. **WHEN** *Player* moves across a precarious surface  
   **THEN** the system requires an Acrobatics check against the surface's DC  
   **Evidence:** HeroesHandbook-rules__chunk_045.md — lines 2894–2994

2. **WHEN** Acrobatics check succeeds  
   **THEN** character may move at ground speed rank −1  
   **AND** the character is *Vulnerable* unless they voluntarily chose DC +5  
   **Evidence:** HeroesHandbook-rules__chunk_045.md — lines 2894–2994

3. **WHEN** Acrobatics check fails by exactly one degree  
   **THEN** character makes no movement this round  
   **Evidence:** HeroesHandbook-rules__chunk_045.md — lines 2894–2994

4. **WHEN** Acrobatics check fails by two or more degrees  
   **THEN** the character falls  
   **Evidence:** HeroesHandbook-rules__chunk_045.md — lines 2894–2994

5. **WHEN** character fails a resistance check while balancing  
   **THEN** the system immediately triggers a reactive Acrobatics check against the original surface DC  
   **AND** failure on the reactive check causes a fall  
   **Evidence:** HeroesHandbook-rules__chunk_045.md — lines 2894–2994

---

## Story: Perform Acrobatic Maneuver

**Story type:** user

### Domain terms

- *Acrobatic Maneuver* — flips, vaults, tumbling stunts; GM sets DC
- *Prone Condition* — applied on two or more degrees of failure

### Acceptance criteria

1. **WHEN** *Player* attempts an acrobatic stunt (flip, vault, tumble)  
   **THEN** the GM sets a DC for the maneuver  
   **AND** an Acrobatics check resolves success  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

2. **WHEN** Acrobatics check succeeds  
   **THEN** the maneuver completes as intended  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

3. **WHEN** Acrobatics check fails by two or more degrees  
   **THEN** the character ends up prone  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

4. **BUT** one degree of failure leaves the character stopped but not prone; the attempt simply does not complete  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

---

## Story: Rise from Prone as Free Action

**Story type:** user

### Domain terms

- *Prone Condition* — character is on the ground; normally requires a move action to stand
- *DC 20* — threshold for using Acrobatics to rise as a free action instead

### Acceptance criteria

1. **WHEN** *Player* uses Acrobatics to rise from prone  
   **THEN** an Acrobatics check against DC 20 is required  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

2. **WHEN** DC 20 Acrobatics check succeeds  
   **THEN** the character stands as a free action (does not cost move action)  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

3. **WHEN** DC 20 Acrobatics check fails  
   **THEN** the character remains prone and must use a standard move action to stand  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

4. **BUT** this use of Acrobatics may not be combined with other free-action activities in the same moment  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

---

## Story: Reduce Fall Damage with Tumbling

**Story type:** user

### Domain terms

- *Tumbling* — Acrobatics use to reduce fall damage
- *Fall Damage* — damage rank for falling; starts at rank 4 + 2× distance rank
- *Damage Reduction* — −1 damage rank per degree of success

### Acceptance criteria

1. **WHEN** *Player* uses Acrobatics to tumble from a fall  
   **THEN** an Acrobatics check against DC 5 is made  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

2. **WHEN** Acrobatics check succeeds  
   **THEN** fall damage rank is reduced by 1 for each degree of success  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

3. **WHEN** fall damage is reduced to rank 0 or less  
   **THEN** no damage is dealt  
   **AND** the character rises from the landing as a free action  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

4. **BUT** tumbling cannot negate fall damage if the fall is into a hazardous environment; GM discretion applies for environmental effects  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

---

## Story: Climb Surface with Athletics

**Story type:** user

### Domain terms

- *Climb Check* — Athletics check vs surface DC
- *Climb Speed* — ground speed rank −2 while climbing
- *Fall from Climb* — triggered on 2+ degrees of failure while climbing

### Acceptance criteria

1. **WHEN** *Player* climbs a surface using Athletics  
   **THEN** an Athletics check against the surface's DC is required  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

2. **WHEN** the check succeeds  
   **THEN** the character climbs at ground speed rank −2  
   **AND** the character is *Vulnerable* unless they voluntarily increase DC by +5  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

3. **WHEN** Athletics fails by exactly one degree  
   **THEN** no upward progress is made this round  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

4. **WHEN** Athletics fails by two or more degrees  
   **THEN** the character falls from their current height  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

5. **WHEN** character fails a resistance check while climbing  
   **THEN** an immediate reactive Athletics check triggers against the original climb DC  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

---

## Story: Jump with Athletics

**Story type:** user

### Domain terms

- *Jump Distance* — check result in feet (running long-jump); divided for standing/vertical variants
- *Running Long-Jump* — full check result in feet
- *Standing Long-Jump* — result ÷ 2 feet
- *Vertical Jump* — running ÷ 5 feet; standing ÷ 10 feet

### Acceptance criteria

1. **WHEN** *Player* makes a running long-jump  
   **THEN** the Athletics check result equals the horizontal distance covered in feet  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

2. **WHEN** *Player* makes a standing long-jump  
   **THEN** the distance is the Athletics check result divided by 2  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

3. **WHEN** *Player* makes a running vertical jump  
   **THEN** the height reached is the Athletics check result divided by 5  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

4. **WHEN** *Player* makes a standing vertical jump  
   **THEN** the height reached is the Athletics check result divided by 10  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

5. **BUT** the character must have movement remaining in the round to take a running jump; stationary characters default to standing jump  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

---

## Story: Sprint to Increase Speed

**Story type:** user

### Domain terms

- *Sprint Check* — DC 15 Athletics check to increase speed
- *Ground Speed Rank* — base movement speed; +1 rank on successful sprint
- *Free Action Sprint* — the check itself is a free action

### Acceptance criteria

1. **WHEN** *Player* sprints using Athletics (free action)  
   **THEN** an Athletics check against DC 15 is made  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

2. **WHEN** Athletics check succeeds  
   **THEN** ground speed rank increases by +1 for the current round  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

3. **WHEN** Athletics check fails  
   **THEN** speed does not increase; the free action is spent  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

4. **BUT** the speed increase lasts only one round; repeated sprinting requires a check each round  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

---

## Story: Swim with Athletics

**Story type:** user

### Domain terms

- *Swim Check* — DC 10 Athletics check to move in water
- *Swim Speed* — ground speed rank −2 while swimming
- *Going Under* — triggered on 2+ degrees of failure while swimming

### Acceptance criteria

1. **WHEN** *Player* attempts to swim using Athletics  
   **THEN** a DC 10 Athletics check is required  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

2. **WHEN** Athletics check succeeds  
   **THEN** the character moves at ground speed rank −2 through the water  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

3. **WHEN** Athletics check fails by exactly one degree  
   **THEN** no progress is made this round  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

4. **WHEN** Athletics check fails by two or more degrees  
   **THEN** the character goes under water  
   **AND** the GM determines consequences (drowning rules per Powers/GM chapter)  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

---

## Story: Apply Fall Damage to Character

**Story type:** system

### Domain terms

- *Fall Damage* — damage rank = 4 + 2 × distance rank fallen; maximum rank 16
- *Distance Rank* — power rank representing how far the character fell
- *Prone Condition* — character lands prone after any fall

### Acceptance criteria

1. **WHEN** a character falls from height  
   **THEN** the system calculates fall damage rank = 4 + 2 × distance rank fallen  
   **AND** applies damage rank to the character  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

2. **WHEN** calculated fall damage rank exceeds 16  
   **THEN** the system caps it at rank 16  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

3. **WHEN** fall distance rank is 0 or less  
   **THEN** no damage is dealt  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

4. **WHEN** fall damage is dealt  
   **THEN** the character lands prone  
   **Evidence:** HeroesHandbook-rules__chunk_046.md — lines 2995–3065

5. **BUT** Acrobatics tumbling may reduce fall damage before the system applies it; the reduced rank is what damages the character  
   **Evidence:** HeroesHandbook-rules__chunk_047.md — lines 3066–3117

---

## Story: Hide from Observer with Stealth

**Story type:** user

### Domain terms

- *Stealth Check* — Agility-based; opposed by observer's Perception
- *Cover / Concealment* — prerequisite for hiding
- *Distraction* — Deception or Intimidation check creating an opportunity to hide at −5

### Acceptance criteria

1. **WHEN** *Player* attempts to hide while cover or concealment exists  
   **THEN** Stealth check is opposed by the observer's Perception  
   **AND** character is hidden if Stealth result exceeds Perception  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

2. **WHEN** observers are already actively aware of the character  
   **THEN** the character cannot use Stealth to hide without first creating a distraction via Deception or Intimidation  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

3. **WHEN** *Player* uses Deception or Intimidation to create a distraction for hiding  
   **THEN** the Stealth check is at −5 penalty  
   **AND** the cover must be within 1 foot per Stealth rank of the character's position  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

4. **WHEN** character moves at speed rank −1 or slower while hidden  
   **THEN** no Stealth penalty applies for movement  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

5. **WHEN** character moves at full speed while hidden  
   **THEN** a −5 circumstance penalty applies to the Stealth check  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

6. **BUT** hiding in plain sight (no cover or concealment) is not permitted by default  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

---

## Story: Tail Subject Undetected with Stealth

**Story type:** user

### Domain terms

- *Tail / Follow* — Stealth use to follow a subject without being noticed
- *Worried Subject* — subject who makes opposed Perception each time they change course
- *Unsuspecting Subject* — subject who gets only one Perception check per scene

### Acceptance criteria

1. **WHEN** *Player* tails a subject using Stealth  
   **THEN** a Stealth check is made using available cover at normal speed  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

2. **WHEN** the tailed subject is unsuspecting  
   **THEN** the subject gets only one Perception check per scene to notice the tail  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

3. **WHEN** the tailed subject becomes worried (suspects they are being followed)  
   **THEN** the subject makes an opposed Perception check each time they change course  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

4. **WHEN** the subject's Perception check beats the Stealth check  
   **THEN** the subject spots the tail and the follow fails  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

5. **BUT** tailing requires that the character always have cover available on their planned path; losing cover breaks the tail  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

---

### Sub-Epic: Use Combat Skills

---

## Story: Add Close Combat Rank to Attack Check

**Story type:** user

### Domain terms

- *Close Combat Rank* — rank in a specific Close Combat skill (weapon/power)
- *Attack Check* — Fighting + Close Combat rank vs target's defense
- *Specific Weapon or Power* — the named scope of the skill

### Acceptance criteria

1. **WHEN** *Player* makes an attack with the weapon or power named by their Close Combat skill  
   **THEN** the system adds the Close Combat rank to the attack check total  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

2. **WHEN** *Player* attacks with a different weapon (not the one named by the skill)  
   **THEN** the Close Combat rank for that skill does not apply  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

3. **WHEN** the attack targets any defense value  
   **THEN** Close Combat rank does not add to any defense check  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

4. **WHEN** the character has Close Combat: Unarmed  
   **THEN** it applies to punches and kicks but not to grab or trip maneuvers  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

5. **BUT** Close Combat rank is a narrow alternative to raising Fighting; both can contribute in separate instances  
   **Evidence:** HeroesHandbook-rules__chunk_048.md — lines 3118–3168

---

## Story: Add Ranged Combat Rank to Attack Check

**Story type:** user

### Domain terms

- *Ranged Combat Rank* — rank in a specific Ranged Combat skill (weapon/power)
- *Attack Check* — Dexterity + Ranged Combat rank vs target's defense
- *Specific Weapon or Power* — the named scope of the skill

### Acceptance criteria

1. **WHEN** *Player* makes a ranged attack with the weapon or power named by their Ranged Combat skill  
   **THEN** the system adds the Ranged Combat rank to the attack check total  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

2. **WHEN** *Player* attacks with a different ranged weapon  
   **THEN** the Ranged Combat rank for that skill does not apply  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

3. **WHEN** the attack targets any defense value  
   **THEN** Ranged Combat rank does not add to defense  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

4. **WHEN** the character has Ranged Combat: Throwing  
   **THEN** it applies to thrown weapons and thrown objects  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

5. **BUT** for broad bonuses across all ranged attacks, the Ranged Attack advantage is the correct mechanic — not stacking multiple Ranged Combat skills  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

---

### Sub-Epic: Use Manipulation Skills

---

## Story: Conceal Object on Person with Sleight of Hand

**Story type:** user

### Domain terms

- *Concealment Check* — Sleight of Hand check result becomes discovery DC
- *Discovery DC* — DC that Investigation or Perception must beat to find the concealed item

### Acceptance criteria

1. **WHEN** *Player* conceals an object using Sleight of Hand  
   **THEN** the check result becomes the DC for subsequent Investigation or Perception checks to find it  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

2. **WHEN** the concealed object is searched for  
   **THEN** the searcher must beat the concealment DC with Investigation or Perception  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

3. **BUT** concealment applies at the time of hiding; a poorly hidden object (low check) is easily found later  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

4. **BUT** an observer who was watching at the moment of concealment gets a reactive Perception check against the Sleight of Hand check  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

---

## Story: Escape Restraints with Sleight of Hand

**Story type:** user

### Domain terms

- *Escape Check* — Sleight of Hand check vs restraint DC
- *Restraint DC* — difficulty set by the type of restraint (ropes, manacles, etc.)
- *One Minute Minimum* — minimum time for each escape attempt

### Acceptance criteria

1. **WHEN** *Player* attempts to escape restraints using Sleight of Hand  
   **THEN** a Sleight of Hand check vs the restraint's DC is required  
   **AND** at least one minute passes per attempt  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

2. **WHEN** the check meets or exceeds the restraint DC  
   **THEN** the character escapes  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

3. **WHEN** the check fails  
   **THEN** the character remains restrained; another attempt may be made after another minute  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

4. **BUT** repeated failure does not increase the restraint DC unless the character's attempts alert guards  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

---

## Story: Perform Legerdemain with Sleight of Hand

**Story type:** user

### Domain terms

- *Legerdemain* — minor manual feats (card palming, small-object tricks)
- *Unobserved DC* — DC 10 when no observer is focused on the character
- *Observed DC* — opposed by focused observer's Perception

### Acceptance criteria

1. **WHEN** *Player* performs legerdemain without anyone focused on them  
   **THEN** a Sleight of Hand check against DC 10 is made  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

2. **WHEN** an observer is specifically watching the character's hands  
   **THEN** the check is opposed by that observer's Perception  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

3. **WHEN** the check fails  
   **THEN** the observer or nearby characters notice the attempted manipulation  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

4. **BUT** legerdemain cannot produce impossible results; it is limited to what is physically achievable with the character's hands  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

---

## Story: Plant Object on Person with Sleight of Hand

**Story type:** user

### Domain terms

- *Plant* — Sleight of Hand use to secretly place an object on another person
- *Minimum Result 20* — required regardless of DC to successfully plant
- *Notice Attempt* — target's Perception vs Sleight of Hand if they beat the check result

### Acceptance criteria

1. **WHEN** *Player* attempts to plant an object on a person using Sleight of Hand  
   **THEN** a check result of 20 or higher is required to succeed, regardless of opposed Perception  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

2. **WHEN** the check result is 20 or higher and the target's Perception does not beat the check  
   **THEN** the object is planted without the target noticing  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

3. **WHEN** the target's Perception check beats the Sleight of Hand check  
   **THEN** the target notices the planting attempt  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

4. **BUT** a check result below 20 always fails to plant the object, even if the target's Perception would not notice  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

---

## Story: Steal Object from Person with Sleight of Hand

**Story type:** user

### Domain terms

- *Steal Check* — Sleight of Hand vs DC 20 and target's Perception
- *Covert Theft* — successful theft without target awareness
- *Target's Perception* — must not beat Sleight of Hand check for theft to remain covert

### Acceptance criteria

1. **WHEN** *Player* attempts to steal an object from a person using Sleight of Hand  
   **THEN** the check must meet or exceed DC 20  
   **AND** the target's Perception must not beat the check result  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

2. **WHEN** both conditions are met (DC 20+ and Perception not exceeded)  
   **THEN** the object is taken covertly and the target does not notice  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

3. **WHEN** the target's Perception beats the Sleight of Hand check  
   **THEN** the target notices the theft attempt  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

4. **BUT** the target checks Perception against the theft attempt; this is not a passive check — the GM may call it at any time during the scene  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

---

## Story: Contort Through Tight Space with Sleight of Hand

**Story type:** user

### Domain terms

- *Contortion* — Sleight of Hand use to fit through a space too narrow for the body
- *DC 30* — required to fit through a space wide enough for head but not shoulders

### Acceptance criteria

1. **WHEN** *Player* attempts to contort through a tight space using Sleight of Hand  
   **THEN** a check against DC 30 is required  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

2. **WHEN** the check succeeds  
   **THEN** the character fits through the space  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

3. **WHEN** the check fails  
   **THEN** the character cannot fit through and must find another route  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

4. **BUT** contortion applies to spaces wide enough for the head but not the shoulders — smaller spaces are not possible even with a successful check  
   **Evidence:** HeroesHandbook-rules__chunk_060.md — lines 3827–3895

---

## Story: Operate Unfamiliar Technological Device

**Story type:** user

### Domain terms

- *Technology Operate Check* — DC 10 (simple) to DC 25+ (highly advanced)
- *Unfamiliar Device* — device the character has not previously operated
- *Lacking Tools Penalty* — −5 circumstance penalty

### Acceptance criteria

1. **WHEN** *Player* operates an unfamiliar device using Technology  
   **THEN** a check against the device's complexity DC is required (DC 10 simple to DC 25 highly advanced)  
   **Evidence:** HeroesHandbook-rules__chunk_061.md — lines 3896–3943

2. **WHEN** the check succeeds  
   **THEN** the device operates as intended  
   **Evidence:** HeroesHandbook-rules__chunk_061.md — lines 3896–3943

3. **WHEN** the check fails  
   **THEN** the device does not operate; another attempt may be made at the GM's discretion  
   **Evidence:** HeroesHandbook-rules__chunk_061.md — lines 3896–3943

4. **WHEN** the character lacks appropriate tools  
   **THEN** the system applies a −5 circumstance penalty to the check  
   **Evidence:** HeroesHandbook-rules__chunk_061.md — lines 3896–3943

5. **BUT** routine operation of familiar devices does not require a check  
   **Evidence:** HeroesHandbook-rules__chunk_061.md — lines 3896–3943

---

## Story: Build Technological Item

**Story type:** user

### Domain terms

- *Build Check* — Technology check vs complexity DC; time-consuming
- *Build Complexity* — Simple (DC 15, 2 hours) through Advanced (DC 25, 4 days)
- *Wasted Materials* — result of failed build check

### Acceptance criteria

1. **WHEN** *Player* builds a technological item using Technology  
   **THEN** a check against the build DC is required after the specified build time  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

2. **WHEN** the check succeeds  
   **THEN** the item is built and functional  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

3. **WHEN** the check fails  
   **THEN** the build time is wasted and materials are consumed  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

4. **WHEN** *Player* reduces build time by 1 rank  
   **THEN** a −5 penalty applies to the check  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

5. **BUT** a failed build does not permanently prevent building the item; materials and time may be spent again  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

---

## Story: Repair Damaged Technological Item

**Story type:** user

### Domain terms

- *Repair Check* — DC 5 lower than building same item; time 2 ranks lower
- *Repair DC* — complexity-based DC for the specific item

### Acceptance criteria

1. **WHEN** *Player* repairs a damaged technological item  
   **THEN** a Technology check against DC 5 lower than the item's build DC is required  
   **AND** repair time is 2 ranks lower than build time  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

2. **WHEN** the check succeeds  
   **THEN** the item is repaired and functional  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

3. **WHEN** the check fails  
   **THEN** the repair attempt fails; another attempt may be made  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

4. **BUT** an item that has been jury-rigged must be fully repaired before it can be jury-rigged again  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

---

## Story: Perform Jury-Rig Repair

**Story type:** user

### Domain terms

- *Jury-Rig* — emergency Technology repair; standard action; temporary fix
- *Jury-Rig DC* — 10 lower than building the same item
- *Scene Duration* — jury-rig fix lasts only until end of scene

### Acceptance criteria

1. **WHEN** *Player* performs a jury-rig repair using Technology (standard action)  
   **THEN** a check against DC 10 lower than the item's build DC is required  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

2. **WHEN** the check succeeds  
   **THEN** one specific problem with the item is fixed until end of scene  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

3. **WHEN** the scene ends  
   **THEN** the jury-rig fix expires and the item's problem returns  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

4. **WHEN** the item has already been jury-rigged this scene  
   **THEN** it cannot be jury-rigged again until fully repaired  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

5. **BUT** jury-rigging fixes only one problem per check; multiple problems require multiple successful checks  
   **Evidence:** HeroesHandbook-rules__chunk_062.md — lines 3944–3994

---

## Story: Place Demolitions Charge with Technology

**Story type:** user

### Domain terms

- *Demolitions Placement* — careful charge setup at least 1 minute, DC 10
- *Structure Damage Bonus* — +5 per two full degrees of success
- *Premature Detonation* — 2+ degrees of failure during placement

### Acceptance criteria

1. **WHEN** *Player* places a demolitions charge carefully (at least 1 minute) using Technology  
   **THEN** a DC 10 check is required  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

2. **WHEN** the check succeeds by two full degrees  
   **THEN** each two-degree block adds +5 damage rank to the structure being targeted  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

3. **WHEN** the check fails by two or more degrees  
   **THEN** the charge detonates prematurely  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

4. **BUT** successful placement maximizes damage — substandard placement deals standard damage only  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

---

## Story: Defeat Security Device with Technology

**Story type:** user

### Domain terms

- *Security Check* — Technology check vs security level DC
- *Security Level DC* — Simple (DC 10) to Super-Max (DC 40+)
- *Security Trigger* — sets off the device on 2+ degrees of failure

### Acceptance criteria

1. **WHEN** *Player* attempts to disarm a security device using Technology  
   **THEN** a check against the device's security DC is required  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

2. **WHEN** the check meets or exceeds the DC  
   **THEN** the device is disabled or bypassed  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

3. **WHEN** the check fails by more than one degree  
   **THEN** the security device triggers (alarm sounds, trap fires, lockdown activates)  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

4. **WHEN** the check fails by one degree or less  
   **THEN** the disarm fails but the device does not trigger  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

5. **BUT** multiple attempts may be made if the device was not triggered; each attempt risks triggering  
   **Evidence:** HeroesHandbook-rules__chunk_063.md — lines 3995–4045

---

## Story: Diagnose Injuries and Ailments

**Story type:** user

### Domain terms

- *Diagnosis* — Treatment check to identify injuries/ailments; takes ≥1 minute
- *Diagnosis Bonus* — +2 to subsequent Treatment checks at GM's discretion

### Acceptance criteria

1. **WHEN** *Player* diagnoses a patient using Treatment (at least 1 minute)  
   **THEN** a Treatment check is made  
   **AND** success reveals the patient's injuries and ailments  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

2. **WHEN** the diagnosis check succeeds  
   **THEN** at the GM's discretion it grants a +2 bonus to subsequent Treatment checks on the same patient  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

3. **WHEN** the diagnosis check fails  
   **THEN** the character cannot accurately identify the patient's condition  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

4. **BUT** diagnosis cannot invent conditions that do not exist — it only reveals what is actually present  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

---

## Story: Provide Long-Term Patient Care

**Story type:** user

### Domain terms

- *Long-Term Care* — Treatment over one or more days to accelerate recovery
- *Recovery Time Rank* — time it takes to recover; reduced by 1 on successful care check
- *Patient Limit* — healer can treat up to Treatment rank patients simultaneously

### Acceptance criteria

1. **WHEN** *Player* provides long-term care using Treatment (one day or more per check)  
   **THEN** a Treatment check is made at end of each care period  
   **AND** on success the patient's recovery time rank decreases by 1  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

2. **WHEN** a healer provides care  
   **THEN** they may treat up to their Treatment rank in patients simultaneously  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

3. **WHEN** the care check fails  
   **THEN** the patient's recovery time rank does not change for that period  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

4. **BUT** long-term care cannot reduce recovery time below rank 0; natural minimum still applies  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

---

## Story: Revive Dazed or Stunned Character

**Story type:** user

### Domain terms

- *Revive* — Treatment standard action to remove dazed or stunned condition
- *Dazed Condition* — character can take only a single action next round
- *Stunned Condition* — character loses their action for the round
- *Dying Condition* — cannot be revived without first being stabilized

### Acceptance criteria

1. **WHEN** *Player* attempts to revive a dazed or stunned character using Treatment (standard action)  
   **THEN** a Treatment check is made  
   **AND** on success the dazed or stunned condition is removed  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

2. **WHEN** the revive check succeeds  
   **THEN** only the dazed or stunned condition is removed — other conditions remain  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

3. **WHEN** the target is dying  
   **THEN** revive cannot be used — the character must be stabilized first  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

4. **BUT** reviving does not restore any damage; it only removes the specific condition  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

---

## Story: Stabilize Dying Character with Treatment

**Story type:** user

### Domain terms

- *Stabilize* — Treatment standard action to prevent a dying character from worsening
- *Dying Condition* — character on the edge of death; worsens without intervention
- *Stabilized* — dying character is made safe; no longer worsening

### Acceptance criteria

1. **WHEN** *Player* stabilizes a dying character using Treatment (standard action)  
   **THEN** a Treatment check is made  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

2. **WHEN** the check succeeds  
   **THEN** the dying character is stabilized  
   **AND** is no longer at risk of further deterioration  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

3. **WHEN** the check fails  
   **THEN** the character remains dying and may worsen  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

4. **BUT** stabilizing does not awaken or revive the character — a separate revive check is needed to remove the dazed or stunned condition  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

---

## Story: Treat Disease or Poison

**Story type:** user

### Domain terms

- *Treat Disease/Poison* — Treatment check concurrent with patient's resistance check
- *Treatment Bonus* — +2 on success, +5 on 3+ degrees of success, added to patient's resistance check
- *Concurrent Check* — both patient and healer check at the same time

### Acceptance criteria

1. **WHEN** a patient must make a resistance check against disease or poison  
   **THEN** *Player* may make a concurrent Treatment check  
   **AND** on success the patient gains +2 to their resistance check  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

2. **WHEN** the Treatment check succeeds by three or more degrees  
   **THEN** the patient gains +5 to their resistance check instead of +2  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

3. **WHEN** the Treatment check fails  
   **THEN** no bonus is granted to the patient's resistance check  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

4. **BUT** the healer's Treatment check is concurrent — it cannot be made before or after the patient's resistance check for the same event  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

---

## Story: Operate Vehicle Under Stress

**Story type:** user

### Domain terms

- *Vehicle Maneuver Check* — Vehicles check in dramatic/stressful situations
- *Maneuver DC* — Easy (DC 10) to Formidable (DC 25+)
- *Routine Operation* — no check required for familiar vehicles in calm conditions

### Acceptance criteria

1. **WHEN** *Player* attempts a dramatic vehicle maneuver  
   **THEN** a Vehicles check against the maneuver DC is required  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

2. **WHEN** the check succeeds  
   **THEN** the maneuver is completed as intended  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

3. **WHEN** the check fails  
   **THEN** the maneuver fails; the GM determines the consequence (crash, loss of control, etc.)  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

4. **WHEN** *Player* operates a familiar vehicle under calm conditions  
   **THEN** no check is required; routine operation succeeds automatically  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

5. **BUT** Vehicles does not cover animal mounts; Expertise: Riding handles mounts  
   **Evidence:** HeroesHandbook-rules__chunk_064.md — lines 4046–4106

---

### Sub-Epic: Use Knowledge and Awareness Skills

---

## Story: Apply Professional Expertise

**Story type:** user

### Domain terms

- *Professional Task* — routine work within the Expertise field
- *Expertise Check* — Intellect-based; answers knowledge questions
- *Trained Status* — required for professional tasks; untrained limits to easy/basic questions

### Acceptance criteria

1. **WHEN** a trained *Player* performs a routine professional task within their Expertise  
   **THEN** no check is needed for the daily work of the profession  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

2. **WHEN** a trained *Player* answers a basic knowledge question in their field (DC 15)  
   **THEN** an Expertise check against DC 15 resolves success  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

3. **WHEN** a trained *Player* answers a difficult question (DC 20+)  
   **THEN** an Expertise check against the specific DC is required  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

4. **WHEN** an untrained character attempts an Expertise check  
   **THEN** the check is limited to easy questions (DC 10–15) and cannot be routine  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

5. **BUT** Expertise does not cover all knowledge — only what falls within the named field; adjacent fields require a separate skill with circumstance penalty  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

---

## Story: Resolve Expert Knowledge Check Secretly

**Story type:** system (GM-initiated)

### Domain terms

- *Secret Knowledge Check* — GM makes Expertise check on behalf of character without player rolling
- *Expert DC* — GM-set DC based on question difficulty

### Acceptance criteria

1. **WHEN** a knowledge question arises that the character's Expertise should address  
   **THEN** GM may make the Expertise check secretly on behalf of the character  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

2. **WHEN** the secret check succeeds  
   **THEN** GM provides the correct information to the player  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

3. **WHEN** the secret check fails  
   **THEN** GM provides no information or misleading information as appropriate  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

4. **BUT** the player is not told a check was made; they simply receive or do not receive the information  
   **Evidence:** HeroesHandbook-rules__chunk_051.md — lines 3284–3373

---

## Story: Search Area for Clues with Investigation

**Story type:** user

### Domain terms

- *Search Check* — Investigation check to detect hidden details or clues in an area
- *Search DC* — scales from low (obvious clues) to DC 25+ (extremely obscure clues)
- *Concealed Clue DC* — opposed by hider's Stealth or Sleight of Hand

### Acceptance criteria

1. **WHEN** *Player* searches an area for clues using Investigation  
   **THEN** an Investigation check against the clue's DC is required  
   **Evidence:** HeroesHandbook-rules__chunk_055.md — lines 3528–3571

2. **WHEN** the check succeeds  
   **THEN** the character finds the clue or detail being sought  
   **Evidence:** HeroesHandbook-rules__chunk_055.md — lines 3528–3571

3. **WHEN** the clue was deliberately concealed by someone  
   **THEN** the search DC is opposed by the concealer's Stealth or Sleight of Hand check  
   **Evidence:** HeroesHandbook-rules__chunk_055.md — lines 3528–3571

4. **WHEN** the check fails  
   **THEN** the character does not find the clue this round; another attempt may be made  
   **Evidence:** HeroesHandbook-rules__chunk_055.md — lines 3528–3571

5. **BUT** Investigation does not create clues where none exist — if no clue is present, no check can find one  
   **Evidence:** HeroesHandbook-rules__chunk_055.md — lines 3528–3571

---

## Story: Collect Physical Evidence with Investigation

**Story type:** user

### Domain terms

- *Gather Evidence* — Investigation DC 15 to collect without ruining it
- *Two-Degree Failure* — evidence is ruined on 2+ degrees of failure
- *Analysis Penalty* — −5 to analysis if evidence was collected with a single-degree failure

### Acceptance criteria

1. **WHEN** *Player* collects physical evidence using Investigation (DC 15)  
   **THEN** success collects the evidence undamaged for later analysis  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

2. **WHEN** the check fails by exactly one degree  
   **THEN** evidence is collected but compromised; analysis check has −5 penalty  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

3. **WHEN** the check fails by two or more degrees  
   **THEN** the evidence is ruined and cannot be analyzed  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

4. **WHEN** collection succeeds by two or more degrees  
   **THEN** the system grants +2 to the subsequent analysis check  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

5. **BUT** collection is required before analysis — analysis cannot run without collected evidence  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

---

## Story: Analyze Collected Evidence

**Story type:** user

### Domain terms

- *Analyze Evidence* — Investigation DC 15 to extract useful information
- *Analysis DC* — modified by time elapsed and scene disturbance
- *Useful Information* — facts about events, persons, or circumstances extracted from evidence

### Acceptance criteria

1. **WHEN** *Player* analyzes collected evidence using Investigation (DC 15 base)  
   **THEN** success produces useful information about the events or persons involved  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

2. **WHEN** evidence was collected with time elapsed or scene disturbance  
   **THEN** the analysis DC increases accordingly  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

3. **WHEN** the analysis check fails  
   **THEN** no useful information is extracted this attempt  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

4. **BUT** analysis cannot produce information the evidence does not contain; the evidence is the limiting factor  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

---

## Story: Gather Information through Contacts

**Story type:** user

### Domain terms

- *Gather Information* — Investigation check DC 10+ after at least 1 hour
- *Information Classification* — general (DC 10), specific (DC 15), restricted (DC 20), protected (DC 25+)
- *Alert Risk* — 2+ degrees of failure may alert those being investigated

### Acceptance criteria

1. **WHEN** *Player* gathers information through contacts using Investigation (minimum 1 hour)  
   **THEN** a DC 10 or higher check is required based on information classification  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

2. **WHEN** the check meets DC 10  
   **THEN** general information is gathered  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

3. **WHEN** the check meets DC 15 / 20 / 25+  
   **THEN** specific / restricted / protected information is gathered respectively  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

4. **WHEN** the check fails by two or more degrees  
   **THEN** the subjects being investigated are alerted that someone is asking questions  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

5. **BUT** gathering information requires at least one hour per check; faster attempts are not possible  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

---

## Story: Conduct Surveillance on Subject

**Story type:** user

### Domain terms

- *Surveillance* — stationary Investigation check creating a Stealth-opposition DC
- *Surveillance DC* — Investigation check result; subjects must exceed with Stealth to evade
- *Stationary* — character must remain in one position to maintain surveillance

### Acceptance criteria

1. **WHEN** *Player* conducts surveillance using Investigation (stationary)  
   **THEN** the Investigation check result becomes the DC subjects must beat with Stealth to evade  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

2. **WHEN** a subject passes through the surveilled area  
   **THEN** their Stealth check is compared against the surveillance DC  
   **AND** subjects who do not beat the DC are detected  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

3. **WHEN** the character moves from their surveillance position  
   **THEN** the surveillance DC is no longer active  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

4. **BUT** surveillance targets only subjects who pass through the watched area — it does not provide general awareness  
   **Evidence:** HeroesHandbook-rules__chunk_056.md — lines 3572–3638

---

## Story: Make Secret Perception Check for Character

**Story type:** system (GM-initiated)

### Domain terms

- *Secret Perception Check* — GM makes Perception check on behalf of character
- *GM Roll* — hidden from player; only results affect the scene

### Acceptance criteria

1. **WHEN** a potentially noticeable stimulus exists in the scene  
   **THEN** the GM may make a secret Perception check on behalf of the character  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

2. **WHEN** the secret check succeeds  
   **THEN** the GM communicates what the character notices through scene description  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

3. **WHEN** the secret check fails  
   **THEN** the character does not notice the stimulus; GM provides no notification  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

4. **WHEN** the character previously failed a Perception check against a stimulus  
   **THEN** they may retry as a move action if they remain in the area  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

5. **BUT** the player does not know a check was made — only the consequences are revealed  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

---

## Story: Detect Disguise with Perception

**Story type:** user

### Domain terms

- *Detect Disguise* — Perception check opposed by disguise creator's Deception check result
- *Disguise DC* — established at time of Deception disguise check
- *Associate Bonus* — Perception bonus for those who know the impersonated person

### Acceptance criteria

1. **WHEN** *Player* observes a disguised person using Perception  
   **THEN** Perception check is compared against the disguise creator's earlier Deception result  
   **AND** if Perception exceeds the DC the disguise is seen through  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225; HeroesHandbook-rules__chunk_050.md — lines 3226–3283

2. **WHEN** the observer is a regular associate of the impersonated person  
   **THEN** they gain +2 to Perception for this check  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

3. **WHEN** the observer is a close friend  
   **THEN** they gain +5 to Perception for this check  
   **Evidence:** HeroesHandbook-rules__chunk_050.md — lines 3226–3283

4. **WHEN** Perception does not exceed the disguise DC  
   **THEN** the observer does not see through the disguise  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

5. **BUT** the check is typically made secretly by the GM — the observer does not know they failed unless their behavior reveals the deception  
   **Evidence:** HeroesHandbook-rules__chunk_049.md — lines 3169–3225

---

## Story: Notice Concealed Object with Perception

**Story type:** user

### Domain terms

- *Notice Concealed Object* — Perception check vs Sleight of Hand concealment DC
- *Concealment DC* — established at time of Sleight of Hand concealment check
- *Distance Penalty* — −1 per 10 feet to Perception before comparison

### Acceptance criteria

1. **WHEN** *Player* searches for a concealed object using Perception  
   **THEN** Perception check is compared against the concealer's earlier Sleight of Hand result  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

2. **WHEN** Perception exceeds the concealment DC  
   **THEN** the object is noticed  
   **Evidence:** HeroesHandbook-rules__chunk_059.md — lines 3762–3826

3. **WHEN** the observer is 10 or more feet from the concealed object  
   **THEN** the system applies −1 per 10 feet to the Perception check before comparing  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

4. **BUT** Perception does not allow searching through opaque barriers; the object must be in a sensed area  
   **Evidence:** HeroesHandbook-rules__chunk_057.md — lines 3639–3682

---
