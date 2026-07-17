# checks

Resolves Mutants & Masterminds checks: d20 + trait rank + modifiers against difficulty, including opposed, comparison, routine, critical success, and team assist.

## Seam

The seam is `Check` / `OpposedCheck.resolve` and `TeamCheck.add_helper` / `assist`. Callers pass modifiers (and optional resolve modes); they get `CheckResult`, a visible `die_roll`, or a leader `Modifier` from team assist. This module owns dice resolution, degree math, critical success, routine and routine-opposition modes, opposed/comparison tie-break, and team-degree → circumstance mapping.

Constraint: construct `Check` with `trait` and `difficulty_class` (`opposing_trait` for opposed); optional `dice` defaults to 1d20 — pass a stub/mock dice in tests (e.g. always returns 20). Never pass trait/DC into `resolve`. This module owns check totals via the constructed dice. `routine` / `comparison` / `routine_opposition` are resolve flags, not construction. `TeamCheck` helpers are external objects that own a `trait` (e.g. Character later) — not defined in this module; `assist` only reads `helper.trait`. Attack checks stay outside (combat). `Trait.rank` comes from the `measurement` module.

## Public API

### Check

Callers construct with trait, difficulty class, and optional `dice` (default 1d20), call `resolve(modifiers, routine=False)`, and read `die_roll` plus `CheckResult`. Owns critical success (natural 20 → +1 degree) and routine (die treated as 10).

### OpposedCheck

Same construction as `Check`, plus `opposing_trait`. `resolve` supports comparison (rank vs rank), routine opposition (DC = opposing rank + 10), or a transient opposing check then `super().resolve`, including handbook tie-breaks.

### TeamCheck

Callers `add_helper` external helpers, then `assist` to get a circumstance `Modifier` for the leader’s `resolve`. Helpers own their traits; this type only orchestrates DC-10 helper checks and degree stacking.

Supporting types: `Trait`, `Modifier`, `DifficultyClass`, `CheckResult`.

## Dependencies

Depends on `measurement` for `Rank` (on `Trait`). Expects external helpers (later Character) to expose `trait` for team checks. Later combat modules may use `Check` but attack-specific rules are not owned here. Does not depend on character sheets, powers catalog, or session/scenes.
