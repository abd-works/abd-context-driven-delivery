# building-blocks-fidelity-requires-tactical-stereotype

- **tool:** Ddd (logged through Cdd on a sketch)
- **error:** Plan, Feature, PlanRepository, PlanFilter, SelectedPlan written as bare names — no <<Aggregate Root>> / <<Entity>> / <<Value Object>> / <<Repository>>.
- **rule:** building-blocks-fidelity-requires-tactical-stereotype
- **what changed:**
  - **Prose — yes.** Rule bullet on ddd.md building_blocks, and the same one-liners copied onto templates/ddd-sketch.md so generate sees them.
  - **Detector — yes.** ddd/scanners/building_blocks_fidelity_requires_tactical_stereotype_scanner.py.
  - **Generator — template already showed tagged names** ({{Root}} <<Aggregate Root>> <<Entity>>). The new bullets make “bare name = defect” explicit.
