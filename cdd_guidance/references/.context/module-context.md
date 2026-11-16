# cdd_guidance/references
*References* are reference documents the installer copies into each IDE's `references/` folder for agents to read on demand, such as `language-tools.md`. They hold no code.

- **Purpose:** Keep reference material an agent may need in one place, installed beside the rules rather than loaded into every prompt.
- **Seam (terms):** each document by its file name
- **Dependencies (one-way):** none; installed by `harness/installation`.

## Constraint

A reference explains; it does not set a rule. A rule an agent must always follow belongs in `cdd_guidance/rules`.
