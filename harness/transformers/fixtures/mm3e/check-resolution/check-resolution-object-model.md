---
state: domain-model
---

# Module: [Check Resolution]

_Typed object model for the d20 resolution mechanic, checks, degrees, conditions, and rank-to-measure translation. Primary input: `check-resolution-crc.md`. Every CRC collaborator is accounted for in a parameter, return type, property type, or Interaction block._

Scope: The d20 resolution mechanic (roll + modifier vs DC), checks (routine, opposed, team), degrees of success/failure, the Rank/Measure table, and conditions (basic, combined, imposed).

---

# Core Domain

## **Trait**

`Trait` is an entity: two traits with the same rank on different characters are distinct. `MEASUREMENT_TYPE` is a pre-defined enum used by `Measurement` and `Trait`. `Measurement` is a service: pure static lookup and rank-arithmetic operations with no instance state.

### **Trait** << Entity >>

+ Trait(character: Character, purchasedRank: Integer)
+ Trait(character: Character, purchasedRank: Integer, circumstanceModifier: Integer)
------
+ character: Character
+ traitName: String
+ purchasedRank: Integer
----
+ effectiveRank(): Integer
	Invariant: effectiveRank = purchasedRank minus the sum of active game modifier amounts targeting this trait from the character's imposed conditions
	Interaction:
		penalty: Integer = conditionPenalty()
		return purchasedRank - penalty

- conditionPenalty(): Integer
	Invariant: sum of game modifier amounts on active imposed conditions whose modifier applies to this trait's name; returns 0 when no active conditions target this trait
	Interaction:
		total: Integer = 0
		for each imposed in character.imposedConditions.activeConditions():
			if imposed.condition.gameModifier.appliesTo == this.traitName:
				total = total + imposed.condition.gameModifier.amount
		return total

+ realWorldValue(type: MEASUREMENT_TYPE): Number
	Invariant: delegates to Measurement table; values at higher ranks are approximate guidelines, not precise calculations
	Interaction:
		return Measurement.lookup(rank: effectiveRank(), type: type)

+ addRank(other: Integer, type: MEASUREMENT_TYPE): Integer
	Invariant: ranks must never be added directly — convert to measures, add measures, convert back to a rank
	Interaction:
		thisMeasure: Number = Measurement.lookup(rank: effectiveRank(), type: type)
		otherMeasure: Number = Measurement.lookup(rank: other, type: type)
		combined: Number = thisMeasure + otherMeasure
		return Measurement.rankFor(measure: combined, type: type)

+ performCheck(dc: DifficultyClass): CheckResult
	Invariant: creates and resolves a Check using this trait and the given DC
	Interaction:
		check: Check = new Check(trait: this, dc: dc)
		return check.resolve()

### **MEASUREMENT_TYPE** << ValueObject >>

Initialisation: pre-defined constants; no constructor
------
MASS : Integer = 1
TIME : Integer = 2
DISTANCE : Integer = 3
VOLUME : Integer = 4

### **Measurement** << Service >>

Initialisation: static methods; no instance state; no constructor
------
+ lookup(rank: Integer, type: MEASUREMENT_TYPE): Number
	Invariant: returns the real-world value for the given rank in the given dimension; values at higher ranks are approximate guidelines

+ rankFor(measure: Number, type: MEASUREMENT_TYPE): Integer
	Invariant: returns the rank whose real-world value is nearest to the given measure in the given dimension

+ throwingDistanceRank(strengthRank: Integer, massRank: Integer): Integer
	Invariant: throwingDistanceRank = strengthRank − massRank via measure arithmetic
	Interaction:
		strengthMeasure: Number = lookup(rank: strengthRank, type: DISTANCE)
		massMeasure: Number = lookup(rank: massRank, type: DISTANCE)
		combined: Number = strengthMeasure - massMeasure
		return rankFor(measure: combined, type: DISTANCE)

+ travelDistanceRank(timeRank: Integer, speedRank: Integer): Integer
	Invariant: travelDistanceRank = timeRank + speedRank via measure arithmetic
	Interaction:
		timeMeasure: Number = lookup(rank: timeRank, type: TIME)
		speedMeasure: Number = lookup(rank: speedRank, type: DISTANCE)
		combined: Number = timeMeasure + speedMeasure
		return rankFor(measure: combined, type: DISTANCE)

+ travelTimeRank(distanceRank: Integer, speedRank: Integer): Integer
	Invariant: travelTimeRank = distanceRank − speedRank via measure arithmetic
	Interaction:
		distanceMeasure: Number = lookup(rank: distanceRank, type: DISTANCE)
		speedMeasure: Number = lookup(rank: speedRank, type: DISTANCE)
		combined: Number = distanceMeasure - speedMeasure
		return rankFor(measure: combined, type: TIME)

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

- `Rank` is not a separate class — it is an `Integer` carried by `Trait`. All rank logic (measurement lookup, rank arithmetic, penalty calculation) lives on `Trait` or `Measurement`. The CRC decision is preserved here.
- `MEASUREMENT_TYPE` is a typed enum constant block, not a parenthetical value or a set of subtypes — the four dimensions all share the same doubling-scale lookup and rank-arithmetic rules.
- `Measurement` is a `<< Service >>` — purely static lookup methods with no instance state. The "per-dimension" lookup (CRC: `dimension type | MEASUREMENT_TYPE`) is a parameter to each method, not an instance property.
- `traitName: String` added to `Trait` — needed by `ImposedConditions.penaltyFor()` and `conditionPenalty()` to match which trait a `GameModifier` targets. Concrete trait subtypes from other modules (Ability, Defense, Skill) will provide a canonical name.
- `conditionPenalty()` is a private helper — extracted because the traversal logic (character → imposedConditions → active conditions → game modifier) is a discrete concern within `effectiveRank()`.
- `addRank(other, type)` takes an explicit `type` parameter — the domain sketch notes that rank arithmetic is dimension-specific (distance, time, etc.); the caller specifies which dimension to convert through.
- `Trait.performCheck()` creates a standard `Check`; for graded resolution (resistance) the caller uses `Check.resolveGraded()` on the returned or constructed check object. This avoids overloading `performCheck` with a graded/non-graded flag.

---

## **Check**

`Check` is an entity — each resolution event is a distinct occurrence with its own identity and outcome. `CheckResult` and `GradedCheckResult` are value objects: the outcome is fully defined by its values. `DifficultyClass` is a value object holding just a threshold integer. Three subtypes vary only how the roll total or DC is derived; the core resolution contract (`rollTotal vs dc.value`) is never changed.

### **Check** << Entity >>

+ Check(trait: Trait, dc: DifficultyClass)
+ Check(trait: Trait, dc: DifficultyClass, circumstanceModifier: Integer)
------
+ trait: Trait
+ dc: DifficultyClass
+ circumstanceModifier: Integer
----
+ resolve(): CheckResult
	Invariant: shape is always rollTotal vs dc.value; subtypes vary only how total or DC is produced
	Interaction:
		roll: Integer = rollD20()
		total: Integer = trait.effectiveRank() + roll + circumstanceModifier
		isCritical: Boolean = roll == 20
		isSuccess: Boolean = total >= dc.value
		margin: Integer = total - dc.value
		result: CheckResult = new CheckResult(rollTotal: total, dc: dc, isSuccess: isSuccess, margin: margin, isCritical: isCritical)
		return result

+ resolveGraded(): GradedCheckResult
	Invariant: same resolution as resolve(); additionally computes degree from margin; critical adds one degree of success after normal calculation
	Interaction:
		baseResult: CheckResult = resolve()
		degree: Integer = computeDegree(margin: baseResult.margin, isCritical: baseResult.isCritical, isSuccess: baseResult.isSuccess)
		return new GradedCheckResult(rollTotal: baseResult.rollTotal, dc: dc, isSuccess: baseResult.isSuccess, margin: baseResult.margin, isCritical: baseResult.isCritical, degree: degree, resultingCondition: null)

- rollD20(): Integer
	Invariant: produces a uniformly random integer from 1 to 20 inclusive

- computeDegree(margin: Integer, isCritical: Boolean, isSuccess: Boolean): Integer
	Invariant: base 1; +1 for each full 5 points of margin; maximum 4; if isCritical, add 1 after normal calculation (can upgrade 1 degree of failure to 1 degree of success, flipping isSuccess); always clamp to 1–4

### **CheckResult** << ValueObject >>

+ CheckResult(rollTotal: Integer, dc: DifficultyClass, isSuccess: Boolean, margin: Integer, isCritical: Boolean)
------
+ rollTotal: Integer
+ dc: DifficultyClass
+ isSuccess: Boolean
	Invariant: isSuccess when rollTotal ≥ dc.value; failure when below
+ margin: Integer
+ isCritical: Boolean
	Invariant: true only when the raw d20 roll was exactly 20

### **GradedCheckResult : CheckResult** << ValueObject >>

+ GradedCheckResult(rollTotal: Integer, dc: DifficultyClass, isSuccess: Boolean, margin: Integer, isCritical: Boolean, degree: Integer, resultingCondition: Condition)
------
+ degree: Integer
	Invariant: 1–4 combined with inherited isSuccess; if isCritical, degree is increased by one after normal calculation
+ resultingCondition: Condition
	Invariant: the condition imposed by this degree of failure; determined by the resisted effect's condition set; null when no condition maps to this degree or when isSuccess is true

### **DifficultyClass** << ValueObject >>

+ DifficultyClass(value: Integer)
------
+ value: Integer
	Invariant: 0 ≤ value ≤ 40 on the standard benchmark scale; higher values are valid for exceptional circumstances

### **OpposedCheck : Check** << Entity >>

+ OpposedCheck(trait: Trait, opponent: Character, isPassive: Boolean)
------
+ opponent: Character
+ isPassive: Boolean
----
+ resolve(): CheckResult
	Invariant: passive — DC = opponent modifier + 10, opponent does not roll; active — both characters roll, higher rollTotal wins; tie resolved by bonus then d20
	Interaction:
		if isPassive:
			passiveDc: DifficultyClass = new DifficultyClass(opponent.traitMatching(this.trait).effectiveRank() + 10)
			passiveCheck: Check = new Check(trait: this.trait, dc: passiveDc, circumstanceModifier: this.circumstanceModifier)
			return passiveCheck.resolve()
		opposingCheck: Check = new Check(trait: opponent.traitMatching(this.trait), dc: new DifficultyClass(0))
		opposingResult: CheckResult = opposingCheck.resolve()
		activeDc: DifficultyClass = new DifficultyClass(opposingResult.rollTotal)
		activeCheck: Check = new Check(trait: this.trait, dc: activeDc, circumstanceModifier: this.circumstanceModifier)
		activeResult: CheckResult = activeCheck.resolve()
		if activeResult.margin != 0: return activeResult
		return resolveTie(activeResult: activeResult, opposingResult: opposingResult)

- resolveTie(activeResult: CheckResult, opposingResult: CheckResult): CheckResult
	Invariant: higher trait effectiveRank wins; if ranks are equal, a new d20 decides (1–10 active character wins, 11–20 opposing character wins)

### **RoutineCheck : Check** << Entity >>

+ RoutineCheck(trait: Trait, dc: DifficultyClass)
+ RoutineCheck(trait: Trait, dc: DifficultyClass, circumstanceModifier: Integer)
------
+ resolve(): CheckResult
	Invariant: substitutes 10 for the d20; all trait rank and circumstance modifiers still apply; if routine total < DC returns failure and the caller may create a standard Check to roll instead
	Interaction:
		total: Integer = trait.effectiveRank() + 10 + circumstanceModifier
		isSuccess: Boolean = total >= dc.value
		margin: Integer = total - dc.value
		return new CheckResult(rollTotal: total, dc: dc, isSuccess: isSuccess, margin: margin, isCritical: false)

### **TeamCheck : Check** << Entity >>

+ TeamCheck(trait: Trait, dc: DifficultyClass, helpers: List<Character>)
------
+ helpers: List<Character>
----
+ resolve(): CheckResult
	Invariant: helpers roll same trait vs DC 10 first; their results produce a circumstance modifier added to the leader's check; only the leader's rollTotal determines the final outcome
	Interaction:
		helperModifier: Integer = computeHelperModifier()
		adjustedCircumstanceModifier: Integer = this.circumstanceModifier + helperModifier
		leaderCheck: Check = new Check(trait: this.trait, dc: this.dc, circumstanceModifier: adjustedCircumstanceModifier)
		return leaderCheck.resolve()

- computeHelperModifier(): Integer
	Invariant: 1–2 helper successes → +2; 3 or more helper successes → +5; any helper failure may impose −2; net modifier applied once to leader's check
	Interaction:
		successCount: Integer = 0
		hasFailure: Boolean = false
		for each helper in helpers:
			helperTrait: Trait = helper.traitMatching(this.trait)
			helperCheck: Check = new Check(trait: helperTrait, dc: new DifficultyClass(10))
			helperResult: CheckResult = helperCheck.resolve()
			if helperResult.isSuccess: successCount = successCount + 1
			else: hasFailure = true
		if successCount >= 3: return 5
		if successCount >= 1: return 2
		if hasFailure: return -2
		return 0

### references

**Ref — Ch1 The Basics**
Source: context/rules/HeroesHandbook-rules__chunk_005.md
Locator: lines 244–284
Extract: whole

```source
(verbatim from HeroesHandbook-rules__chunk_005.md lines 244–284)
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

- `Check` is an `<< Entity >>` — each resolution event is a distinct occurrence; two checks with identical attributes on the same character at different moments are different check events.
- `CheckResult` and `GradedCheckResult` are `<< ValueObject >>` — the outcome is fully defined by its values; two results with identical rollTotal, dc, isSuccess, margin, and isCritical are interchangeable.
- `rollD20()` is a private helper on `Check` — the d20 is the instrument the check uses; it is not a collaborating class but an internal operation. `computeDegree()` is extracted as a named private helper because degree calculation with critical upgrade logic is non-trivial; naming it after the invariant keeps `resolveGraded()` high-level.
- `Check.resolveGraded()` produces a `GradedCheckResult` with `resultingCondition: null` — the condition mapping is the Effect's responsibility, performed by `AppliedEffect.resist()` after receiving the graded result. This preserves the separation of concerns between the resolution mechanic and the condition-assignment logic.
- `OpposedCheck` takes `isPassive: Boolean` in the constructor — the passive vs active mode is set at creation time (the caller decides whether the opponent is actively contesting). The `resolve()` override branches on this flag and calls `resolveTie()` for active ties.
- `resolveTie()` is a private extracted helper — it represents a domain rule ("higher bonus wins; equal bonus uses d20") that is distinct enough to name and isolate from the main `resolve()` interaction.
- `RoutineCheck` returns a failure `CheckResult` with `isCritical: false` when the routine total is insufficient — it does not auto-fall-back to a standard roll; the caller decides whether to issue a new `Check.resolve()`. The domain rule "the player may still roll" is a player choice, not an automatic branch inside `RoutineCheck`.
- `Resistance Check` is not a class — it is a `Check` (or its `GradedCheckResult` variant) instantiated with a defense `Trait` and an `Effect`-provided `DifficultyClass` by `AppliedEffect.resist()`.
- `TeamCheck.computeHelperModifier()` is a private extracted helper — the helper-loop, success count, and ±modifier branching logic constitutes a discrete domain rule that would obscure `resolve()` if inlined.
- `DifficultyClass.value` is constrained to 0–40 on the standard benchmark scale; higher values are permitted for exceptional circumstances (e.g., ongoing effect DCs exceeding the normal ladder).

---

## **Condition**

`Condition` is a value object — two dazed conditions are interchangeable. `GameModifier` and `ConditionSource` are value objects. `ImposedCondition` is an entity — each application to a specific character at a specific time from a specific source is a distinct occurrence. `ImposedConditions` is an entity owned by `Character`; it manages all supersession logic and dying-progress tracking. `AppliedEffect` is an entity that links an `Effect` to the conditions it imposed; it owns the ongoing-resistance lifecycle.

### **Condition** << ValueObject >>

Initialisation: pre-defined instances (DAZED, STUNNED, IMPAIRED, DISABLED, VULNERABLE, DEFENSELESS, HINDERED, IMMOBILE, COMPELLED, CONTROLLED, WEAKENED, DEBILITATED, FATIGUED, TRANSFORMED, UNAWARE, NORMAL)
------
+ name: String
+ gameModifier: GameModifier
+ supersedes: Condition
	Invariant: the supersession chain is navigable through Condition data — supersedes and supersededBy are properties, not a separate runtime object
+ supersededBy: Condition

### **GameModifier** << ValueObject >>

+ GameModifier(appliesTo: String, amount: Integer)
------
+ appliesTo: String
	Invariant: names the trait type this modifier targets; null or empty means the modifier applies to all checks
+ amount: Integer
	Invariant: negative values impose a penalty; positive values grant a bonus

### **ConditionSource** << ValueObject >>

+ ConditionSource(identity: String)
------
+ identity: String
	Invariant: two imposed conditions sharing the same identity are evaluated under same-source supersession rules; different identities use different-source rules

### **ImposedCondition** << Entity >>

+ ImposedCondition(condition: Condition, source: ConditionSource)
------
+ condition: Condition
+ source: ConditionSource
+ isActive: Boolean
	Invariant: only an active imposed condition applies its game modifier to the character
+ blockingCondition: ImposedCondition
	Invariant: set when this condition is parked inactive by a more severe condition from a different source; null when the condition is active or unblocked
----
+ activate(): void
	Invariant: sets isActive to true and clears blockingCondition; called when the blocking condition is removed and this condition's source is still in effect
	Interaction:
		isActive = true
		blockingCondition = null

+ deactivate(blocker: ImposedCondition): void
	Invariant: sets isActive to false and records the blocking condition; called when a more severe condition from a different source supersedes this one
	Interaction:
		isActive = false
		blockingCondition = blocker

### **ImposedConditions** << Entity >>

+ ImposedConditions()
------
+ << composition >> appliedConditions: List<ImposedCondition>
+ dyingSuccessCount: Integer
+ dyingFailureCount: Integer
----
+ activeConditions(): List<ImposedCondition>
	Invariant: returns only the imposed conditions whose isActive is true
	Interaction:
		return appliedConditions filtered by imposed.isActive == true

+ applyCondition(condition: Condition, source: ConditionSource): void
	Invariant: same-source more severe → remove less severe, add new as active; same-source less severe → no change; different-source more severe → new active, existing becomes inactive; different-source less severe → add as inactive
	Interaction:
		sameSourceActive: ImposedCondition = findActiveBySameSource(source: source)
		if sameSourceActive is not null:
			if incomingSupersedes(existing: sameSourceActive, incoming: condition):
				appliedConditions.remove(sameSourceActive)
				newImposed: ImposedCondition = new ImposedCondition(condition: condition, source: source)
				appliedConditions.add(newImposed)
			// else: same-source less severe → no change
		else:
			newImposed: ImposedCondition = new ImposedCondition(condition: condition, source: source)
			differentSourceActive: ImposedCondition = findActiveInSupersessionChain(condition: condition)
			if differentSourceActive is not null:
				if incomingSupersedes(existing: differentSourceActive, incoming: condition):
					differentSourceActive.deactivate(blocker: newImposed)
				else:
					newImposed.deactivate(blocker: differentSourceActive)
			appliedConditions.add(newImposed)

- incomingSupersedes(existing: ImposedCondition, incoming: Condition): Boolean
	Invariant: returns true when incoming.supersedes == existing.condition; returns false when existing.condition.supersedes == incoming

- findActiveBySameSource(source: ConditionSource): ImposedCondition
	Invariant: returns the first active imposed condition whose source.identity matches; null if none

- findActiveInSupersessionChain(condition: Condition): ImposedCondition
	Invariant: returns any currently active imposed condition that is in the same supersession chain as the incoming condition; null if none

+ penaltyFor(trait: Trait): Integer
	Invariant: sum of game modifier amounts from active imposed conditions whose modifier targets the given trait; all active conditions stack
	Interaction:
		total: Integer = 0
		for each imposed in activeConditions():
			if imposed.condition.gameModifier.appliesTo == null or imposed.condition.gameModifier.appliesTo == trait.traitName:
				total = total + imposed.condition.gameModifier.amount
		return total

+ revealBlockedConditions(removedBlocker: ImposedCondition): void
	Invariant: when a blocking condition is removed, every condition it was blocking becomes active if its source is still in effect
	Interaction:
		for each imposed in appliedConditions:
			if imposed.blockingCondition == removedBlocker:
				imposed.activate()

+ remove(imposed: ImposedCondition): void
	Invariant: removes the given imposed condition from the collection; if it was a blocker, reveals any conditions it was blocking
	Interaction:
		appliedConditions.remove(imposed)
		revealBlockedConditions(removedBlocker: imposed)

+ recordDyingFortitudeResult(result: GradedCheckResult): String
	Invariant: accumulates degrees of success and failure across rounds; 2 accumulated successes → STABILIZED; 3 accumulated failures → DEAD; otherwise ALIVE
	Interaction:
		if result.isSuccess:
			dyingSuccessCount = dyingSuccessCount + result.degree
		else:
			dyingFailureCount = dyingFailureCount + result.degree
		if dyingSuccessCount >= 2: return "STABILIZED"
		if dyingFailureCount >= 3: return "DEAD"
		return "ALIVE"

### **CombinedCondition** << ValueObject >>

Initialisation: pre-defined instances (STAGGERED, INCAPACITATED, DYING, EXHAUSTED, ASLEEP, BLIND, BOUND, DEAF, ENTRANCED, PARALYZED, PRONE, RESTRAINED, SURPRISED)
------
+ name: String
+ << composition >> constituents: List<Condition>
	Invariant: each constituent may be superseded or resolved independently while the combined condition name persists

### **AppliedEffect** << Entity >>

+ AppliedEffect(effect: Effect, character: Character)
------
+ effect: Effect
+ character: Character
+ isOngoing: Boolean
	Invariant: when false, all imposed conditions created by this effect have been removed from the character
+ << composition >> imposedConditions: List<ImposedCondition>
	Invariant: tracks every imposed condition this effect created on the character
----
+ resist(defenseTrait: Trait): GradedCheckResult
	Invariant: DC = 10 + effect.rank; on success — effect ends and all its conditions are removed; on failure — conditions persist and further conditions may be added per the effect's degree mapping
	Interaction:
		resistanceDc: DifficultyClass = new DifficultyClass(effect.effectDc())
		resistanceCheck: Check = new Check(trait: defenseTrait, dc: resistanceDc)
		gradedResult: GradedCheckResult = resistanceCheck.resolveGraded()
		resultingCondition: Condition = effect.conditionFor(degree: gradedResult.degree, isSuccess: gradedResult.isSuccess)
		fullResult: GradedCheckResult = new GradedCheckResult(rollTotal: gradedResult.rollTotal, dc: resistanceDc, isSuccess: gradedResult.isSuccess, margin: gradedResult.margin, isCritical: gradedResult.isCritical, degree: gradedResult.degree, resultingCondition: resultingCondition)
		if fullResult.isSuccess:
			end()
		else if resultingCondition is not null:
			character.imposedConditions.applyCondition(condition: resultingCondition, source: new ConditionSource(effect.name))
			imposedConditions.add(character.imposedConditions.findActiveBySameSource(source: new ConditionSource(effect.name)))
		return fullResult

+ end(): void
	Invariant: sets isOngoing to false; removes all imposed conditions this effect created from the character's ImposedConditions
	Interaction:
		for each imposed in imposedConditions:
			character.imposedConditions.remove(imposed: imposed)
		imposedConditions.clear()
		isOngoing = false

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

- `Condition` is a `<< ValueObject >>` — the named conditions (DAZED, STUNNED, etc.) are pre-defined instances; two DAZED conditions are identical. Supersession chain is held as properties on `Condition` itself, not via a runtime structure.
- `GameModifier` is a `<< ValueObject >>` — the modifier is fully defined by its `appliesTo` scope and `amount`. `appliesTo: String` is nullable (null = applies to all checks); concrete trait subtypes in other modules supply the canonical name string.
- `ImposedCondition` is an `<< Entity >>` — each application of a condition to a character from a specific source is a distinct tracked occurrence with its own active/inactive lifecycle.
- `ImposedConditions` is an `<< Entity >>` composition-owned by `Character` — it owns all supersession logic. Three private helpers extracted: `incomingSupersedes`, `findActiveBySameSource`, `findActiveInSupersessionChain` — each names a specific domain rule, keeping `applyCondition()` readable.
- `remove()` on `ImposedConditions` automatically calls `revealBlockedConditions()` — when any condition is removed (by source end or supersession), blocked conditions must be revealed in the same call to preserve invariant integrity.
- `AppliedEffect` is an `<< Entity >>` in the Core Domain, not a boundary class — it emerged from the condition-lifecycle requirement that conditions track which effect imposed them and are removed when that effect ends. This logic is owned here, not on the boundary `Effect`.
- `AppliedEffect.resist()` constructs the final `GradedCheckResult` with `resultingCondition` populated — the condition mapping belongs to `Effect.conditionFor()`, and the result object must carry the condition per the CRC. The graded result from `Check.resolveGraded()` has null condition; `resist()` enriches it.
- `recordDyingFortitudeResult` returns a `String` ("ALIVE", "STABILIZED", "DEAD") — a `DyingOutcome` enum could replace this in production code; the domain model uses a string for readability.
- `CombinedCondition.constituents` uses `<< composition >>` — the combined condition name owns the constituent list; the list has no identity outside the combined condition.
- `Dying` fortitude tracking (`dyingSuccessCount`, `dyingFailureCount`) lives on `ImposedConditions` — it is accumulation state tied to active-condition management on a character, not a property of the `Dying` condition instance.

---

# Boundary Domain

### **Effect** << Entity >>

_Owned by: Power_

Initialisation: constructed and owned by the Power module; this module receives Effect instances as collaborators
------
+ name: String
+ rank: Integer
	Invariant: resistance check DC = 10 + rank
----
+ effectDc(): Integer
	Invariant: always 10 + rank
	Interaction:
		return 10 + rank

+ conditionFor(degree: Integer, isSuccess: Boolean): Condition
	Invariant: maps degree of failure to the condition this effect imposes at that degree, as defined by the effect's configuration; returns null when isSuccess is true or when no condition is defined for the given degree

### **Character** << Entity >>

_Owned by: Character Construction_

Initialisation: constructed and owned by the Character Construction module
------
+ << aggregation >> traits: List<Trait>
+ << composition >> imposedConditions: ImposedConditions
+ << composition >> appliedEffects: List<AppliedEffect>
----
+ traitMatching(other: Trait): Trait
	Invariant: returns this character's trait whose traitName matches other.traitName
	Interaction:
		return traits where trait.traitName == other.traitName

+ makeCheck(dc: DifficultyClass, trait: Trait): CheckResult
	Invariant: creates and resolves a Check using the given trait and DC
	Interaction:
		return trait.performCheck(dc: dc)

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

- `Effect.conditionFor()` is an operation not a data property — the condition mapping is defined by the Power module's effect configuration; this module only calls it. The signature declares the contract (degree → Condition or null) without specifying how the mapping is stored.
- `Effect.name: String` added — needed by `AppliedEffect.resist()` to construct a `ConditionSource` identity token that associates conditions with this specific effect instance.
- `Character.traits` uses `<< aggregation >>` — traits have their own identity and lifecycle; character groups them but does not own their existence.
- `Character.imposedConditions` uses `<< composition >>` — `ImposedConditions` has no identity or lifecycle outside the character it belongs to.
- `Character.traitMatching()` is the bridge between `OpposedCheck`/`TeamCheck` (which need the opponent's or helper's matching trait) and the `Trait` typed surface. This keeps the matching concern on `Character` rather than leaking trait-name lookups into the check subtypes.

---
