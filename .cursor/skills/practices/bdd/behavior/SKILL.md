**Default format:** markdown

**Goal:** Name the BDD subject tree before behavior signatures — delegates module structure to Clean Engineering at the same depth.

### Guidance

Name the BDD subject tree before behavior signatures. Delegate module structure to Clean Engineering at the same depth. Rough subject index for a partition pass: domain things, states, or observable conditions (top-level `describe`s); subject + candidate `that`/`with` + TODOs. Not full `it should` suites.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ## behavior / ## development below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

Rough subject index for a **partition** pass or first cut — domain things, states, or observable conditions (top-level `describe`s); subject + candidate `that`/`with` + TODOs. Not full `it should` suites.

Key rules: `state-not-when` — nest by the state or condition that enables an observation, never by a `when` trigger; `nest-by-enabling-events` — sub-groupings are conditions that unlock further behavior, not implementation steps; `context-setup-expresses-state` — setup under a label must establish that label's state, not unrelated host boot.

### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

### Rules

- **no-implementation** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **framework-syntax** — Refer to [`practices/language-tools.md`](/practices/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.
