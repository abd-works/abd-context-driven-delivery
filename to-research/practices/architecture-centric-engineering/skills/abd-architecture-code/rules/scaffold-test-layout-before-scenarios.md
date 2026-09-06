# Rule: Scaffold test layout before scenarios

Declare and create the full test file tree **before** writing scenario methods or production code. Authority order:

1. **`<context-file>`** — per-folder mechanism `architecture-context.md` (Testing references, layer order)
2. **Test-helpers package-tier context file** (typically `tests/<helpers>/architecture-context.md`) — tier names, helper layout, folder structure, spec-alignment table — this is the new source-of-truth for testing-architecture decisions in the project-distributed model.
3. **`<spec-root>/templates/tests/`** — parameterized test scaffolds the `abd-architecture-template` skill produced from the helpers context file. Authoritative for filename patterns and helper signatures.
4. **`<spec-root>/example/`** — sentinel-bound example tests proving the scaffold compiles and runs.
5. **`<spec-root>/rules/`** — mechanism-specific test rules lifted into the template package.

Not story titles. Not agent memory of another stack. Not repo drift unless it matches items 1–5.

If items 1–2 (the spec design) disagree with items 3–5 (the template embodiment), stop and route back to `abd-architecture-template` for a refresh. Do not pick one silently.

## DO

- Resolve **`<spec-root>`** (the template package at `docs/architecture/templates/<slug>/`) and **`<context-file>`** (the mechanism's per-folder `architecture-context.md`) first; every layout decision reads from those two artefacts plus the test-helpers package-tier context file.

- Derive the test inventory from the **lowest story artifact** the helpers context file maps to a file (often lowest-level sub-epic in `story-graph.json`) — not from individual story or scenario names.

  **Example (pass):** Helpers context file's folder structure maps **sub-epic → file**; three sub-epics in scope → three file units × each mandatory tier × helper set defined in `<spec-root>/templates/tests/`.

- Instantiate empty scaffolds from **`<spec-root>/templates/tests/`** **before** the first RED scenario; substitute `{epicSlug}`, `{subEpicSlug}`, and other placeholders per `<spec-root>/parameters.json`.

- When `<spec-root>/templates/tests/` lacks a tier the helpers context file mandates, mirror **`<spec-root>/example/`** test file names and folder depth as a reference, then route the gap back to `abd-architecture-template`.

- Use existing project tests only **after** verifying they match **`<spec-root>/rules/`** and **`<context-file>` § Rules**; reconcile drift before adding scenarios.

- Run project lint and the helpers context file's prescribed scanners after scaffolding and again before declaring done.

## DO NOT

- Hardcode MERN, hero-vtt, or any stack in generated paths when `<spec-root>` is something else.

- Name test files after **stories** or **scenarios** when the helpers context file maps a higher artifact → file.

  **Example (fail):** Files like `validate-*_server.test.ts` / `enqueue-*_server.test.ts` when the helpers context file maps **sub-epic → file** — fragments one unit across many files.

- Create only some tiers for a file unit when `<spec-root>/rules/` or `<context-file>` § Rules mandates all tiers for that unit.

- Follow **`abd-story-acceptance-test`** "host project conventions" when they contradict `<spec-root>` or `<context-file>`.

- Split helpers per story when the helpers context file defines one helper set per file unit.

- Treat `<spec-root>` as the design authority when it disagrees with `<context-file>`; the design lives in the per-folder spec, the embodiment lives in the template package. Disagreement is a template-skill drift bug — route back, do not silently pick one.
