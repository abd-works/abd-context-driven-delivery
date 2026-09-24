# tldraw prompt — Check Resolution class diagram

Paste the section below (everything inside the `==== PROMPT ====` block) into the tldraw AI panel. The prompt is fully self-contained: every class, property, operation, invariant, and edge is listed inline. The tldraw AI does not need to read any other file.

If you want to iterate, ask tldraw to build **one frame at a time** in this order: `Trait` → `Check` → `Condition`. Each frame is independent.

---

==== PROMPT ====

You are drafting a UML class diagram for the **Check Resolution** module of a tabletop RPG. Build it as **three labeled frames** on a single tldraw canvas — one frame per Key Abstraction. Frames sit side-by-side with ~200px gap. Inside each frame, render classes as **3-compartment UML boxes** and connect them with the relationship arrows specified below.

## Rendering conventions

Every class is a rectangle ~280–440px wide with three horizontal dividers, producing four stacked compartments:

1. **Header** — centered: italic stereotype on line 1 (e.g. `«Entity»`), bold class name on line 2.
2. **Properties** — one per line, left-aligned, format `+ name: Type` or `- name: Type` (`+` public, `-` private).
3. **Operations** — one per line, format `+ method(arg: Type, …): ReturnType`.
4. **Invariants** — small italic gray text, one rule per line.

Use a small font (10–11px) inside compartments so all rows fit without wrapping. Header font 12–13px bold.

### Imported classes (cross-KA ancestors / boundary types)

A class belonging to a different Key Abstraction must render with:

- **Dashed border** (light gray stroke).
- Header stereotype `«from: <Source KA Name>»` instead of `«Entity»` / `«ValueObject»`.
- Light-gray fill or muted text color.
- Only the properties/operations actually used on this page — do not duplicate the full home-KA detail.

### Edge styles

| Relationship | Line | Arrowhead at target | Label |
|---|---|---|---|
| Inheritance (`Child : Parent`) | solid | hollow triangle | none |
| Composition (`«composition»`) | solid | filled diamond at **owner end** + open arrow at part end | none |
| Aggregation (`«aggregation»`) | solid | hollow diamond at owner end + open arrow at part end | none |
| Association (uses-a, holds-a) | solid | open arrow | optional role name |
| Dependency (creates / uses transiently) | **dashed** | open arrow | `«creates»` or `«uses»` |

### Layout rules (apply on every frame)

1. **Base classes above derived classes.** Parent classes get the lowest y-values; children sit below. Sibling subclasses share the same y-row.
2. **Cross-KA ancestors at the top.** Any imported class (dashed border) is positioned in the top band of its frame so the reader sees the full ancestry chain without leaving the page.
3. **Distinct anchor points.** When more than one edge enters or leaves the **same side** of a class, give each a distinct attachment point along that side (e.g. spread three children entering the bottom of a parent at 25%, 50%, 75% of the bottom edge). Edges must read as separate lines, never stacked.
4. **No edge crosses through an unrelated class.** Route orthogonally around any class boxes between source and target. If you cannot route cleanly, move the obstructing class.

---

## Frame 1 — `Trait` (Core Domain)

Suggested frame size: 1000×700.

### Imported (top band, dashed)

**Character** — `«from: Character Construction»` — pos top-right.
- Properties: `+ traits: List<Trait>`, `+ imposedConditions: ImposedConditions`

### Local classes

**Trait** — `«Entity»` — top-left, base class of the frame.
- Properties:
  - `+ character: Character`
  - `+ traitName: String`
  - `+ purchasedRank: Integer`
- Operations:
  - `+ effectiveRank(): Integer`
  - `- conditionPenalty(): Integer`
  - `+ realWorldValue(type: MEASUREMENT_TYPE): Number`
  - `+ addRank(other: Integer, type: MEASUREMENT_TYPE): Integer`
  - `+ performCheck(dc: DifficultyClass): CheckResult`
- Invariants:
  - *effectiveRank = purchasedRank − sum of active condition penalties on this trait*
  - *ranks must never be added directly — convert to measures, add, convert back*

**MEASUREMENT_TYPE** — `«ValueObject»` — bottom-left.
- Properties (constants):
  - `MASS: Integer = 1`
  - `TIME: Integer = 2`
  - `DISTANCE: Integer = 3`
  - `VOLUME: Integer = 4`

**Measurement** — `«Service»` — bottom-right.
- Operations:
  - `+ lookup(rank: Integer, type: MEASUREMENT_TYPE): Number`
  - `+ rankFor(measure: Number, type: MEASUREMENT_TYPE): Integer`
  - `+ throwingDistanceRank(strengthRank: Integer, massRank: Integer): Integer`
  - `+ travelDistanceRank(timeRank: Integer, speedRank: Integer): Integer`
  - `+ travelTimeRank(distanceRank: Integer, speedRank: Integer): Integer`
- Invariant: *values at higher ranks are approximate guidelines*

### Edges

- `Trait` ─association→ `Character` (open arrow, role `character`).
- `Trait` ─dependency→ `Measurement` (dashed, label `«uses»`).
- `Measurement` ─association→ `MEASUREMENT_TYPE` (open arrow, label `type parameter`).

---

## Frame 2 — `Check` (Core Domain)

Suggested frame size: 1400×1200. This frame has the most classes — give it room.

### Imported (top band, dashed)

**Trait** — `«from: Trait»` — top-left.
- `+ purchasedRank: Integer`
- `+ effectiveRank(): Integer`

**Condition** — `«from: Condition»` — middle-right (used only by `GradedCheckResult.resultingCondition`).
- `+ name: String`
- `+ gameModifier: GameModifier`

**Character** — `«from: Character Construction»` — bottom-center.
- `+ traits: List<Trait>`
- `+ imposedConditions: ImposedConditions`
- `+ traitMatching(other: Trait): Trait`
- `+ makeCheck(dc: DifficultyClass, trait: Trait): CheckResult`

### Local classes — top tier (parents)

**Check** — `«Entity»` — center-top, the base of three subtypes.
- Properties:
  - `+ trait: Trait`
  - `+ dc: DifficultyClass`
  - `+ circumstanceModifier: Integer`
- Operations:
  - `+ resolve(): CheckResult`
  - `+ resolveGraded(): GradedCheckResult`
  - `- rollD20(): Integer`
  - `- computeDegree(margin: Integer, isCritical: Boolean, isSuccess: Boolean): Integer`
- Invariants:
  - *shape: rollTotal vs dc.value, always*
  - *raw d20 = 20 → adds one degree after normal calculation*

**DifficultyClass** — `«ValueObject»` — top-right of `Check`.
- `+ value: Integer`
- Invariant: *0 ≤ value ≤ 40 standard; higher values for exceptional circumstances*

### Local classes — middle tier (results, side of Check)

**CheckResult** — `«ValueObject»` — right side, mid-height.
- Properties:
  - `+ rollTotal: Integer`
  - `+ dc: DifficultyClass`
  - `+ isSuccess: Boolean`
  - `+ margin: Integer`
  - `+ isCritical: Boolean`
- Invariants:
  - *isSuccess when rollTotal ≥ dc.value*
  - *isCritical only when raw d20 was exactly 20*

**GradedCheckResult** — `«ValueObject»` — directly below `CheckResult`. Inherits `CheckResult`.
- `+ degree: Integer`
- `+ resultingCondition: Condition`
- Invariants:
  - *degree 1–4; if isCritical, degree increased by one*
  - *resultingCondition assigned by Effect.conditionFor()*

### Local classes — bottom tier (Check subtypes)

Place three subclasses side-by-side **below** `Check`, sharing the same y-row. From left to right:

**OpposedCheck : Check** — `«Entity»`.
- `+ opponent: Character`
- `+ isPassive: Boolean`
- Operations: `+ resolve(): CheckResult`, `- resolveTie(active: CheckResult, opposing: CheckResult): CheckResult`
- Invariants: *passive: DC = opponent modifier + 10*; *active: both roll, higher total wins*; *tie: higher bonus, then d20*

**RoutineCheck : Check** — `«Entity»`.
- Operations: `+ resolve(): CheckResult`
- Invariants: *substitutes 10 for d20*; *if routine total < DC, caller may choose to roll*

**TeamCheck : Check** — `«Entity»`.
- `+ helpers: List<Character>`
- Operations: `+ resolve(): CheckResult`, `- computeHelperModifier(): Integer`
- Invariants: *1–2 successes → +2; 3+ → +5; failure → −2*; *only leader's rollTotal determines outcome*

### Edges (Check frame)

Inheritance arrows (hollow triangle) — three children to one parent. Spread their entry points along the **bottom edge** of `Check` at x≈25%, 50%, 75%.

- `OpposedCheck` ─inheritance→ `Check`
- `RoutineCheck` ─inheritance→ `Check`
- `TeamCheck` ─inheritance→ `Check`
- `GradedCheckResult` ─inheritance→ `CheckResult`

Associations / properties (open arrow):

- `Check` ─association→ `Trait` (role `trait`).
- `Check` ─association→ `DifficultyClass` (role `dc`).
- `OpposedCheck` ─association→ `Character` (role `opponent`).
- `TeamCheck` ─association→ `Character` (role `helpers`, multiplicity `0..*`).
- `GradedCheckResult` ─association→ `Condition` (role `resultingCondition`, may be null).

Dependencies (dashed, label):

- `Check` ─«creates»→ `CheckResult` (dashed open arrow).
- Note: `Check.resolveGraded()` also creates `GradedCheckResult`; the inheritance edge already shows the type relation, so omit a second creates edge to keep the frame readable. Add an annotation note "`resolveGraded() creates GradedCheckResult`" near the inheritance arrow if space allows.

**Anchor discipline for `Check`:** because `Check` has 3 inheritance edges entering its bottom and 2 association edges exiting its top + 1 dashed creates edge exiting its right side, give each its own anchor:

- `Check` top-left → `Trait` (entering Trait at right, mid).
- `Check` top-right → `DifficultyClass` (entering DC at left, mid).
- `Check` right → `CheckResult` («creates» dashed).
- `Check` bottom-25% / 50% / 75% → three subtypes.

---

## Frame 3 — `Condition` (Core Domain + boundary)

Suggested frame size: 1500×1300.

### Imported (top band / sides, dashed)

**Trait** — `«from: Trait»` — left side, used by `ImposedConditions.penaltyFor()`.
- `+ traitName: String`
- `+ effectiveRank(): Integer`

**Character** — `«from: Character Construction»` — bottom-left.
- `+ «composition» imposedConditions: ImposedConditions`
- `+ «composition» appliedEffects: List<AppliedEffect>`

**Effect** — `«from: Power»` — bottom-right.
- `+ name: String`
- `+ rank: Integer`
- `+ effectDc(): Integer`
- `+ conditionFor(degree: Integer, isSuccess: Boolean): Condition`
- Invariant: *resistance check DC = 10 + rank*

**GradedCheckResult** — `«from: Check»` — bottom-right, near `AppliedEffect.resist()` return.
- `+ degree: Integer`
- `+ resultingCondition: Condition`

### Local classes — top tier (value objects)

**Condition** — `«ValueObject»` — center-top.
- `+ name: String`
- `+ gameModifier: GameModifier`
- `+ supersedes: Condition`
- `+ supersededBy: Condition`
- Invariant: *supersession chain navigable through Condition data*
- Note pinned to header: *pre-defined instances: DAZED, STUNNED, IMPAIRED, DISABLED, VULNERABLE, DEFENSELESS, HINDERED, IMMOBILE, COMPELLED, CONTROLLED, WEAKENED, DEBILITATED, FATIGUED, TRANSFORMED, UNAWARE, NORMAL*

**CombinedCondition** — `«ValueObject»` — top-left of `Condition`.
- `+ name: String`
- `+ «composition» constituents: List<Condition>`
- Invariant: *each constituent superseded/resolved independently*
- Note: *pre-defined instances: STAGGERED, INCAPACITATED, DYING, EXHAUSTED, ASLEEP, BLIND, BOUND, DEAF, ENTRANCED, PARALYZED, PRONE, RESTRAINED, SURPRISED*

**ConditionSource** — `«ValueObject»` — top-right of `Condition`.
- `+ identity: String`
- Invariant: *shared identity → same-source supersession rules*

**GameModifier** — `«ValueObject»` — left side, mid-height.
- `+ appliesTo: String`
- `+ amount: Integer`
- Invariants: *null appliesTo → applies to all checks*; *negative = penalty, positive = bonus*

### Local classes — middle tier (entities)

**ImposedCondition** — `«Entity»` — center-middle.
- Properties: `+ condition: Condition`, `+ source: ConditionSource`, `+ isActive: Boolean`, `+ blockingCondition: ImposedCondition`
- Operations: `+ activate(): void`, `+ deactivate(blocker: ImposedCondition): void`
- Invariant: *only an active imposed condition applies its game modifier*

**ImposedConditions** — `«Entity»` — center-lower (just below `ImposedCondition`).
- Properties:
  - `+ «composition» appliedConditions: List<ImposedCondition>`
  - `+ dyingSuccessCount: Integer`
  - `+ dyingFailureCount: Integer`
- Operations:
  - `+ activeConditions(): List<ImposedCondition>`
  - `+ applyCondition(condition: Condition, source: ConditionSource): void`
  - `+ penaltyFor(trait: Trait): Integer`
  - `+ revealBlockedConditions(removedBlocker: ImposedCondition): void`
  - `+ remove(imposed: ImposedCondition): void`
  - `+ recordDyingFortitudeResult(result: GradedCheckResult): String`
  - `- incomingSupersedes(existing: ImposedCondition, incoming: Condition): Boolean`
  - `- findActiveBySameSource(source: ConditionSource): ImposedCondition`
  - `- findActiveInSupersessionChain(condition: Condition): ImposedCondition`
- Invariants: *same-source more severe replaces; less severe ignored*; *different-source more severe supersedes (existing parked inactive)*; *different-source less severe added inactive*; *2 dying successes → STABILIZED; 3 dying failures → DEAD*

**AppliedEffect** — `«Entity»` — bottom-center, between `Character` and `Effect`.
- Properties: `+ effect: Effect`, `+ character: Character`, `+ isOngoing: Boolean`, `+ «composition» imposedConditions: List<ImposedCondition>`
- Operations: `+ resist(defenseTrait: Trait): GradedCheckResult`, `+ end(): void`
- Invariants: *on resist success → effect ends*; *when ended, removes all imposed conditions it created*

### Edges (Condition frame)

Compositions (filled diamond at owner):

- `CombinedCondition` ─composition→ `Condition` (constituents list).
- `ImposedConditions` ─composition→ `ImposedCondition` (appliedConditions list).
- `Character` (imported) ─composition→ `ImposedConditions`.
- `Character` (imported) ─composition→ `AppliedEffect` (appliedEffects list).
- `AppliedEffect` ─composition→ `ImposedCondition` (the conditions this effect imposed).

Associations (open arrow):

- `Condition` ─association→ `GameModifier` (role `gameModifier`).
- `Condition` ─association→ `Condition` (self-loop, role `supersedes` / `supersededBy`).
- `ImposedCondition` ─association→ `Condition` (role `condition`).
- `ImposedCondition` ─association→ `ConditionSource` (role `source`).
- `ImposedCondition` ─association→ `ImposedCondition` (self-loop, role `blockingCondition`).
- `ImposedConditions` ─association→ `Trait` (used by `penaltyFor(trait)`; route from left side of `ImposedConditions` to imported `Trait`).
- `AppliedEffect` ─association→ `Effect` (role `effect`).
- `AppliedEffect` ─association→ `Character` (role `character`).

Dependencies (dashed, label):

- `AppliedEffect` ─«creates»→ `GradedCheckResult` (return of `resist()`).

**Anchor discipline for `Condition`:** it has three association edges out (to `GameModifier` left, the self-loop, and to `ImposedCondition`/`ImposedConditions` below). Use distinct anchors:

- Bottom-30% → `ImposedCondition` (incoming from `ImposedCondition.condition`).
- Bottom-70% → self-loop bend right (`supersedes` / `supersededBy`).
- Left-mid → `GameModifier`.

**Anchor discipline for `ImposedCondition`:** four incoming/outgoing edges share its sides. Spread:

- Top → `Condition` (role `condition`).
- Top-right → `ConditionSource` (role `source`).
- Right (self) → self-loop `blockingCondition`.
- Bottom → composition diamond from `ImposedConditions`.

---

## Validation checklist (run mentally before declaring done)

- [ ] Every Key Abstraction is its own frame, named exactly `Trait`, `Check`, `Condition`.
- [ ] Every imported class has a dashed border and a `«from: <KA>»` stereotype.
- [ ] Every base class (and every imported class) sits at a lower y than its children on the same frame.
- [ ] Sibling subclasses share a y-row (e.g. `OpposedCheck`, `RoutineCheck`, `TeamCheck`).
- [ ] No two edges share the same anchor point on any class side. Multiple edges from `Check` (bottom: 3 children; top: 2 associations) and multiple edges around `ImposedCondition` and `Condition` use distinct anchors as listed.
- [ ] No edge route passes through a class box it is not connected to. Reroute orthogonally if needed.
- [ ] Inheritance arrows use a hollow triangle head; composition uses a filled diamond at the owner; aggregation uses a hollow diamond; dependencies are dashed and labeled `«creates»` / `«uses»`.

When done, take a screenshot of each frame so the human reviewer can verify the visual hierarchy, the dashed cross-KA imports, and the absence of stacked edges.

==== END PROMPT ====

---

## Notes for the human operator

- This prompt mirrors the structure produced by the `drawio-domain-sync` skill. The companion `.drawio` rendering at `check-resolution-class-diagram.drawio` is the authoritative visual reference if tldraw output drifts.
- The source of truth is `check-resolution-object-model.md` — if you change a class signature, update both that file and re-prompt tldraw (or hand-edit one frame at a time).
- If the tldraw AI cannot fit all four compartments in one shape, fall back to a single rectangle with multiline text and `---` as visual separators between header / props / ops / invariants.
