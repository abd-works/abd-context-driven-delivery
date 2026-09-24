---
state: domain-sketch
---

# Module: [Check Resolution]

_Object model for all Check Resolution terms. Concepts: Trait, Rank, Measurement, Check, Check Result, Condition. Subtypes: Graded Check Result, Opposed Check, Resistance Check, Routine Check, Team Check. Properties, instances, composites, and boundary terms modeled inline._

Scope: The d20 resolution mechanic (roll + modifier vs DC), checks (routine, opposed, resistance), degrees of success/failure, measurements and the Rank/Measure table, and conditions (basic and combined).

**Core terms**:
- d20
- check
- Difficulty Class (DC)
- opposed check
- resistance check
- routine check
- degree of success
- degree of failure
- modifier
- rank
- measure
- condition
- combined condition
- dazed
- stunned
- staggered
- incapacitated
- dying
- vulnerable
- defenseless
- impaired
- disabled
- weakened
- exhausted
- fatigued
- Gamemaster (GM)
- player character (PC)
- non-player character (NPC)

**Moved to other modules**:
- hero point → Combat
- extra effort → Combat
- power stunt → Combat
- reaction → Combat

---

All uncertain outcomes are resolved with one mechanic: roll d20, add all appropriate modifiers, compare against a Difficulty Class; meeting or exceeding the DC is success. Each check is tied to exactly one trait. Opposed, resistance, and routine checks are specializations — not different systems. Graded checks produce degrees based on the margin above or below the DC; a natural 20 always increases the degree of success by one.

---

# Core Domain

## Trait

A trait is the base abstraction for every quantifiable game characteristic a character possesses — abilities, skills, defenses, powers, and advantages are all traits. Trait owns the concept of rank: every trait has exactly one rank, a single numeric measure of its effectiveness, and that rank is the value that flows into checks as the modifier. Without a trait there is no rank, without a rank there is no modifier, and without a modifier there is no check. The Rank and Measure abstraction translates trait ranks into real-world values (mass, time, distance, volume), but it is the trait that carries the rank in the first place. Defenses (Dodge, Parry, Fortitude, Toughness, Will) are traits derived from abilities; they supply the DC or the modifier for resistance and attack checks. Other modules (Ability, Skill, Power, Advantage) define specific kinds of traits, but the abstract concept — a quantifiable characteristic with a rank — belongs here. Every trait is always referenced through a check ("Strength check," "Dodge resistance check"), making Trait the single point of connection between a character's capabilities and the resolution system.

### Trait

#### Ubiquitous Language

- A trait is any quantifiable game characteristic a character possesses — abilities, skills, advantages, powers, and defenses are all traits.
- Every trait has a rank; rank is the single numeric measure of a trait's effectiveness.
- A check is always a check *of* a trait — "Strength check," "Acrobatics check," "Dodge resistance check" — there is no check without a trait supplying the modifier.
- The Measurements Table translates trait ranks into real-world values (mass, time, distance, volume); traits are what have ranks, so measurements are a property of traits.
- Defenses (Dodge, Parry, Fortitude, Toughness, Will) are traits derived from abilities; they supply the DC or the modifier for resistance and attack checks.
- Other modules (Ability, Skill, Power, Advantage) define *specific* traits; the abstract concept of what a trait is — a quantifiable characteristic with a rank — belongs here.

#### Domain Sketch

- is a *quantifiable characteristic* of a *character*
- has exactly one *rank* — the single numeric value measuring its effectiveness
- supplies its *rank* as the primary *modifier* for any *check* made using it; without a *trait* there is no *check*
- *abilities*, *defenses*, *skills*, *powers*, and *advantages* are all *traits* — each is a subtype owned by its own module

#### Decisions made

- *Trait* is owned by this module as the base abstraction — other modules (*Ability*, *Skill*, *Power*, *Advantage*) define specific traits but the abstract concept of "quantifiable characteristic with a rank" belongs here.
- *Ability*, *defense*, *skill*, *power*, *advantage* are **subtypes** of *Trait* with distinct behavior — each is owned by its own module; this module defines only the abstract base.
- *Rank* is a concept — simple, but with its own scale, invariant, and interactions with *Check* and *Measurement*. *Trait* carries exactly one *Rank*.
- *Measurement* is a concept — it owns the conversion logic and the real-world value lookup. *Rank* feeds into it; *Measurement* produces the value.

#### References

**Ref — Ranks & Measures**
Source: context/rules/HeroesHandbook-rules__chunk_008.md
Locator: lines 376–808
Extract: whole

**Ref — Game Play**
Source: context/rules/HeroesHandbook-rules__chunk_009.md
Locator: lines 809–874
Extract: whole

---

### Rank

#### Ubiquitous Language

- Every quantifiable trait has a rank — the single numeric value measuring that trait's effectiveness.
- Ranks can be negative; each lower rank halves the previous measurement.
- Ranks must not be added directly; convert to measures, add the measures, then convert back to a rank.

#### Domain Sketch

- is a single numeric value carried by a *trait* — the measure of that *trait's* effectiveness
- can be negative; each lower *rank* halves the previous *measurement* value
- supplies the base *modifier* for a *check* — the *trait's* *rank* flows directly into the *roll total*
- feeds into *Measurement* for conversion to real-world values (*mass*, *time*, *distance*, *volume*)
- follows a roughly doubling scale — each *rank* increase approximately doubles the *measurement* value
- **Invariant:** *ranks* must never be added directly; convert to *measures*, perform arithmetic on the *measures*, then convert back to a *rank*

#### Decisions made

- *Rank* is a concept, not a property of *Trait* — it has its own scale (doubling), its own invariant (no direct addition), and its own interactions (feeds into both *Check* as modifier and *Measurement* as lookup key). Simple, but distinct.

#### References

**Ref — Ranks & Measures**
Source: context/rules/HeroesHandbook-rules__chunk_008.md
Locator: lines 376–808
Extract: whole

---

### Measurement

#### Ubiquitous Language

- The Measurements Table maps each rank to mass, time, distance, and volume on a roughly doubling scale.
- Distance Rank = Time Rank + Speed Rank; Time Rank = Distance Rank − Speed Rank; Throwing Distance Rank = Strength Rank − Mass Rank.
- Measurements are approximate, especially at higher ranks — guidelines, not precise values.

#### Domain Sketch

- translates a *rank* into a real-world value across four dimensions: *mass*, *time*, *distance*, and *volume*
- determines *throwing distance* by subtracting the *object's mass rank* from the *thrower's strength rank* and looking up the result as a *distance* value
- determines *travel distance* by adding *time rank* and *speed rank* and looking up the result as a *distance* value
- determines *travel time* by subtracting *speed rank* from *distance rank* and looking up the result as a *time* value
- resolves combined quantities by converting *ranks* to *measures*, performing the arithmetic on the *measures*, then converting back to a *rank*
- values at higher *ranks* are approximate — guidelines for play, not precise calculations

#### Decisions made

- *Measurement* is a concept — it has its own structure (four dimension types) and its own arithmetic rules (rank subtraction for throwing, rank addition for distance/time). *Rank* feeds in; *Measurement* produces the real-world value.
- The four dimension types (*mass*, *time*, *distance*, *volume*) are type properties of *Measurement*, not subtypes — every dimension follows the same doubling-scale lookup and rank-arithmetic rules.
- The formulas (throwing distance = strength rank − mass rank; travel distance = time rank + speed rank) are behaviors of *Measurement*, not of *Trait* or *Check* — they resolve ranks into outcomes using the measurement table.

#### References

**Ref — Things To Know About Measurements**
Source: context/rules/HeroesHandbook-rules__chunk_007.md
Locator: lines 336–375
Extract: whole

**Ref — Ranks & Measures**
Source: context/rules/HeroesHandbook-rules__chunk_008.md
Locator: lines 376–808
Extract: whole

---

## Check

A check is the core resolution mechanic — the single mechanism through which any uncertain outcome in the game is determined. It binds together a d20 roll, a trait-derived modifier, and a Difficulty Class into one comparison: roll plus modifier versus DC, with success on a match or exceed. The check owns this formula and is the single source of truth for whether an action succeeds or fails; no other abstraction may duplicate this determination. Three specialized forms exist within its boundary: opposed checks (two characters' results compared directly), resistance checks (defense bonus versus an effect's DC, typically 10 + effect rank), and routine checks (a fixed result of 10 replacing the die, used when circumstances are not demanding). Trait supplies the modifier, and the GM controls which DCs, circumstance modifiers, and routine allowances apply. Every check references exactly one trait — "Strength check," "Dodge resistance check" — and without a trait there is no check.

A check must always produce a binary success/failure result. When graded, it yields a degree that the Degree abstraction interprets. A natural 20 is always a critical success (degree increased by one). Circumstance modifiers (±2 minor, ±5 major) and team checks (helpers rolling against DC 10 to grant bonuses) layer onto the base formula but never change its fundamental shape. The invariant: d20 + modifier vs DC, every time, no exceptions.

### d20

#### Ubiquitous Language

- The game uses a single twenty-sided die (d20) to resolve actions.
- "d20+2" means roll the die and add two; "d20−4" means roll and subtract four.
- The die can also express percentages in increments of 5% (multiply the face value by 5).

#### Domain Sketch

- is the instrument a *check* rolls — a property of *check*, not a separate concept

#### References

**Ref — The Die**
Source: context/rules/HeroesHandbook-rules__chunk_004.md
Locator: lines 202–243
Extract: whole

**Ref — Ch1 The Basics**
Source: context/rules/HeroesHandbook-rules__chunk_005.md
Locator: lines 244–284
Extract: whole

---

### check

#### Ubiquitous Language

- A check is d20 + trait rank (plus any additional modifiers) vs a Difficulty Class (DC); equaling or exceeding the DC is success, below is failure.
- Whenever a character attempts something where the outcome is in doubt, it requires a check of an appropriate trait — ability, skill, power, etc.
- Additional modifiers come from circumstances, advantages, or power effects layered on top of the trait rank.
- A natural 20 on a check is a critical success: determine the degree normally, then increase it by one degree; this can turn a failure into a success.

#### Domain Sketch

- is made using the *trait* of a *character*
- is made against a *difficulty class* set by the *GM* or through a *trait difficulty table*
- may have a *circumstance modifier* applied to the check *result* (±2 minor, ±5 major)
- is resolved by *rolling* a *d20*, adding the *trait rank* and the *circumstance modifier* and comparing the *roll total* to the *difficulty class*
- produces a *check result*
- may be assisted by a *team check*
- *difficulty class* comes from the *rules benchmark ladder*, *opposed totals*, *passive opposition* (*opposing modifier + 10*), or *effect rank* (*resistance*) — these are mechanisms in the rules, not a *Gamemaster* modeled as a domain object
- **Invariant:** shape is always *roll total* versus *difficulty class*; subtypes only vary how *total* or *DC* is produced

#### Decisions made

- *Check* alone owns *success/failure* for uncertain outcomes; nothing else reimplements *roll total* versus *difficulty class*.
- *Check result* is a concept, not a property of *Check* — it carries its own responsibilities (success/failure, margin, grading, degree mapping to conditions).
- *Degree of success* and *degree of failure* are properties of a *graded check result*, not standalone concepts.
- *Comparison check* (rank vs rank, no roll) stays a special case inside *opposed check*, not a second engine.
- *d20* is the instrument a *check* rolls — a property, not a separate concept.
- *Modifier* is a value slot on a *check* (primary from *trait rank*, plus stacked *circumstance modifiers*) — a property, not a concept.
- *Gamemaster*, *player character*, *non-player character* are user/actor roles, not domain objects in this module.

#### References

**Ref — Ch1 The Basics**
Source: context/rules/HeroesHandbook-rules__chunk_005.md
Locator: lines 244–284
Extract: whole

**Ref — Game Play**
Source: context/rules/HeroesHandbook-rules__chunk_009.md
Locator: lines 809–874
Extract: whole

**Ref — The Die**
Source: context/rules/HeroesHandbook-rules__chunk_004.md
Locator: lines 202–243
Extract: whole

**Ref — Check Examples**
Source: context/rules/HeroesHandbook-rules__chunk_011.md
Locator: lines 931–990
Extract: whole

**Ref — Circumstances And Difficulty**
Source: context/rules/HeroesHandbook-rules__chunk_015.md
Locator: lines 1147–1194
Extract: whole

**Ref — The Gamemaster**
Source: context/rules/HeroesHandbook-rules__chunk_006.md
Locator: lines 285–335
Extract: whole

---

### Check Result

#### Domain Sketch

- is produced by a *check* — the outcome of comparing *roll total* to *difficulty class*
- is either *success* (*roll total* meets or exceeds *difficulty class*) or *failure* (below)
- carries the *margin* — how far above or below the *difficulty class* the *roll total* fell
- a *natural 20* can turn *failure* into *success*

---

### Graded Check Result *is a type of* Check Result

#### Domain Sketch

- adds *degrees of success* and *degrees of failure* based on the *margin*
- each full *five points* of *margin* above *difficulty class* adds a *degree of success*; each full *five points* below adds a *degree of failure*
- a *natural 20* increases the *degree of success* by one after normal calculation (*critical success*)
- on a *resistance check*, each *degree of failure* maps to a specific *condition* imposed on the *character*

#### References

**Ref — Degrees Of Success And Failure**
Source: context/rules/HeroesHandbook-rules__chunk_013.md
Locator: lines 1038–1101
Extract: whole

**Ref — Critical Success**
Source: context/rules/HeroesHandbook-rules__chunk_010.md
Locator: lines 875–930
Extract: whole

---

### Difficulty Class (DC)

#### Ubiquitous Language

- The DC is a number set by the GM that a check result must equal or exceed to succeed.
- A standard difficulty scale runs from Very Easy (DC 0) through Nigh-Impossible (DC 40) in steps of 5.
- In some cases the DC is set by another character's trait (opposed checks) or by an effect's rank (resistance checks, typically 10 + effect rank).

#### References

**Ref — Ch1 The Basics**
Source: context/rules/HeroesHandbook-rules__chunk_005.md
Locator: lines 244–284
Extract: whole

**Ref — Critical Success**
Source: context/rules/HeroesHandbook-rules__chunk_010.md
Locator: lines 875–930
Extract: whole

---

### modifier

#### Ubiquitous Language

- A modifier is a number added to or subtracted from a d20 roll before comparing to the DC.
- The primary modifier comes from the trait's rank; additional modifiers come from circumstances, advantages, or power effects.
- A minor circumstance modifier is ±2; a major circumstance modifier is ±5.
- Missing required tools imposes a −5 penalty; makeshift tools reduce this to −2.
- Circumstance modifiers apply to the check result (not the DC) for consistency.
- Team checks: one leader rolls normally; each helper checks the same trait against DC 10; helper success grants the leader a +2 or +5 circumstance bonus; helper failure can impose a −2 penalty.

#### References

**Ref — The Die**
Source: context/rules/HeroesHandbook-rules__chunk_004.md
Locator: lines 202–243
Extract: whole

**Ref — Circumstances And Difficulty**
Source: context/rules/HeroesHandbook-rules__chunk_015.md
Locator: lines 1147–1194
Extract: whole

---

### opposed check *is a type of* check

#### Ubiquitous Language

- An opposed check pits two characters' check results against each other; the higher result wins.
- On a tie, the character with the higher bonus wins; if bonuses are also equal, roll d20 — 1–10 one character wins, 11–20 the other.
- Routine opposition sets the DC as the opposing character's modifier + 10 (used when the opponent is not actively opposing).
- A comparison check compares ranks directly without rolling; the higher rank wins (no luck involved).

#### Domain Sketch

- is made against an *opposing character's* *check result* as the *difficulty class*
- is rolled by both the *active character* and the *opposing character*; the *higher result* wins
- on a *tie*, the *higher bonus* wins; if *bonuses* also tie, a *tie-break d20* decides (1–10 vs 11–20)
- *passive opposition* sets *difficulty class* to *opposing trait modifier + 10* when the *opponent* is not *actively contesting*
- a *comparison check* skips the *d20* and compares *ranks* directly — higher *rank* wins; no luck involved

#### References

**Ref — Opposed Check Examples**
Source: context/rules/HeroesHandbook-rules__chunk_012.md
Locator: lines 991–1037
Extract: whole

**Ref — Opposed Checks**
Source: context/rules/HeroesHandbook-rules__chunk_014.md
Locator: lines 1102–1146
Extract: whole

---

### resistance check *is a type of* check

#### Ubiquitous Language

- A resistance check is d20 + defense bonus vs the hazard's DC (typically 10 + effect rank).
- Resistance checks may be graded, with different outcomes at different degrees of success or failure.

#### Domain Sketch

- uses a *defense bonus* (from a *defense trait*) as its *modifier*
- *difficulty class* is typically *10 + effect rank* from the *effect* being resisted
- produces a *graded check result*
- each *degree of failure* in the *result* maps to a specific *condition* imposed on the *character*

#### References

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195–1237
Extract: whole

---

### routine check *is a type of* check

#### Ubiquitous Language

- A routine check substitutes a fixed result of 10 for the die roll; the GM decides when circumstances allow a routine check.
- A character with a +10 bonus achieves a routine result of 20, succeeding at DC 20 tasks without rolling.
- If a character's routine result is not sufficient for a task, the player may still roll; the task is by definition not routine for that character.
- Certain game traits change what tasks or situations count as "routine" for a character.

#### Domain Sketch

- *substitutes* a fixed *10* for the *d20*; full *modifiers* still apply
- if *10 + modifiers* meets or exceeds the *difficulty class*, the *character* succeeds without *rolling*
- if the *routine total* is insufficient, the *player* may still *roll* — the task is by definition not *routine* for that *character*
- some *traits* widen what counts as *routine* for a given *character*

#### References

**Ref — Critical Success**
Source: context/rules/HeroesHandbook-rules__chunk_010.md
Locator: lines 875–930
Extract: whole

**Ref — Check Examples**
Source: context/rules/HeroesHandbook-rules__chunk_011.md
Locator: lines 931–990
Extract: whole

---

### Team Check *is a type of* check

#### Domain Sketch

- has a *leader* who *rolls* the primary *check* normally
- has one or more *helpers* who each *roll* the same *trait* versus a fixed *difficulty class* of *10*
- each *helper success* grants the *leader* a +2 *circumstance modifier*; three or more *helper successes* grant +5
- *helper failure* may impose a −2 *circumstance modifier* on the *leader's* *check*
- the *leader's* *check result* determines the outcome — *helpers* only modify it

#### References

**Ref — Circumstances And Difficulty**
Source: context/rules/HeroesHandbook-rules__chunk_015.md
Locator: lines 1147–1194
Extract: whole

---

### degree of success

#### Ubiquitous Language

- A graded check counts each 5 full points above the DC as one additional degree of success; a bare success is one degree.
- Degrees of success range up to four (DC + 15 or higher).
- A natural 20 (critical success) increases the degree of success by one.
- Some checks specify specific results for each degree of success.

#### References

**Ref — Critical Success**
Source: context/rules/HeroesHandbook-rules__chunk_010.md
Locator: lines 875–930
Extract: whole

**Ref — Degrees Of Success And Failure**
Source: context/rules/HeroesHandbook-rules__chunk_013.md
Locator: lines 1038–1101
Extract: whole

---

### degree of failure

#### Ubiquitous Language

- A graded check counts each 5 full points below the DC as one additional degree of failure; a bare failure is one degree.
- Degrees of failure range down to four (DC − 20 or lower), though more than two degrees of failure rarely matter in practice.
- Specific types of graded checks — notably resistance checks — give defined results for each degree of failure.

#### References

**Ref — Degrees Of Success And Failure**
Source: context/rules/HeroesHandbook-rules__chunk_013.md
Locator: lines 1038–1101
Extract: whole

---

### Gamemaster (GM)

#### Ubiquitous Language

- The GM creates adventures, portrays villains and supporting characters, describes the world, and decides the outcome of actions based on die rolls and rules.
- The GM sets the DC for checks based on circumstances.
- The GM decides when a routine check is allowed and how many characters can help in a team check.

#### References

**Ref — The Gamemaster**
Source: context/rules/HeroesHandbook-rules__chunk_006.md
Locator: lines 285–335
Extract: whole

---

### player character (PC)

#### Ubiquitous Language

- A player controls a superhero they have created; they interact with other PCs and with the world and stories created by the GM.
- Players declare extra effort, spend hero points, and choose which actions their heroes take each turn.

#### References

**Ref — The Die**
Source: context/rules/HeroesHandbook-rules__chunk_004.md
Locator: lines 202–243
Extract: whole

---

### non-player character (NPC)

#### Ubiquitous Language

- NPCs include villains, supporting cast, thugs, cops — any character controlled by the GM rather than a player.
- Active defenses in combat against NPCs are generally routine opposition (DC 10 + defense).

#### References

**Ref — The Die**
Source: context/rules/HeroesHandbook-rules__chunk_004.md
Locator: lines 202–243
Extract: whole

---

## Condition

Condition is the status-effect system that translates mechanical outcomes — failed resistance checks, fatigue from extra effort, environmental hazards — into named states that impose concrete modifiers on a character. Each condition tracks its *condition source* (the power, effect, attacker, or event that imposed it) and carries an active or inactive status; only active conditions apply their modifiers. Basic conditions impose a single modifier (dazed limits actions, impaired applies −2, vulnerable halves defenses); combined conditions bundle multiple basics under one name (staggered = dazed + hindered, incapacitated = defenseless + stunned + unaware), and individual constituents can be resolved or superseded independently. Condition owns the supersession hierarchy (dazed → stunned, impaired → disabled → debilitated, vulnerable → defenseless, hindered → immobile) and three distinct supersession rules: when a source imposes a more severe condition than one it already imposed, the lesser is removed; when a source would impose a lesser condition it already surpassed, nothing happens; when a lesser condition arrives from a different source while a more severe one is already active, the lesser is parked as inactive and becomes active once the blocking condition is gone. Condition interacts with Check by consuming degrees of failure from resistance checks, with Hero Point which can directly remove specific conditions via Recover, and with Extra Effort whose fatigue cost imposes conditions on the fatigued → exhausted → incapacitated escalation track. When multiple active conditions apply, all effects stack.

### condition

#### Ubiquitous Language

- A condition is shorthand for a set of game modifiers imposed by effects, injuries, or fatigue.
- If multiple conditions apply, use all of their effects; some conditions supersede lesser ones.
- Each basic condition describes a single game modifier; they are the building blocks of the condition system.

#### Domain Sketch

- is a named *state* carried by a *character*; the *source* (effect, injury, fatigue, or hazard) does the imposing — the condition is what the character then carries and enforces
- is created from a *condition source* and carries an *active* or *inactive* status
- *penalizes* a suffering *character* accorsing to a *game modifier* (*impaired* applies −2 penalty, *vulnerable* halves defenses)
- may also *resrict* a suffering *character*  (e.g. *dazed* limits actions)
- enforces *penalties* and *restrictions* on a *character* only when *active*; enforcement handled by *action round structure* (Combat) and by *checks* (this module)
- when multiple *active conditions* apply, all effects stack
- it *supersedes* a less severe *condition*
- is *superseded_by* by a more severe *condition* that overrides it
- is *removed* when the same *source* imposes a more severe *condition*
- is *unchanged* when the same *source* would impose a *condition* that is *superseded_by* an *active* more severe condition
- is *inactive* when imposed by one source while *superseded_by* am active *condition* from a *different source* 
- is *active* when the blocking  *condition* from the other source that *supersedes* this condition is removed — modifiers then apply
- is removed when its *condition source* ends
- **Invariant:** only *active* conditions apply modifiers; same-source supersession removes the lesser condition entirely; different-source supersession parks it as *inactive* until the blocking condition is gone

#### Decisions made

- Each named *condition* (*dazed*, *stunned*, *impaired*, etc.) is an **instance** of *Condition*, not a subtype — they differ by data (which modifiers, which restrictions) but share the same lifecycle: applied, stacked, superseded, resolved.
- *Combined conditions* are **composites** — each names a bundle of *basic condition* instances, not a separate concept with its own behavior.
- *Condition* is imposed as a *result* of a *check* (typically via *degrees of failure* on a *resistance check*); the chain from check to condition is a cross-concept relationship, not duplicated resolution logic.
- Each *Condition* instance owns *supersedes* and *superseded_by* as properties — the *supersession chain* is navigable through condition data itself, not via a separate runtime object.

#### References

**Ref — Reactions**
Source: context/rules/HeroesHandbook-rules__chunk_017.md
Locator: lines 1238–1344
Extract: whole

**Ref — Combined Conditions**
Source: context/rules/HeroesHandbook-rules__chunk_018.md
Locator: lines 1345–1425
Extract: whole

---

### condition source

#### Domain Sketch

- is the *power* *effect* and *attacker*, or *event/situation* that imposed a *condition* on a *character*
- is recorded when the *condition* is applied; used to distinguish same-source from different-source *supersession*
- is data owned by the *condition* — it has no lifecycle of its own
- **Invariant:** two *conditions* sharing the same *condition source* are evaluated under same-source supersession rules; conditions from different sources are evaluated under different-source rules

#### Decisions made

- *Condition Source* is a **value** on the *Condition* instance, not a separate runtime object — it is the identity token (name, reference, or descriptor) of whatever caused the condition to be imposed.

#### References

**Ref — Combined Conditions**
Source: context/rules/HeroesHandbook-rules__chunk_018.md
Locator: lines 1345–1425
Extract: whole

---


### Basic conditions (instances of Condition)

- *dazed* — limited to *free actions* and one *standard action* per turn; superseded by *stunned*
- *stunned* — cannot take any *actions*, including *free actions*; supersedes *dazed*
- *vulnerable* — *active defenses* halved (round up); superseded by *defenseless*
- *defenseless* — *active defense bonuses* become 0; attackers may use *routine checks*; forgoing routine makes any hit a *critical hit*; supersedes *vulnerable*
- *impaired* — −2 *circumstance penalty* on *checks* (may be scoped to a *trait*); superseded by *disabled*
- *disabled* — −5 *circumstance penalty* on *checks* (may be scoped); superseded by *debilitated*
- *weakened* — temporary *power point* loss in a *trait*; superseded by *debilitated*
- *debilitated* — one or more *abilities* lowered below −5
- *hindered* — half normal *speed* (−1 *speed rank*); superseded by *immobile*
- *immobile* — no *movement speed*; still capable of *actions* unless another *condition* prevents it
- *compelled* — limited to *free actions* and one *standard action* chosen by the *controller*; superseded by *controlled*
- *controlled* — all *actions* each turn dictated by another *character*
- *fatigued* — *hindered*; recovers after one hour of rest
- *normal* — unharmed, unaffected, acting normally
- *transformed* — some or all *traits* altered by an outside agency; *power point total* cannot increase
- *unaware* — completely unaware of surroundings; cannot make *interaction* or *Perception checks* (may be scoped to specific senses)

### Combined conditions (composites of basic conditions)
#### Domain Sketch

- a *combined condition* bundles multiple *basic conditions* under one name; individual *constituents* can be *resolved* or *superseded* independently


- *staggered* = *dazed* + *hindered*
- *incapacitated* = *defenseless* + *stunned* + *unaware*; generally fall *prone*
- *dying* = *incapacitated* + near death; *Fortitude* DC 15 each round — two *degrees of success* stabilizes, three total *degrees of failure* means death
- *exhausted* = *impaired* + *hindered*; recovers after one hour of comfortable rest
- *asleep* = *defenseless* + *stunned* + *unaware*; hearing *Perception check* (3+ *degrees of success*) or shaking wakes the *character*
- *blind* = *hindered* + visually *unaware* + *vulnerable*; may also be *impaired* or *disabled* for vision-dependent activities
- *bound* = *defenseless* + *immobile* + *impaired*
- *deaf* — auditory concealment from the *character*; may allow surprise attacks
- *entranced* = *stunned*; any obvious *threat* breaks the trance; an ally can free with *interaction skill check* (DC 10 + *effect rank*)
- *paralyzed* = *defenseless* + *immobile* + physically *stunned*; still aware; can take purely mental *actions*
- *prone* — −5 *close attack penalty*; opponents get +5 *close* / −5 *ranged attack modifier*; *hindered*; standing up is a *move action*
- *restrained* = *hindered* + *vulnerable*; if anchored to an *immobile* object, *immobile* instead of *hindered*
- *surprised* = *stunned* + *vulnerable*

---

# Boundary Domain

## Effect / power effect

Owned by: Power

### Ubiquitous Language

- An effect is the basic building block of a power; it describes what a power does in game terms.
- Resistance check DC is typically 10 + effect rank — the effect's rank is what the character resists against.
- Conditions are imposed by effects (as well as by injuries, fatigue, and environmental hazards).
- Some effects are ongoing — they must be resisted multiple times, not just once.

### Domain Sketch

- has a *rank* that determines the *resistance check* DC (DC = rank + 10)
- may impose one or more *conditions* on a *character* based on the type of effect and the *degree of failure* on the resistance check
- may be **ongoing** for a target *character*: requires a *resistance check* at the end of each of the target's turns until ended
- when ongoing and the *resistance check* succeeds: the effect ends and all *conditions* it imposed on the *character* are removed
- when ongoing and the *resistance check* fails: the effect persists; all conditions it imposed remain; further conditions may be added per the effect's description
- **Invariant:** an ongoing effect is either active or ended; when ended, all conditions it imposed — whether *active* or *inactive* — are removed from the *character*

### Decisions made

- The "ongoing" quality is a property of an effect, not a separate concept. Whether an effect requires repeated resistance checks is determined by the Power module (the effect's definition), not by this module.
- This module is responsible only for the check-resolution behavior when an ongoing effect is in play: what happens on success (ends + conditions cleared) and failure (persists + conditions remain).

### References

**Ref — Resistance and Ongoing Effects**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791–14830
Extract: whole

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195–1237
Extract: whole

---

## Character / hero

Owned by: Character Construction

### Ubiquitous Language

- A character is the entity that possesses traits, makes checks, and has conditions applied to it.
- Every rule in this module acts on or through a character — there is no check without a character making it.

### References

**Ref — The Gamemaster**
Source: context/rules/HeroesHandbook-rules__chunk_006.md
Locator: lines 285–335
Extract: whole

---

## Power points

Owned by: Character Construction

### Ubiquitous Language

- A character's power point total is referenced by conditions: Transformed cannot increase it; Weakened temporarily removes power points from a trait.

### References

**Ref — Reactions**
Source: context/rules/HeroesHandbook-rules__chunk_017.md
Locator: lines 1238–1344
Extract: whole

---

## Game modifier

Owned by: (consuming module — Combat for action restrictions, Check Resolution for check penalties, Character Construction for trait alterations)

### Ubiquitous Language

- Conditions define modifiers (action restrictions, check penalties, defense reductions); enforcement is owned by the consuming module.

---

## Action round structure

Owned by: Combat

### Ubiquitous Language

- Defines standard/move/free actions and turn order that conditions restrict.
- A round is 6 seconds; each character gets one turn per round.

### References

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195–1237
Extract: whole
