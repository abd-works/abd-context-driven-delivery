# cdd_guidance/practices
*Practice* is a field of expertise used as a lens on the work — Stories, DDD, UX, Clean Engineering, BDD, and agent BDD — each a *PracticeGuidance* with its own `{practice}.md` (Overview, shared rules, and a section per fidelity with its rules), templates, examples, and formats. Each practice is its own module with its own card in its folder; this card covers what the practices share.

*Stage* is how far the work has gone — `discovery`, `specification`, or `implementation` — written on each fidelity as **Stage:**, so the fidelities of different practices line up: story map, bounded context, IA, modules, and behavior are all discovery. The stage names are the constants `DISCOVERY`, `SPECIFICATION`, and `IMPLEMENTATION` in `cdd_guidance.practices.stages`; the Session Board's *Stage* columns (space/kanban) are named from them.

- **Purpose:** Name the stages every practice's fidelities line up on, so the board and the actions can move work through the same three stages whatever practice it uses.
- **Seam (terms):** `cdd_guidance.practices.stages` — `DISCOVERY`, `SPECIFICATION`, `IMPLEMENTATION`
- **Dependencies (one-way):** none

## Constraint

A practice's fidelity names its stage with one of these three names; do not add stage names in a practice. Run lifecycle steps on a practice through the actions — `generate.generate(guidance=["stories-story-map"])` — rather than adding them as methods on the practice class.
