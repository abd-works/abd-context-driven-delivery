# abd-architecture-specification — eval/

This folder holds the fixture suite the skill is validated against, following
the convention described in
[`common/reference/agentic-repair-loop.md`](../../../../common/reference/agentic-repair-loop.md)
and [`common/reference/manual-repair-loop.md`](../../../../common/reference/manual-repair-loop.md).

## Layout

- **`pass/golden-spec/`** — full passing artefact set: the main
  `architecture-specification.md` plus one example of each context-file tier
  (mechanism, package, two miscellaneous flavours). Every rule in `rules/`
  must report **clean** against every file here.
- **`fail/<rule-slug>/`** — one minimal artefact per new rule that breaks
  ONLY that rule. Every other rule should still report clean. This lets a
  scanner suite assert each rule independently.
- **`cases.json`** — registry. Maps each fixture to the expected result
  (`clean` or `violate`) for every rule. The format follows the same shape
  used by other skills in the repo.

## How to run (when scanners are wired)

Scanners are not yet implemented for this skill — `cases.json` is currently a
declarative target. When `scripts/scanners/<rule-slug>.py` is added per rule,
the runner under `foundational/skill-helpers/skills/common/scripts/` can
execute the full suite via the standard cases-file contract.

## Updating fixtures

If the live `pml-midtier/docs/architecture/specification/architecture-specification.md`
materially changes in a way that improves the canonical shape (not a typo
fix, not a drafting note), refresh `pass/golden-spec/docs/architecture/...`
from the live file and re-run the full suite. If the live file regresses
relative to the rules, fix the live file rather than the fixture.
