# Concepts — abd-architecture-code

> **Practice-level model:** [`../../../reference/architecture-context-model.md`](../../../reference/architecture-context-model.md) — the centralized documents, per-folder context files, and template packages this skill reads from.

## Two inputs to every code-generation run

Code generation consumes **two distinct artefacts** in the architecture family:

1. **The project's architecture specification** — central `docs/architecture/specification/architecture-specification.md` plus the per-folder `architecture-context.md` reachable via Where-to-Start. Source of truth for *what design every generated file must conform to*.
2. **The template package** — a runnable parameterized reference module at `docs/architecture/templates/<slug>/` produced by `abd-architecture-template`. Source of truth for *what the generated files look like before placeholder substitution*.

Both must exist before this skill writes code. If the spec is missing, route back to `abd-architecture-specification`. If the template package is missing, route back to `abd-architecture-template`.

## `<spec-root>` — resolves to a template package

The variable `<spec-root>` referenced throughout this skill's generate.md and rules is the **path to the resolved template package** — *not* the central spec file and *not* a project-wide spec directory. It is one of:

| Mode of the source template skill | `<spec-root>` resolves to |
|---|---|
| `project` *(default)* | `docs/architecture/templates/<project-slug>/` — the project's single template package. |
| `mechanism` *(opt-in)* | `docs/architecture/templates/<mechanism-slug>/` — the package for the mechanism the current story touches; resolved via the central spec's Where-to-Start lookup. |

Inside `<spec-root>` the layout is the same in both modes — `template/`, `templates/tests/`, `example/`, `rules/`, `parameters.json`, `README.md`. This skill reads:

| `<spec-root>` artefact | What this skill does with it |
|---|---|
| `<spec-root>/template/` | Copies and renames per feature (placeholder substitution via `parameters.json`). |
| `<spec-root>/templates/tests/` | Instantiates the test scaffolds for every tier the spec mandates. |
| `<spec-root>/example/` | Reads as the *runnable proof* the template package is valid; never modifies. |
| `<spec-root>/rules/` | Validates every generated file against these rules; a FAIL stops the run. |
| `<spec-root>/parameters.json` | The substitution table; defines what to rename. |

`<spec-root>` overrides generic paths in downstream skills (e.g. when `abd-story-acceptance-test` says "follow host project conventions").

## `<context-file>` — the design source

The variable `<context-file>` is the per-folder `architecture-context.md` for the mechanism the current story is implementing. Reached via:

1. Read the central spec's `## Where to Start` table.
2. Find the row matching the story's requirement.
3. Follow the link to the mechanism-tier `architecture-context.md`.

`<context-file>` carries File Structure, Participants, Class Specification, Rules, and Canonical Patterns. These describe the design that `<spec-root>` embodies as runnable code. The two must be consistent (enforced by `abd-architecture-template`'s `template-stays-in-sync-with-spec` rule); if they drift, route back to the template skill for a refresh.

This skill reads `<context-file>` to:

- Verify the template package matches the current design (catch drift between spec and template).
- Resolve cross-references (a participant in `<spec-root>/template/` whose role description lives in `<context-file>` § Participants).
- Read any rules that have been added to the spec but not yet lifted into `<spec-root>/rules/`.

## Orchestration

| Phase | Skill | Output |
| --- | --- | --- |
| Setup | **`track_task`** | **`progress/`** checklists — one row per spec testing tier and production layer |
| RED | **`abd-story-acceptance-test`** | Acceptance tests per **`<spec-root>/templates/tests/`** scaffolds (validated against **`<context-file>`** Testing references and the test-helpers package-tier context file) |
| GREEN | **`abd-clean-code`** | Production code copying and renaming **`<spec-root>/template/`** files, enforcing **`<spec-root>/rules/`** |

## Per-scenario increment

Work **one scenario at a time** within each layer: write test → run RED → write code → run GREEN → fix → next scenario. Do not batch all tests then all code.

**Layer order** — read from **`<context-file>`** Testing references first, falling back to the test-helpers package-tier context file when the per-mechanism context file does not pin order. When both are silent, default: domain → server → client → E2E (or spec-equivalent tier names).

Continue through deploy and verify until the story works end-to-end in a running solution — not when unit tests alone pass.

The `abd-architecture-template` skill shows the *parameterized template shape* as a runnable reference module (`<spec-root>/template/` plus a built-and-tested `<spec-root>/example/`); this skill shows *filled-in output* — the per-feature substitution of the template against a real story.
