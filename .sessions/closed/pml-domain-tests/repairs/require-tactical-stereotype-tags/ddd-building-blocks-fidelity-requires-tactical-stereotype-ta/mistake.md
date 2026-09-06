# ddd-building-blocks-fidelity-requires-tactical-stereotype-ta

- **entry_id:** 8b1192c8
- **artifact:** cdd-sketch.md # DDD > Plan BC
- **rule:** DDD building_blocks fidelity requires tactical stereotype tags (<<Aggregate Root>>, <<Entity>>, <<Value Object>>, <<Repository>>) on every class name — per context_tools/ddd/templates/ddd-sketch.md building_blocks section (e.g. "{{Root}} <<Aggregate Root>> <<Entity>>", "members: {{Part}} <<Value Object|Entity>>"). Do not write bare class names without their stereotype.
- **wrong:** Plan (bare, no stereotype); Feature (bare); PlanRepository (bare); PlanFilter (bare); SelectedPlan (bare) — none tagged with DDD tactical stereotypes
- **status:** fixed
