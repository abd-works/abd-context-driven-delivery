# BDD context tool — agent rules

Lessons from correcting `bdd.md` and the BDD tool itself. Record each in the same turn as the fix.

1. **Validate ≠ scan.** Judge every named rule in `bdd.md` (Shared Rules + development Rules). Scanner pass/fail is not a substitute.

2. **Do not add a scanner unless asked.** When adding a validate rule, update `bdd.md` only.

3. **New shared rules go in three places in `bdd.md`:** Shared Rules, modules scaffold key rules (if applicable), and development Rules.
