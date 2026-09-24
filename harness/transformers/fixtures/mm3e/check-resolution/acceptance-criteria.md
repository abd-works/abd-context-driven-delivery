du# Acceptance Criteria — Check Resolution

Source: `abd-ooad/modules/check-resolution-domain-sketch.md`
Scope: `(E) Resolve Checks` (all sub-epics) and `(E) Translate Rank to Measure`

---

## Epic: Resolve Checks — Make Check

---

### Story: Make Trait Check

**Story type:** user

#### Domain terms

- *Trait Check* — resolution attempt: d20 + Trait Rank + modifiers vs DC
- *d20* — the twenty-sided die; the instrument of every check
- *Trait Rank* — the numeric rank of the trait being checked; primary modifier
- *Circumstance Modifier* — situational bonus or penalty layered on top of the Trait Rank (±2 minor, ±5 major)
- *Roll Total* — d20 result plus all modifiers combined
- *Difficulty Class (DC)* — the target number; Roll Total must meet or exceed it for success
- *Success* — Roll Total ≥ DC
- *Failure* — Roll Total < DC
- *Critical Success* — a natural 20 increases the degree of success by one after normal calculation

#### Acceptance criteria

1. **WHEN** the player makes a *Trait Check* against a set *Difficulty Class (DC)*
   **THEN** the system rolls a *d20* and adds the *Trait Rank* as the primary modifier
   **AND** compares the *Roll Total* to the *DC*: *Roll Total* ≥ *DC* is *Success*; below is *Failure*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### check > Domain Sketch` (invariant: shape is always roll total vs DC)

2. **WHEN** one or more *Circumstance Modifiers* apply to the *Trait Check*
   **THEN** the system adds each modifier to the *Roll Total* before comparing to the *DC*
   **AND** a minor *Circumstance Modifier* is ±2; a major one is ±5
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### modifier > Ubiquitous Language`

3. **WHEN** the required tools for a task are missing
   **THEN** the system imposes a −5 *Circumstance Modifier* on the *Roll Total*
   **AND** if makeshift tools are available, the penalty is −2 instead
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### modifier > Ubiquitous Language`

4. **WHEN** the die result is a natural 20
   **THEN** the system determines the degree normally from the *Roll Total*
   **AND** increases the degree of success by one (*Critical Success*)
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### check > Ubiquitous Language` ("a natural 20 on a check is a critical success: determine the degree normally, then increase it by one")

---

### Story: Grade Check Result by Degree

**Story type:** system

#### Domain terms

- *Graded Check Result* — a check result that produces degrees rather than binary pass/fail
- *Degree of Success* — one per full 5 points the Roll Total exceeds the DC; bare success = 1 degree
- *Degree of Failure* — one per full 5 points the Roll Total falls below the DC; bare failure = 1 degree
- *Margin* — how far above or below the DC the Roll Total landed
- *Critical Success* — natural 20 upgrades degree of success by one after normal calculation

#### Acceptance criteria

1. **WHEN** a check result is graded and the *Roll Total* meets or exceeds the *DC*
   **THEN** the system assigns one *Degree of Success* as a base
   **AND** adds one additional *Degree of Success* for each full 5 points the *Roll Total* exceeds the *DC*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### degree of success > Ubiquitous Language`; `### Graded Check Result > Domain Sketch`

2. **WHEN** a check result is graded and the *Roll Total* falls below the *DC*
   **THEN** the system assigns one *Degree of Failure* as a base
   **AND** adds one additional *Degree of Failure* for each full 5 points the *Roll Total* falls below the *DC*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### degree of failure > Ubiquitous Language`; `### Graded Check Result > Domain Sketch`

3. **WHEN** the *Roll Total* reaches *DC* + 15 or higher
   **THEN** the system reports four *Degrees of Success* (maximum)
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### degree of success > Ubiquitous Language` ("degrees of success range up to four")

4. **WHEN** the *Roll Total* falls *DC* − 20 or lower
   **THEN** the system reports four *Degrees of Failure* (maximum)
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### degree of failure > Ubiquitous Language` ("degrees of failure range down to four")

5. **WHEN** a natural 20 is rolled on a graded check
   **THEN** the system determines the degree normally from the *Margin* first
   **AND** then increases the degree of success by one (*Critical Success*)
   **AND** this can convert a result that would be one *Degree of Failure* into a *Success*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### Graded Check Result > Domain Sketch` ("a natural 20 increases the degree of success by one after normal calculation — critical success")

---

### Story: Make Opposed Check Against Opponent

**Story type:** user

#### Domain terms

- *Opposed Check* — both characters roll; the higher Roll Total wins
- *Active Character* — the character initiating the opposed action
- *Opposing Character* — the character resisting or countering
- *Tie* — Roll Totals are equal; resolved by Trait Bonus, then Tie-Break Roll
- *Tie-Break Roll* — d20 tiebreaker when bonuses also equal (1–10 one character wins, 11–20 the other)
- *Passive Opposition* — DC set to opponent's modifier + 10 when the opponent is not actively contesting

#### Acceptance criteria

1. **WHEN** the player initiates an *Opposed Check*
   **THEN** both the *Active Character* and the *Opposing Character* each roll a *Trait Check*
   **AND** the system compares their *Roll Totals*; the higher total wins
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Ubiquitous Language`; `opposed check > Domain Sketch`

2. **WHEN** the two *Roll Totals* are equal (*Tie*)
   **THEN** the system awards the win to the character with the higher *Trait Bonus*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Ubiquitous Language` ("on a tie, the character with the higher bonus wins")

3. **WHEN** both *Roll Totals* and *Trait Bonuses* are equal
   **THEN** the system rolls a *Tie-Break Roll*: result 1–10 one character wins, 11–20 the other
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Ubiquitous Language`

4. **WHEN** the *Opposing Character* is not actively contesting (*Passive Opposition*)
   **THEN** the system sets the *DC* to the opposing character's modifier + 10
   **AND** the *Active Character* makes a standard *Trait Check* against that *DC* 
   **BUT** the *Opposing Character* does not roll
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Ubiquitous Language`; `opposed check > Domain Sketch` ("passive opposition sets DC to opposing trait modifier + 10")

---

### Story: Resolve Comparison Check Without Roll

**Story type:** system

#### Domain terms

- *Comparison Check* — rank-vs-rank resolution; no d20 involved
- *Rank* — the numeric trait value compared directly
- *Higher Rank* — the winning side; outcome is deterministic

#### Acceptance criteria

1. **WHEN** a *Comparison Check* is made
   **THEN** the system compares the *Ranks* of both characters directly without rolling a *d20*
   **AND** the character with the *Higher Rank* wins
   **BUT** no *Circumstance Modifiers* or die roll are involved; the outcome has no luck component
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Ubiquitous Language` ("a comparison check compares ranks directly without rolling; the higher rank wins — no luck involved"); `opposed check > Domain Sketch`

2. **WHEN** both characters have equal *Ranks* in a *Comparison Check*
   **THEN** the system reports a tie with no winner determined
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Ubiquitous Language` (tie-break rules are stated for Opposed Checks; Comparison Check tie behavior is not explicitly specified — AC phase should confirm with SME)

3. **WHEN** a *Comparison Check* is used to determine priority or advantage
   **THEN** the character with the *Higher Rank* proceeds first or gains the advantage
   **BUT** no degree of success or failure is produced; only a winner or tie
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### opposed check > Domain Sketch` ("a comparison check skips the d20 and compares ranks directly — higher rank wins")

---

### Story: Make Resistance Check Against Effect

**Story type:** user

#### Domain terms

- *Resistance Check* — defense check against an incoming power effect
- *Defense Bonus* — the relevant defense trait modifier (Dodge, Parry, Fortitude, Toughness, or Will)
- *Effect DC* — 10 + Effect Rank; the target number the character must meet or exceed to resist
- *Effect Rank* — the power rank of the incoming effect
- *Degree of Failure* — each 5-point band below the Effect DC; each maps to a condition the effect defines
- *Condition Source* — the power, effect, attacker, or event/situation that imposed a condition; tracked per applied condition
- *Active Condition* — a condition currently applying its modifiers to the character
- *Inactive Condition* — a condition tracked on the character but not applying modifiers; superseded by a more severe condition from a different source
#### Acceptance criteria

1. **WHEN** a power effect targets a character
   **THEN** the system sets the *Effect DC* as 10 + *Effect Rank*
   **AND** resolves the *Resistance Check* as d20 + *Defense Bonus* vs *Effect DC*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### resistance check > Ubiquitous Language`; `resistance check > Domain Sketch`

2. **WHEN** the *Resistance Check Roll Total* equals or exceeds the *Effect DC*
   **THEN** the system reports success and applies no conditions from this effect
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### resistance check > Domain Sketch`

3. **WHEN** the *Resistance Check Roll Total* falls below the *Effect DC*
   **THEN** the system determines the *Degree of Failure* from the margin (one per full 5 points below *Effect DC*)
   **AND** applies the *condition* the effect defines for that *degree of failure* to the *character*
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### Graded Check Result > Domain Sketch` ("on a resistance check, each degree of failure maps to a specific condition imposed on the character")

4. **WHEN** the effect imposes a more severe *condition* than one it already imposed on the *character* (same *Condition Source*)
   **THEN** the more severe *condition* becomes *active* on the *character*
   **AND** the less severe *condition* from that same source is *removed*
   **AND** on recovery from the more severe *condition*, that source's conditions are cleared and the character is unaffected
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` (same-source supersession)

5. **WHEN** the effect would impose a less severe *condition* than one it already imposed on the *character* (same *Condition Source*)
   **THEN** no change is made — the more severe *condition* remains *active*
   **AND** on recovery from the more severe *condition*, that source's conditions are cleared and the character is unaffected
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` (same-source re-hit below superseding)

6. **WHEN** another effect would impose a less severe *condition* than one already *active* on the *character* (a **different** *Condition Source*)
   **THEN** the new condition is added as *inactive* on the *character*
   **AND** if the more severe condition from the other source is later removed, the *inactive* condition becomes *active* and applies its modifiers
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` (different-source supersession)

7. **WHEN** a natural 20 is rolled on the *Resistance Check*
   **THEN** the system applies the *Critical Success* rule — degree of success is increased by one after normal calculation
   **AND** a result that would otherwise be one *Degree of Failure* becomes a success with no conditions applied
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### Graded Check Result > Domain Sketch`; `### check > Ubiquitous Language`

---

### Story: Perform Routine Check

**Story type:** user

#### Domain terms

- *Routine Check* — check substituting a fixed result of 10 for the d20
- *Routine Total* — 10 + all applicable Trait Rank and Circumstance Modifiers
- *Routine Eligibility* — circumstances the GM judges allow a routine check; some traits expand it

#### Acceptance criteria

1. **WHEN** circumstances allow a *Routine Check*
   **THEN** the system substitutes a fixed result of 10 for the *d20*
   **AND** adds all applicable *Trait Rank* and *Circumstance Modifiers* to produce the *Routine Total*
   **AND** reports success if *Routine Total* ≥ *DC* without rolling
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### routine check > Ubiquitous Language`; `routine check > Domain Sketch`

2. **WHEN** the *Routine Total* does not meet the *DC*
   **THEN** the player may choose to roll the *d20* instead
   **AND** the system treats the task as not routine for that character at that modifier level
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### routine check > Ubiquitous Language`; `routine check > Domain Sketch` ("if the routine total is insufficient, the player may still roll")

3. **WHEN** a character's *Trait Bonus* is +10 or higher on a *Routine Check* against *DC* 20
   **THEN** the system reports automatic success without requiring any roll
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### routine check > Ubiquitous Language` ("a character with a +10 bonus achieves a routine result of 20, succeeding at DC 20 tasks without rolling")

4. **WHEN** a trait grants extended *Routine Eligibility* for specific situations
   **THEN** the system applies *Routine Check* resolution in those situations even where it would not otherwise apply
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### routine check > Domain Sketch` ("some traits widen what counts as routine for a given character")

---

### Story: Lead Team Check with Helpers

**Story type:** user

#### Domain terms

- *Team Check* — a check with one Leader and one or more Helpers contributing modifiers
- *Leader* — the character whose Roll Total determines the final outcome
- *Helper* — each assisting character; rolls the same Trait against a fixed DC of 10
- *Helper Success* — Helper Roll Total ≥ 10; grants the Leader a Circumstance Modifier
- *Helper Failure* — Helper Roll Total < 10; may impose a −2 Circumstance Modifier on the Leader

#### Acceptance criteria

1. **WHEN** the player initiates a *Team Check*
   **THEN** the *Leader* rolls the shared *Trait* normally
   **AND** each *Helper* rolls the same *Trait* against a fixed *DC* of 10
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### Team Check > Domain Sketch`; `### modifier > Ubiquitous Language`

2. **WHEN** one or two *Helpers* achieve *Helper Success*
   **THEN** the system grants the *Leader* a +2 *Circumstance Modifier* on the Leader's check
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### modifier > Ubiquitous Language`; `### Team Check > Domain Sketch`

3. **WHEN** three or more *Helpers* achieve *Helper Success*
   **THEN** the system grants the *Leader* a +5 *Circumstance Modifier* instead
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### modifier > Ubiquitous Language` ("three or more helper successes grant +5"); `### Team Check > Domain Sketch`

4. **WHEN** a *Helper* achieves *Helper Failure*
   **THEN** the system may impose a −2 *Circumstance Modifier* on the *Leader's* check
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### modifier > Ubiquitous Language`; `### Team Check > Domain Sketch`

5. **WHEN** the *Leader's* check is resolved
   **THEN** only the *Leader's* final *Roll Total* determines the outcome
   **BUT** Helper results do not contribute beyond the *Circumstance Modifier* already applied to the Leader
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### Team Check > Domain Sketch` ("the leader's check result determines the outcome — helpers only modify it")

---

## Epic: Resolve Checks — Apply Conditions

---

### Story: Apply Condition to Character

**Story type:** system

#### Domain terms

- *Condition* — named state applied to a character; imposes modifiers, restrictions, or behavioral changes
- *Basic Condition* — single game modifier (e.g. *Dazed* limits actions, *Impaired* −2 penalty, *Vulnerable* halves defenses)
- *Combined Condition* — bundle of Basic Conditions under one name (e.g. *Staggered* = *Dazed* + *Hindered*)
- *Game Modifier* — the specific mechanical effect a condition imposes on checks, actions, or defenses
- *Stack* — all active conditions apply simultaneously; effects combine
- *Constituent* — a Basic Condition that is part of a Combined Condition; can be superseded or resolved independently

#### Acceptance criteria

1. **WHEN** a condition is imposed on a character
   **THEN** the system records the condition as active and applies its *Game Modifier* to that character
   **AND** if multiple conditions are active simultaneously, all effects *Stack*
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Ubiquitous Language`; `condition > Domain Sketch` ("when multiple conditions apply, all effects stack")

2. **WHEN** a *Basic Condition* is applied
   **THEN** the system enforces its single *Game Modifier* (action restriction, check penalty, or defense reduction)
   **AND** the modifier persists until the condition's source effect ends or the condition is otherwise removed
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions (instances of Condition)` list

3. **WHEN** a *Combined Condition* is applied
   **THEN** the system applies each of its *Constituent* *Basic Conditions* simultaneously
   **AND** individual *Constituents* can be independently superseded or resolved while the parent *Combined Condition* name persists
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch`; `Combined conditions (composites of basic conditions)` list

4. **WHEN** the *Dazed* condition is applied
   **THEN** the system restricts the character to free actions and one standard action per turn
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*dazed*)

5. **WHEN** the *Impaired* condition is applied
   **THEN** the system applies a −2 *Circumstance Modifier* to the character's checks
   **AND** if scoped to a specific trait, only checks using that trait take the penalty
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*impaired*)

6. **WHEN** the *Vulnerable* condition is applied
   **THEN** the system halves the character's active defense values (rounding up)
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*vulnerable*)

---

### Story: Supersede Condition in Chain

**Story type:** system

#### Domain terms

- *Superseded Condition* — the less severe condition overridden while the more severe is present
- *More Severe Condition* — the condition that takes precedence in the chain
- *Override* — the more severe condition suppresses the lesser's effects while both are present
- *Source Effect* — the effect that imposed a condition; removal of the source is what truly resolves it

#### Acceptance criteria

1. **WHEN** a more severe *condition* is applied to a character who already has a lesser one
   **THEN** the system applies only the *More Severe Condition's* effects
   **AND** overrides the *Superseded Condition* while the more severe one is present
   **BUT** the *Superseded Condition* is not destroyed — its *Source Effect* continues to be tracked
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` (invariant: "overridden by the more severe one while present, never duplicated"); corrections-log.md — Correction 23

2. **WHEN** *Dazed* is active and *Stunned* is applied
   **THEN** the system enforces the *Stunned* restriction (no actions, including free actions)
   **AND** suppresses the *Dazed* modifier for as long as *Stunned* is present
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*dazed* → *stunned*)

3. **WHEN** *Impaired* is active and *Disabled* is applied
   **THEN** the system applies the *Disabled* −5 penalty instead of *Impaired's* −2
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*impaired* → *disabled*)

4. **WHEN** *Vulnerable* is active and *Defenseless* is applied
   **THEN** the system sets active defense bonuses to 0 (not merely halved)
   **AND** attackers may use routine checks against the character; forgoing routine makes any hit a critical hit
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*vulnerable* → *defenseless*)

5. **WHEN** *Hindered* is active and *Immobile* is applied
   **THEN** the system overrides movement to zero speed
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*hindered* → *immobile*)

6. **WHEN** *Compelled* is active and *Controlled* is applied
   **THEN** the system transfers full action control to the controlling character (all actions dictated)
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Basic conditions` (*compelled* → *controlled*)

---

## Epic: Resolve Checks — Recover from Conditions

---

### Story: Roll Resistance Check Against Ongoing Effect to Remove Conditions

**Story type:** user

#### Domain terms

- *Ongoing Effect* — a sustained power effect that remains active across rounds
- *Active Resistance* — the character's attempt to resist or shake off a sustained effect
- *Effect Ends* — the ongoing effect is terminated; all its conditions are removed
- *Effect Persists* — the ongoing effect remains; conditions stay active

#### Acceptance criteria

1. **WHEN** the *Resistance Check* against an *Ongoing Effect* succeeds
   **THEN** the *Ongoing Effect* ends
   **AND** all conditions imposed by that effect on the character are removed
   **AND** any *inactive* conditions that were blocked by those removed conditions become *active*
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` ("is removed when the source effect ends"); `## Condition > ### condition > Domain Sketch` (different-source supersession — inactive becomes active)

2. **WHEN** the *Resistance Check* against an *Ongoing Effect* fails
   **THEN** the *Ongoing Effect* remains active
   **AND** all conditions imposed by it persist; no conditions are removed
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch`

3. **WHEN** the *Resistance Check* against an *Ongoing Effect* fails with multiple *Degrees of Failure*
   **THEN** the *Ongoing Effect* remains active
   **AND** additional *conditions* are imposed per the *degrees of failure* as defined by the effect
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### Graded Check Result > Domain Sketch`; `## Condition > ### condition > Domain Sketch`

---

### Story: Remove Condition When Source Effect Ends

**Story type:** system

#### Domain terms

- *Source Effect* — the effect that imposed a condition; its end triggers removal
- *Condition Removal* — the condition is lifted from the character's active state
- *Revealed Condition* — a superseded condition that re-emerges when the more severe one ends while its source is still active
#### Acceptance criteria

1. **WHEN** a *Source Effect* ends (expires, is resisted, or is otherwise terminated)
   **THEN** the system removes all conditions imposed by that specific effect from the character
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` ("is removed when the source effect ends")

2. **WHEN** a *More Severe Condition* ends and the *Superseded Condition's* source effect is still active
   **THEN** the system reveals the *Superseded Condition*; it re-emerges as the active state
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` (supersession invariant); corrections-log.md — Correction 23

3. **WHEN** a *More Severe Condition* ends and the *Superseded Condition's* source has also ended
   **THEN** the system removes both conditions
   **BUT** the lesser condition does not re-emerge
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch`; corrections-log.md — Correction 23

4. **WHEN** a character has conditions from multiple different source effects and one source ends
   **THEN** only the conditions from that source are removed
   **AND** conditions from all other still-active sources remain in place
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### condition > Domain Sketch` (per-source tracking implied by "is removed when the source effect ends")

---

### Story: Roll Fortitude Check to Stabilize While Dying

**Story type:** user

#### Domain terms

- *Dying* — combined condition: Incapacitated + near death; triggers Fortitude Check each round
- *Fortitude Check* — Fortitude defense check at DC 15 while Dying
- *Stabilized* — Dying condition ends; character is no longer imminently at risk of death
- *Accumulated Degrees* — total degrees of success and failure tracked across all rounds of being Dying
- *Death* — three total Degrees of Failure accumulated across rounds while Dying

#### Acceptance criteria

1. **WHEN** a character has the *Dying* condition
   **THEN** the system requires a *Fortitude Check* at *DC* 15 each round
   **AND** tracks *Accumulated Degrees* of success and failure across all rounds of being *Dying*
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Combined conditions` (*dying*: "Fortitude DC 15 each round")

2. **WHEN** the character's *Accumulated Degrees* of success reaches two
   **THEN** the system marks the character as *Stabilized*
   **AND** the *Dying* condition ends
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Combined conditions` (*dying*: "two degrees of success stabilizes")

3. **WHEN** the character's *Accumulated Degrees* of failure reaches three
   **THEN** the system marks the character as dead
   **BUT** the count is total across multiple rounds, not just from a single check
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Combined conditions` (*dying*: "three total degrees of failure means death")

4. **WHEN** a natural 20 is rolled on the *Fortitude Check* while *Dying*
   **THEN** the system applies the *Critical Success* rule — degree of success +1 after normal calculation
   **AND** this accelerates progress toward the two-degree *Stabilized* threshold
   **Evidence:** check-resolution-domain-sketch.md — `## Check > ### check > Ubiquitous Language`; `### Graded Check Result > Domain Sketch`; `## Condition > ### Combined conditions` (*dying*)

---

### Story: Stabilize Dying Ally with Treatment Check

**Story type:** user

#### Domain terms

- *Treatment Check* — a skill check made by an Ally to stabilize a Dying character
- *Dying Character* — the character with the Dying condition being stabilized
- *Ally* — a different character making the Treatment Check
- *Stabilized* — Dying condition ends as a result of the Treatment Check success

#### Acceptance criteria

1. **WHEN** an *Ally* makes a *Treatment Check* on a *Dying Character*
   **THEN** the system resolves the Treatment skill check using the ally's relevant trait and modifier
   **AND** on success, marks the *Dying Character* as *Stabilized*
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Combined conditions` (*dying*: "Fortitude DC 15 each round — two degrees of success stabilizes"); Treatment as an alternative stabilization path

2. **WHEN** the *Treatment Check* fails
   **THEN** the *Dying Character* must still attempt the *Fortitude Check* for that round
   **AND** the *Dying* condition persists
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Combined conditions` (*dying*)

3. **WHEN** the *Treatment Check* succeeds
   **THEN** the character is *Stabilized* — the *Dying* condition ends
   **BUT** stabilization is not the same as recovery; the character remains *Incapacitated* until further treatment or rest
   **Evidence:** check-resolution-domain-sketch.md — `## Condition > ### Combined conditions` (*dying*, *incapacitated*)

4. **WHEN** the *Ally* is also engaged in combat or otherwise constrained
   **THEN** making the *Treatment Check* consumes the *Ally's* action for that round
   **Evidence:** check-resolution-domain-sketch.md — `## Boundary Domain > ### Action round structure` (standard/move/free action structure; Treatment is an action)

---

## Epic: Translate Rank to Measure

---

### Story: Translate Trait Rank to Real-World Value

**Story type:** system

#### Domain terms

- *Rank* — numeric trait value to translate
- *Measurements Table* — lookup table mapping ranks to mass, distance, time, and volume
- *Real-World Value* — the physical quantity (mass, distance, time, or volume) corresponding to a rank
- *Doubling Scale* — each rank increase approximately doubles the measurement value
- *Negative Rank* — each lower rank halves the measurement value of the preceding rank

#### Acceptance criteria

1. **WHEN** the system needs to express a *Trait Rank* as a real-world quantity
   **THEN** it looks up the *Rank* in the *Measurements Table*
   **AND** returns the value in the appropriate dimension (mass, distance, time, or volume)
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Measurement > Ubiquitous Language`; `Measurement > Domain Sketch`

2. **WHEN** the *Rank* is negative
   **THEN** each lower *Rank* halves the measurement value of the rank above it
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Rank > Ubiquitous Language` ("ranks can be negative; each lower rank halves the previous measurement")

3. **WHEN** two *Ranks* must be combined arithmetically
   **THEN** the system converts each *Rank* to its *Measurements Table* value, performs arithmetic on the values, and converts the result back to a *Rank*
   **BUT** *Ranks* must never be added or subtracted directly
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Rank > Domain Sketch` (invariant: "ranks must never be added directly")

4. **WHEN** the *Rank* is at a high value
   **THEN** the resulting measurement is approximate — a guideline for play, not a precise calculation
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Measurement > Domain Sketch` ("values at higher ranks are approximate — guidelines for play, not precise values")

---

### Story: Derive Measurement from Rank Formula

**Story type:** system

#### Domain terms

- *Distance Rank* — the rank result for a distance formula; looked up in Measurements Table as distance
- *Time Rank* — the rank result for a time formula; looked up in Measurements Table as time
- *Speed Rank* — the rank of the character's speed trait
- *Strength Rank* — the rank of the character's Strength ability
- *Mass Rank* — the rank of the object being thrown
- *Rank Arithmetic* — rank addition or subtraction performed via measurement table conversion, not directly

#### Acceptance criteria

1. **WHEN** the system derives travel distance
   **THEN** it adds *Time Rank* + *Speed Rank* and looks up the result in the *Measurements Table* as a distance value
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Measurement > Ubiquitous Language` ("Distance Rank = Time Rank + Speed Rank"); `Measurement > Domain Sketch`

2. **WHEN** the system derives travel time
   **THEN** it subtracts *Speed Rank* from *Distance Rank* and looks up the result in the *Measurements Table* as a time value
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Measurement > Ubiquitous Language` ("Time Rank = Distance Rank − Speed Rank"); `Measurement > Domain Sketch`

3. **WHEN** the system derives throwing distance
   **THEN** it subtracts the thrown object's *Mass Rank* from the thrower's *Strength Rank* and looks up the result in the *Measurements Table* as a distance value
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Measurement > Ubiquitous Language` ("Throwing Distance Rank = Strength Rank − Mass Rank"); `Measurement > Domain Sketch`

4. **WHEN** the formula produces a negative result rank
   **THEN** the system still looks up that negative rank in the *Measurements Table* and returns the halved measurement value
   **Evidence:** check-resolution-domain-sketch.md — `## Core Domain > ### Rank > Ubiquitous Language` ("ranks can be negative; each lower rank halves the previous measurement")
