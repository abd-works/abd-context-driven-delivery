## Language

*Check* is how a trait is resolved against a difficulty class — d20 plus modifier, then optional grading, opposition, routine substitution, or helpers.

### Trait

- Supplies the modifier a check uses for a named trait on a character token.
- Asks *Measurement* for a real-world value and asks *Check* to resolve.
- **Invariant:** Ranks are never added as integers — convert through *Measurement* then convert back.

### Measurement

- Looks up a rank as a measure and converts combined ranks through that table.

### Check

- Owns d20 plus modifier versus difficulty class. Other modules ask *Trait.perform_check*.

### CheckResult

- Reports roll total, success, margin, and whether the face was a natural 20.

### GradedCheckResult

- Grades success or failure by degree, capped at four, and may name a resulting condition.
- **Invariant:** Degree never exceeds 4. After grading, a natural 20 increases degree by one.

### DifficultyClass

- Names the number a check must meet or beat.

### OpposedCheck

- Resolves two traits against each other, or one trait against a passive difficulty class of opponent modifier plus ten.

### RoutineCheck

- Substitutes ten for the die. Never critical.

### TeamCheck

- Helpers check difficulty class 10; only the leader's result decides the outcome.

### Condition

- Names a game modifier and the chain of more severe conditions that supersede it.

### ImposedCondition

- A condition from a source, active or parked.
- **Invariant:** Only active conditions apply modifiers.

### ImposedConditions

- Applies, supersedes, and removes conditions by source.
- **Invariant:** Same-source supersession removes the lesser; a different-source lesser stays parked inactive.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# checks
- **Purpose:** Resolve a trait check, apply and supersede conditions, and look up a rank as a measure.
- **Seam (terms):** Trait, Measurement, Check, CheckResult, GradedCheckResult, DifficultyClass, OpposedCheck, RoutineCheck, TeamCheck, Condition, ImposedCondition, ImposedConditions
- **Dependencies (one-way):** none — takes a character token, an integer effect rank, and named conditions; does not import those modules
- **Primary use case:** `trait.perform_check(dc)` then `check.resolve_graded()`, and `imposed_conditions.apply(condition, source)`
- **Rationale:** One d20 engine. Neighbors ask *Trait*, they do not roll.
- **Public API:** `Trait.perform_check`, `Trait.real_world_value`, `Trait.add_rank`, `Measurement.lookup`, `Check.resolve`, `Check.resolve_graded`, `OpposedCheck.resolve`, `RoutineCheck.resolve`, `TeamCheck.resolve`, `ImposedConditions.apply`, `ImposedConditions.supersede`, `ImposedConditions.remove_when_source_ends`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` checks; stories Resolve Checks)

## Constraint

Only *Check* owns d20 plus modifier versus DC. Other modules ask `Trait.perform_check`. Do not import character-construction, power, or combat.
