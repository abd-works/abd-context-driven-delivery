---
state: crc
---

# Module: [Check Resolution]

_CRC model for the d20 resolution mechanic, checks, degrees, conditions, and rank-to-measure translation. Every behavior bullet in the domain sketch traces to at least one responsibility. `Imposed Condition` introduced as state-carrier; `Imposed Conditions` introduced as collection class to own supersession logic._

Scope: The d20 resolution mechanic (roll + modifier vs DC), checks (routine, opposed, resistance, team), degrees of success/failure, the Rank/Measure table, and conditions (basic and combined).

---

# Core Domain

## **Trait**

Trait is the abstract root for every quantifiable game characteristic. `Rank` is the numeric effectiveness value every trait carries and the primary modifier that flows into checks. `Measurement` converts rank integers to real-world physical values via a roughly doubling scale.

### **Trait**
character                   | Character
purchased rank              | number
effective rank              | number, Character
                            |   invariant: effective rank = purchased rank − modifier
modifier                    | Character,Imposed Conditions, Condition, Game Modifier
real world value            | Measurement, MEASUREMENT_TYPE, Measurement, effective rank
                            |   invariant:  MEASUREMENT_TYPE determined by trait an operationeg Speed.time(distance); Speed.distance(time) ; Strength.throw(weight), Strength.lift()
perform check               | Check, Rank, Check Result
AddRank                     | number, Measurement, MEASUREMENT_TYPE
                                invariant: trait ranks must never be added directly — convert to trait rank measures, perform arithmetic on measures, then convert back to a rank

### **MEASUREMENT_TYPE**
MASS=1
TIME=2
DISTANCE=3
VOLUME=4

### **Measurement**
measurement  type             | MEASUREMENT_TYPE
real-world value | Rank, MEASUREMENT_TYPE
derive throwing distance    | Rank
                            |   invariant: throwing distance rank = thrower strength rank − object mass rank
derive travel distance      | Rank
                            |   invariant: travel distance rank = time rank + speed rank
derive travel time          | Rank
                            |   invariant: travel time rank = distance rank − speed rank
combine via measure arithmetic | Rank
                            |   invariant: values at higher ranks are approximate guidelines, not precise calculations

### references

**Ref — Ranks & Measures**
Source: context/rules/HeroesHandbook-rules__chunk_008.md
Locator: lines 376–808
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_008.md lines 376–808)
```

**Ref — Things To Know About Measurements**
Source: context/rules/HeroesHandbook-rules__chunk_007.md
Locator: lines 336–375
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_007.md lines 336–375)
```

**Ref — Game Play**
Source: context/rules/HeroesHandbook-rules__chunk_009.md
Locator: lines 809–874
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_009.md lines 809–874)
```

### decisions made

- *Rank* is a numeric value — not a separate class. *Trait* owns all logic: measurement lookup, rank arithmetic (`Add`), modifier calculation. Rank has no behavior of its own.
- *Measurement* owns the four-dimension lookup and rank-arithmetic formulas — rank feeds in; *Measurement* produces the real-world value. The formulas (throwing, travel distance, travel time) are behaviors of *Measurement*, not of *Trait*.
- *MEASUREMENT_TYPE* is a named enumeration class with explicit constants (MASS, TIME, DISTANCE, VOLUME) — not a parenthetical value or a set of subtypes.
- *Trait* distinguishes *purchased rank* (what was paid for) from *effective rank* (purchased minus condition penalties). The penalty is retrieved by traversing `Character → Imposed Conditions → Condition → Game Modifier`.
- *Trait* knows its owning *Character* — needed to reach imposed conditions for penalty calculation.

---

## **Check**

Check is the single resolution mechanic for all uncertain outcomes. `Check Result` is separated as a class because it carries its own responsibilities — status, margin, and `is critical` — independently from the check that produced it. `Graded Check Result` adds a single `degree` (1–4); the inherited status tells you whether it's success or failure. Two subtypes vary inherited responsibilities via invariants only: `Opposed Check` changes how the DC is formed; `Routine Check` changes the roll total. `Resistance Check` is not a class — it is an instance of a graded check. `Team Check` adds helpers and drives the whole helper→modifier→leader flow inside `perform check`.

### **Check**
using trait                 | Trait
circumstance modifier       | (±2 minor or ±5 major)
roll total                  | Trait, Difficulty Class
                            |   invariant: roll total = d20 + trait rank + circumstance modifier
resolve                     | Difficulty Class, Check Result
                            |   invariant: shape is always roll total vs difficulty class; subtypes vary only how total or DC is formed

### **Check Result**
status                      | (success or failure)
                            |   invariant: success when roll total ≥ difficulty class; failure when below
margin                      | (integer)
is critical                 | (true or false)

### **Graded Check Result : Check Result**
degree                      | (1–4)
                            |   invariant: base 1; +1 for each full 5 points margin from DC; maximum 4
                            |   invariant: if is critical, increase degree by one after normal calculation
resulting condition         | Condition
                            |   invariant: the condition is determined by the degree and the effect's condition set

### **Difficulty Class**
threshold value             | (integer 0–40)

### **Opposed Check : Check**
opponent                    | Character
difficulty class            | Trait, Check Result
                            |   invariant: both characters roll the same trait; the opposing character's check result roll total becomes the difficulty class
                            |   invariant: on tied roll totals, the higher trait bonus wins; if bonuses also tie, a tie-break d20 decides (1–10 one character wins, 11–20 the other)
                            |   invariant: when passive, the opposing character does not roll; DC = opposing trait modifier + 10


### **Routine Check : Check**
roll total                  |
                            |   invariant: substitutes 10 for the d20; all trait rank and circumstance modifiers still apply
                            |   invariant: some traits expand what situations count as routine for a given character
                            |   invariant: if the routine total does not meet the DC, the character may still roll as a standard check

### **Team Check : Check**
helpers                     | Character
perform check               | Check, Difficulty Class, Check Result
                            |   invariant: each helper runs perform check against DC 10 once before the leader rolls
                            |   invariant: circumstance modifier calculated once from helper results: 1–2 successes → +2; 3+ → +5; any failure → −2
                            |   invariant: only the leader's roll total determines the outcome

### references

**Ref — Ch1 The Basics**
Source: context/rules/HeroesHandbook-rules__chunk_005.md
Locator: lines 244–284
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_005.md lines 244–284)
```

**Ref — Game Play**
Source: context/rules/HeroesHandbook-rules__chunk_009.md
Locator: lines 809–874
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_009.md lines 809–874)
```

**Ref — The Die**
Source: context/rules/HeroesHandbook-rules__chunk_004.md
Locator: lines 202–243
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_004.md lines 202–243)
```

**Ref — Critical Success**
Source: context/rules/HeroesHandbook-rules__chunk_010.md
Locator: lines 875–930
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_010.md lines 875–930)
```

**Ref — Degrees Of Success And Failure**
Source: context/rules/HeroesHandbook-rules__chunk_013.md
Locator: lines 1038–1101
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_013.md lines 1038–1101)
```

**Ref — Opposed Checks**
Source: context/rules/HeroesHandbook-rules__chunk_014.md
Locator: lines 1102–1146
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_014.md lines 1102–1146)
```

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195–1237
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_016.md lines 1195–1237)
```

**Ref — Circumstances And Difficulty**
Source: context/rules/HeroesHandbook-rules__chunk_015.md
Locator: lines 1147–1194
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_015.md lines 1147–1194)
```

### decisions made

- *d20* is the instrument *Check* rolls — a property of *Check*, not a separate class.
- *Modifier* is a value slot on *Check* (primary from trait rank, plus stacked circumstance modifiers) — a property, not a concept.
- *Check Result* separated from *Check* — it carries status (success/failure), margin, and `is critical` independently from the check that produced it. The `is critical` flag is a boolean state; what it does to degrees lives on *Graded Check Result*.
- *Graded Check Result* has a single `degree` (1–4) — combined with the inherited `status`, callers know the direction. No separate degree-of-success and degree-of-failure properties.
- `resulting condition` on *Graded Check Result* — the condition produced by the degree. The mapping from degree to condition is the *Effect*'s job; the result just holds what was produced.
- *Resistance Check* is not a class — it is an instance of a graded check with a defense trait and an Effect-provided DC. No structural difference from *Check*.
- *Opposed Check* is a Liskov-valid subtype — only `difficulty class` and `opponent` differ; all mode variants (active, passive, tie-break) are invariants on inherited responsibilities, not new responsibility names.
- *Routine Check* is a Liskov-valid subtype — only `roll total` differs (d20 pinned to 10 with fallback). No other responsibilities change.
- *Team Check* — `helpers` is a first-class property; `perform check` drives the helper rolls, modifier computation, and leader check in one operation.
- *Difficulty Class* is stateless — it holds a threshold value and has no lifecycle of its own.
- *Gamemaster*, *player character*, and *non-player character* are actor roles, not domain objects — *Check* references only domain concepts (Trait, Difficulty Class, Check Result).

---

## **Condition**

`Condition` is a value object: it holds the named modifier definition and supersession chain that are the same for every character. `Game Modifier` is the penalty a condition applies — it carries what trait it targets and how much. `Imposed Condition` is a state-carrier: it holds the per-application state (active/inactive status, condition source, blocking condition) that varies per character and per imposition. `Imposed Conditions` is a collection class on *Character* that owns supersession logic. `Applied Effect` is a state-carrier that links an *Effect* to the *Imposed Conditions* it created on a character; it owns removal and the `resist` responsibility. `Combined Condition` is a named bundle of basic conditions; constituents may be superseded or resolved independently.

### **Condition**
condition name              | (dazed, stunned, impaired, disabled, vulnerable, defenseless, hindered, immobile, compelled, controlled, weakened, debilitated, fatigued, transformed, unaware, normal)
game modifier               | Game Modifier
supersedes                  | Condition
superseded by               | Condition
                            |   invariant: the supersession chain is navigable through condition data — supersedes and superseded-by are properties of Condition, not a separate runtime object

### **Game Modifier**
applies to                  | Trait
amount                      | number

### **Condition Source**
 source                     | (power effect name, attacker reference, or event descriptor)
                            |   invariant: two imposed conditions sharing the same source are evaluated under same-source supersession rules; conditions from different sources are evaluated under different-source rules

### **Imposed Condition**
applied condition           | Condition
active status               | (active or inactive)
                            |   invariant: only an active imposed condition applies its game modifier to the character
imposing source             | Condition Source
blocking condition          | Imposed Condition
                            |   invariant: a different-source less-severe condition is inactive while a more severe condition from another source is present; it becomes active when the blocking condition is removed

### **Imposed Conditions**
applied conditions          | Imposed Condition
apply new condition         | Condition, Condition Source, Imposed Condition
                            |   invariant: same-source more severe — the more severe becomes active; the less severe imposed condition from that same source is removed entirely
                            |   invariant: same-source less severe — no change when the source already has a more severe active condition
                            |   invariant: different-source more severe — the more severe supersedes the less severe regardless of source; the less severe becomes inactive, blocked by the more severe
                            |   invariant: different-source less severe — the new condition is added as inactive, blocked by the more severe already-active condition from the other source
enforce on check            | Check
                            |   invariant: all active imposed conditions stack; each applies its game modifier simultaneously
reveal blocked condition    | Imposed Condition
                            |   invariant: when a blocking condition is removed, the lesser condition from the other source becomes active if its source is still in effect
track dying fortitude progress | Check Result
                            |   invariant: while Dying is active, a Fortitude Check at DC 15 is required each round; accumulated 2 degrees of success → stabilized (Dying ends); accumulated 3 degrees of failure → death

### **Combined Condition**
constituent conditions      | Condition
                            |   invariant: a combined condition is a named bundle of basic conditions; each constituent may be superseded or resolved independently while the combined name persists

### **Applied Effect**
effect                      | Effect
imposed conditions          | Imposed Condition
                            |   invariant: knows which imposed conditions it created on the character
is ongoing                  | (active or ended)
                            |   invariant: when ended, all imposed conditions it created are removed from the character
resist                      | Character, Trait, Graded Check Result
                            |   invariant: on success — applied effect ends
                            |   invariant: on failure — applied effect persists

### references

**Ref — Reactions**
Source: context/rules/HeroesHandbook-rules__chunk_017.md
Locator: lines 1238–1344
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_017.md lines 1238–1344)
```

**Ref — Combined Conditions**
Source: context/rules/HeroesHandbook-rules__chunk_018.md
Locator: lines 1345–1425
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_018.md lines 1345–1425)
```

### decisions made

- Each named condition (*dazed*, *stunned*, *impaired*, etc.) is an **instance** of *Condition*, not a subtype — they differ by data (modifier description, action restrictions, supersession chain) but share the same structure.
- *Game Modifier* is a named class — it carries `applies to` (which trait type the penalty targets) and `amount`. Not a parenthetical description on *Condition*.
- *Imposed Condition* introduced as a state-carrier — active/inactive status, condition source, and blocking condition reference are per-application state that does not belong on the *Condition* value object or on *Character*.
- *Imposed Conditions* introduced as a collection class — supersession logic requires a named owner; that owner is the collection, not *Character*. Removal is not a responsibility of this collection — the actor removing conditions (*Applied Effect*) drives that.
- *Applied Effect* introduced as a state-carrier — it links an *Effect* to the *Imposed Conditions* it created on a character. Core domain, not boundary, because it emerged from condition lifecycle requirements. When an applied effect ends, it removes its imposed conditions. It also owns the `resist` responsibility (re-rolling defense against the originating effect).
- *Condition Source* is a value on *Imposed Condition* — the identity token of what caused the imposition; it has no lifecycle of its own.
- *Combined Condition* is a composite, not a concept with its own behavior — it bundles basic condition instances under one name; its constituents carry all behavior including independent supersession and resolution.
- Supersession applies by severity chain regardless of source. Source determines removal behavior (same-source removes entirely), but a more severe condition always supersedes a less severe one regardless of which source imposed it.
- Dying fortitude progress tracking lives on *Imposed Conditions* — it is accumulation state tied to active-condition management on a character, not a property of the *Dying* condition instance itself.

---

# Boundary Domain

### **Effect**

_Owned by: Power_

effect rank                 | (integer)
                            |   invariant: resistance check DC = 10 + effect rank
resist                      | Character, Trait, Graded Check Result

### **Character**

_Owned by: Character Construction_

traits                      | Trait
applied effects             | Applied Effect
imposed conditions          | Imposed Conditions
make check                  | Check, Trait

### references

**Ref — Resistance and Ongoing Effects**
Source: context/rules/HeroesHandbook-rules__chunk_209.md
Locator: lines 14791–14830
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_209.md lines 14791–14830)
```

**Ref — Attack Checks**
Source: context/rules/HeroesHandbook-rules__chunk_016.md
Locator: lines 1195–1237
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_016.md lines 1195–1237)
```

**Ref — The Gamemaster**
Source: context/rules/HeroesHandbook-rules__chunk_006.md
Locator: lines 285–335
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_006.md lines 285–335)
```

### decisions made

- *Effect / Power Effect* (domain sketch slash term) resolved to *Effect* in all CRC headings — canonical CRC name is *Effect*; "Power Effect" is a qualifying descriptor, not a second concept.
- *Effect* is a boundary class owned by the Power module — it defines the effect rank and the `resist` entry point. It does not own the condition lifecycle; that belongs to *Applied Effect* in the core domain.
- *Effect* no longer owns `imposed condition` — the conditions that result from failing a resistance check are the *Character*'s concern via *Applied Effect* and *Imposed Conditions*, not a property of *Effect* itself.
- *Character* is a boundary class owned by Character Construction — it participates in check resolution (has traits, makes checks, carries applied effects and imposed conditions) but its construction and power-point accounting are out of scope here.

---
