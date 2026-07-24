# Resolve Checks

**Status:** specification

**Stories in scope:**
- *Resolve Ability Check*

**Example factories (CE — via `resolve-checks-helper.js`):**
- `CheckExampleFactory` — `loadStrengthCheckFaceEight`, `loadStrengthCheckFailsFaceOne`, `loadCriticalNaturalTwentyNearMiss`, `loadRoutineStrengthCheck`
- `CheckResultExampleFactory` — matching expected outcomes
- `AbilityExampleFactory`, `TraitExampleFactory`, `DifficultyClassExampleFactory`

**Scenarios (specification):**
- Happy path success (face 8 / rank 5 / DC 10 → total 13, degree 1) — from `check.spec.js`
- Failure (face 1 → degree -1)
- Natural 20 critical flips near miss (rank 0 / DC 21)
- Routine check treats die as 10

**Context / notes:** Helper loads Check / peers from factories (fake mode for explore/spec). Check constructed with Trait (Ability), DifficultyClass, optional dice. Resolve returns CheckResult; die_roll is visible on Check. Opposed / team checks out of Increment 1 scope.
