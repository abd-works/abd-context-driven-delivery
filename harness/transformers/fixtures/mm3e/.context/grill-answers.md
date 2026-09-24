# Grill answers — MM3E training sketch

Grill skipped on request (training reverse-engineer, no questions).

- **Lenses:** stories story-map then scenarios, clean-engineering modules (plus Check Resolution classes from the object model), bdd-behavior
- **Fidelity:** specification / modules / behavior
- **Scenarios:** reverse-engineered from each module `acceptance-criteria.md`; GWT names domain operations on the sketch (`Trait.performCheck`, `Check.resolve`, `ImposedConditions.apply`, `Hero.spendOn`, …)
- **Source of truth:** `harness/transformers/fixtures/mm3e` story map, module partitions, domain sketches, `check-resolution-object-model.md`
- **Story grouping:** parameterized confirming stories follow the consolidation notes in `story-map.md` (mechanical uniqueness, not one story per catalog row)
- **Deps:** `checks` is standalone; all other modules depend on it. Character Construction owns PP/PL. Combat owns hero point and extra effort.
