# Rule: Scenarios belong in the story graph (canonical persistence)

When the team uses **`story-graph.json`** as the system of record, add scenarios to **`stories[].scenarios`** and scenario outlines to **`stories[].scenario_outlines`**. Do not spin up parallel “feature specification” documents or ad-hoc `docs/.../scenarios.md` collections that compete with the graph—**this skill’s** `specification-by-example.md` / `.txt` artifacts are **authoring** outputs that should align with or feed the same structure, not a second source of truth.

## DO

- Treat epics → features → stories → **scenarios** as the stable hierarchy in JSON when the bot or pipeline expects it.
- Keep scenario names stable enough to link to tests or automation IDs where your process requires it.

## DON'T

- Create standalone markdown specs whose scenarios are not reflected in **`story-graph.json`** when that file is authoritative for the workspace.
- Fork the same scenario under multiple unofficial paths (harder diffing, drift).

```text
OK: story-graph.json → epics[].…stories[].scenarios[]
Avoid: docs/story/Epic/Feature/Feature Specification.md as the only home for scenarios
``