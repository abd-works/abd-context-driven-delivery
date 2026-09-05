# Generate — abd-architecture-code

Concepts and orchestration overview: **`reference/concepts.md`**.

## Step 0 — Required inputs — resolve or ask

Gather **all** of these before reading the spec or writing a line of code. The two architecture inputs (central spec + template package) come from two different upstream skills (`abd-architecture-specification` + `abd-architecture-template`); both must exist before this step proceeds.

| Input | Required | Resolution order | If missing |
| --- | --- | --- | --- |
| **Central architecture spec** | Yes | `docs/architecture/specification/architecture-specification.md` | **AskQuestion** — does the spec exist? If no, route back to `abd-architecture-specification`. |
| **Mechanism in scope** | Yes | The mechanism the story implements — read from the central spec's `## Where to Start` table by matching the story's requirement to a row. | **AskQuestion** — which mechanism row in Where to Start matches this story? |
| **`<context-file>`** | Yes | Follow the Where-to-Start link from the mechanism row to the per-folder `architecture-context.md`. | Stop and route back to `abd-architecture-specification` if the link is missing or the context file has `<!-- spec to fill -->` markers in File Structure, Class Specification, Rules, or Canonical Patterns. |
| **`<spec-root>` (template package)** | Yes | The template package for the mechanism in scope, located at `docs/architecture/templates/<slug>/`. In `project` mode (default) `<slug>` is the project slug. In `mechanism` mode `<slug>` is the kebab-cased mechanism name; the central spec's Where-to-Start row or References section names the link. | Stop and route back to `abd-architecture-template` if the package does not exist or `<spec-root>/example/` does not build. |
| **Domain context** | Yes | `domain-specification.md` (preferred) → `domain-model.md` | **AskQuestion** — which domain artifact? |
| **Story scope** | Yes | Story specification (preferred) → acceptance criteria on the story | **AskQuestion** — which story / spec / AC file? |
| **UX context** | When UI | `ux-specification.md` + mockup for the increment/flow | **AskQuestion** — which UX artifact? |
| **Story hierarchy** | Yes | `story-graph.json` or story map for epic / sub-epic names | **AskQuestion** — which increment / epic? |

**Story scope priority**

1. **Story specification** — Given/When/Then scenarios with real domain values (e.g. `*-specification-by-example.md`, `abd-story-specification` output).
2. **Acceptance criteria** — WHEN/THEN/AND/BUT on the story (`abd-story-acceptance-criteria` output).
3. Neither found → **AskQuestion** before proceeding.

**Domain context priority**

1. **`domain-specification.md`** — typed surface: operations, stereotypes, invariants.
2. **`domain-model.md`** — conceptual domain model: responsibilities and collaborators.
3. Neither found → **AskQuestion** before proceeding.

## Step 1 — Read context — `<context-file>` is the design; `<spec-root>` is the embodiment

**MANDATORY — read both before any generation:**

### From `<spec-root>` (the template package)

| Artifact | Path inside `<spec-root>` | Governs |
| --- | --- | --- |
| Parameterized reference module | `template/` | Canonical runnable code shape — copy and rename, never invent |
| Test scaffolds | `templates/tests/` | Parameterized test files per tier; instantiate one per sub-epic |
| Runnable example | `example/` | Sentinel-bound proof the template package builds + tests pass — read for reference, never modify |
| Mechanism rules | `rules/*.md` | DO / DO NOT for every generated file; FAIL halts the run |
| Substitution map | `parameters.json` | Placeholders + binding hints + rename map; drives all substitution |
| Package README | `README.md` | Runbook commands for `example/`; placeholder summary |

### From `<context-file>` (the per-folder spec the template embodies)

| Artifact | Path | Governs |
| --- | --- | --- |
| Mechanism context file | `<context-file>` (resolved from central spec Where-to-Start) | File Structure, Participants, Class Specification, Rules, Canonical Patterns — the *design* the template package mirrors. Read to verify the template is still current. |
| Central spec | `docs/architecture/specification/architecture-specification.md` | Where-to-Start (already used in Step 0) + cross-file navigation when the story touches multiple mechanisms. |
| Test-helpers context file | `tests/<helpers>/architecture-context.md` | Tier names, helper layout, folder structure — corroborates the template's `templates/tests/` shape; used when picking layer order. |

The template package is the embodiment of the per-folder context file. They MUST agree. If they disagree (template missing a new participant the spec added, vocabulary drift between Canonical Patterns and `template/`), **stop and route back to `abd-architecture-template` for a refresh**. Do not silently bridge the gap.

Layer order and tier mapping come from `<context-file>` + the test-helpers context file. Do not invent folders, file names, test tiers, or layer order not derivable from these inputs.

### Also read (outside `<spec-root>` and `<context-file>`)

- **Domain artifact** resolved in step 0 — class names, operations, field names, invariants.
- **Story artifact** resolved in step 0 — scenarios, acceptance criteria, actors.
- **UX artifact** when the story has screens — controls, test ids, navigation, states (client + E2E tests assert against these).
- **Existing project tests** — use only as a secondary reference **after** confirming they match `<spec-root>/rules/` and `<context-file>` § Rules; repo drift is not authority.

## Step 1b — Test layout inventory — mandatory gate before RED

**Do not write any scenario test or production code until this gate passes.**

All steps read from the joint authority of **`<context-file>`**, the test-helpers package-tier context file, and **`<spec-root>`** — never from agent memory of another project or stack.

1. Read tier names, layer order, and story-artifact → test-artifact mapping from the test-helpers package-tier context file (typically `tests/<helpers>/architecture-context.md`) corroborated by `<context-file>` Testing references.
2. Read test-related rules under `<spec-root>/rules/` and `<context-file>` § Rules — extract mandatory tier count and naming patterns.
3. List every **lowest-level sub-epic** in scope from `story-graph.json` / story map.
4. For each sub-epic, **derive** the full tier file set and helper set by substituting epic/sub-epic slugs into `<spec-root>/templates/tests/` paths per `<spec-root>/parameters.json`; cross-check filename pattern against the helpers context file's folder structure (mirror `<spec-root>/example/` when a tier scaffold is missing and route the gap back to `abd-architecture-template`).
5. Create empty scaffolds on disk from those templates **before** the first RED scenario.
6. Publish the inventory in chat — one row per sub-epic, columns = each tier and helper path **as defined by the helpers context file** (not a fixed column set from this skill).
7. If the project already has tests, compare structure to the inventory; reconcile drift before adding scenarios.

**Named spec overrides downstream defaults:** when **`abd-story-acceptance-test`** says "follow host project conventions", the helpers context file's testing-architecture decisions and `<spec-root>/templates/tests/` win.

See **`rules/scaffold-test-layout-before-scenarios.md`**.

## Step 1c — Layer progress checklist — mandatory (`track_task`)

**Do not start step 3 until this gate passes.** Persist session progress with **`track_task`** — not in chat alone.

1. **Resolve workspace** — **`skill-config.json` → `workspace.active_skill_workspace`**, or **`python skill-helpers/scripts/get_workspace.py`** from the agilebydesign-skills repo root; if unset, ask the user to set workspace first.
2. **Create progress tree** — **`<active_skill_workspace>/abd-architecture-code/progress/`** (do not overwrite existing checklists unless the user asks to reset).
3. **Derive layers** from the same sources as step **1b**: tier names and layer order from the helpers context file + `<context-file>` Testing references; production layer mapping from `<context-file>` § File Structure (mirrored in `<spec-root>/template/`). Default only when all sources are silent: domain → server → client → E2E.
4. **Write `process-checklist.md`** — one `- [ ]` line per workflow phase:

   ```markdown
   - [ ] 0 — Resolve inputs (`<context-file>`, `<spec-root>`, helpers context file, domain, story, UX, hierarchy)
   - [ ] 1 — Read context; derive test + production layer inventory
   - [ ] 1b — Scaffold test layout on disk
   - [ ] 1c — Layer progress checklist created
   - [ ] 3 — Generate tests and production (all spec layers)
   - [ ] 4 — Deploy and verify end-to-end
   - [ ] 4a — All spec-mandated test suites executed (full run, all pass)
   - [ ] 5 — Validate rules and scanners
   ```

5. **Write `<scope-slug>-layers-checklist.md`** — **`<scope-slug>`** = increment, epic, or story scope label from step **0**. For **each lowest-level sub-epic** in scope, list **every testing tier and production layer** from the spec **in order**. **Three checkboxes per layer** (tests require both scenario runs and a full tier execution):

   ```markdown
   ## <sub-epic-slug>

   ### <LayerName> (tests — <tier> per helpers context file)
   - [ ] Scenarios — each RED then GREEN (executed, not merely written) — `<test-tier-path-from-1b-inventory>`
   - [ ] Tier suite — full test run executed, all pass — `<same-path>` via `<spec test command>`

   ### <LayerName> (production — `<context-file>` File Structure layer)
   - [ ] Minimum code green for those scenarios — `<production-path-pattern-from-spec>`
   ```

   After all sub-epics, add **## Test execution — all tiers in scope** — one `- [ ]` line per **distinct test runner or tier** **`<spec-root>/rules/`** mandates (domain, server, client, E2E, etc.), with the command and scope path. Tick only after a **full run** passes — not a single scenario file in isolation when the spec requires the whole tier or suite.

6. **Tick step 0 and 1b items** — flip matching lines in **`process-checklist.md`** to `- [x]` for work already completed before this step.
7. **Publish summary in chat** — table: sub-epic × layer × scenario-run × tier-executed × production checkbox (paths and commands from inventory).

**During step 3** — after the **per-layer gate** passes (every scenario **executed** RED then GREEN, **full tier suite executed** for that layer, **and** production green), flip **all three** lines for that sub-epic × layer to `- [x]` before opening the next layer. **During step 4** — run and tick **Test execution — all tiers in scope** and **`- [ ] 4a`** only when every listed suite has been **executed** with all tests passing. **During step 4–5** — tick remaining **`process-checklist.md`** lines when each phase completes.

**Resume** — read **`progress/`** first; first unchecked `- [ ]` in the layers file is next unless the user names a step.

See **`rules/track-layer-completion-checklist.md`**.

## Step 2 — Downstream skills — mandatory, not optional

| Phase | Skill | When |
| --- | --- | --- |
| **RED — tests** | **`abd-story-acceptance-test`** | Always, for every layer's tests |
| **GREEN — production** | **`abd-clean-code`** | Always, for every production file |

**`abd-story-acceptance-test`**

- **MUST** read and follow that skill's `SKILL.md`, `rules/`, `reference/`, and matching language template.
- **Input:** story specification scenarios when available; acceptance criteria when not.
- **Plus (overrides generic output paths):** tier names, helper layout, test doubles, story-hierarchy → file mapping from the test-helpers package-tier context file + `<context-file>` Testing references; parameterized filenames and helper signatures from `<spec-root>/templates/tests/` (read from those sources, not assumed).
- **File unit** = whatever the helpers context file maps to the lowest story artifact (often sub-epic → file; some stacks differ — read the helpers context file's spec-alignment table).
- **Helpers** = whatever count and naming the helpers context file defines per file unit; signatures live in `<spec-root>/templates/tests/_helpers/` — shared across stories in that unit, not one helper file per story.
- Complete step **1b** (test layout inventory) before declaring file / class / method hierarchy.

**`abd-clean-code`**

- **MUST** read and follow that skill's `SKILL.md` and `rules/` when writing production code.
- **Input:** failing tests from step 3; domain artifact for names and behaviour.
- **Plus:** `<spec-root>/template/` patterns (constructor injection, layer placement, mechanism boundaries) corroborated by `<context-file>` § Class Specification and § Canonical Patterns.

If either skill package is not available in the workspace, **AskQuestion** — do not improvise test or production structure.

## Step 3 — Generate — layer order, one scenario at a time

Work **one layer at a time**, and within each layer work **one scenario at a time**. The unit of progress is a single scenario (one `it` / `test` method) — not a whole story file, not a whole layer.

**Default layer order** — read from the test-helpers package-tier context file + `<context-file>` Testing references first; use this table only when both are silent:

| Order | Production layer | Test layer (typical) |
| --- | --- | --- |
| **1** | Domain / shared | Domain unit tests |
| **2** | Server / API / persistence adapter | Server / HTTP adapter tests |
| **3** | Client / presentation | Client / UI adapter tests |
| **4** | — (full stack) | E2E / browser tests |

Tier file names, extensions, and helper suffixes come from **`<spec-root>/templates/tests/`** and **`<spec-root>/example/`** — not from examples in this skill prose.

**Per-scenario loop (mandatory — repeat for every scenario in story order)**

```
  ┌─────────────────────────────────────────────────────────────┐
  │  1. WRITE TEST   one scenario in the current tier's file    │
  │                  extend sub-epic helpers if needed           │
  │  2. RUN          confirm RED — fails for the right reason   │
  │  3. WRITE CODE   minimum production code to satisfy it      │
  │  4. RUN          confirm GREEN — this scenario passes        │
  │  5. FIX          if fail → fix code or test; re-run until OK  │
  │  6. NEXT TEST    only then add the next scenario              │
  └─────────────────────────────────────────────────────────────┘
```

1. **Write test** — run **`abd-story-acceptance-test`** for **one scenario** in the current tier's existing sub-epic file; add one `it` / `test` method; extend that sub-epic's tier helper — do not create new test files named after stories.
2. **Run (RED)** — execute the suite; confirm this scenario **fails for the right reason** (missing behaviour, not a typo or wiring mistake).
3. **Write code** — run **`abd-clean-code`**; add the **minimum** production code that scenario requires — no ahead-of-scope methods.
4. **Run (GREEN)** — execute again; this scenario **must pass** before any new test is written.
5. **Fix** — if it still fails, fix production code or test setup; re-run until green. Do not skip to the next scenario while this one is red.
6. **Next test** — pick the next scenario in story order; return to step 1.

When every scenario in the current layer is green, move to the next layer and restart the per-scenario loop there.

**Per-layer gate (mandatory)**

- Do not start the next layer until **every scenario in the current tier has been executed** RED then GREEN, the **full tier test suite has been executed** and passes, **and** production for that layer is green.
- After the gate passes, **check off** that layer's scenario-run, tier-executed, and production lines in **`<scope-slug>-layers-checklist.md`** (step **1c**) before opening the next spec layer.
- Do not write multiple scenario tests upfront and implement code in bulk — that violates the increment rule.

**DO NOT**

- Start RED without completing steps **1b** (inventory + scaffolds) and **1c** (**`track_task`** layer checklist on disk).
- Name test files after **stories** or **scenarios** when **`<spec-root>`** maps a higher story artifact (e.g. sub-epic) → file.
- Ship a story-hierarchy unit with only some tiers when **`<spec-root>/rules/`** mandates all tiers for that unit.
- Batch-write all test methods for a story, then all production code.
- Write production code before the scenario's test method exists.
- Move to the next scenario while the current one is still failing.
- Skip a layer or reorder layers contrary to the spec's Testing Architecture.
- Mark a layer done in chat without updating **`progress/`** checklists.
- Start the next spec layer while any scenario-run, tier-executed, or production checkbox for the current layer is still `- [ ]`.
- Mark tests done without **executing** them — writing test methods or seeing one scenario pass is not enough; run the full tier and every spec-mandated suite.
- Implement production files not required by the current scenario — but **test tier files** for each sub-epic must exist upfront even if scenarios are filled incrementally.
- Use live/production seam types in unit or adapter tests when the spec designates fakes or mocks.

## Step 4 — Deploy and verify — working solution required

The per-scenario loop continues through integration. After each layer's scenarios are green, and again when all layers are done:

1. **Install** dependencies (`npm install`, `pip install`, or equivalent per spec) — fix resolution errors immediately.
2. **Execute** every test tier **`<spec-root>/rules/`** and scripts require (unit, adapter, E2E, etc.) — **run the full suite**, not a single file in isolation when the spec mandates the whole tier; fix regressions before proceeding. Passing one runner when the spec mandates another is **not** done. Tick **Test execution — all tiers in scope** and **`- [ ] 4a`** in **`progress/`** only after every listed command has been run and all tests pass.
3. **Start** composition roots (dev server, app host) per spec — verify boot without errors.
4. **Smoke the flow** — walk the story's happy path in the running app (or E2E suite) to confirm the deployed solution actually works, not just that unit tests pass in isolation.
5. **Fix** any integration, wiring, or runtime failures; re-run affected scenarios; repeat until the story works end-to-end.

Do not proceed to validation until install succeeds, all tiers are green, the app runs, and the story flow works in the deployed environment.

When step **4** completes, tick **`- [ ] 4 — Deploy and verify end-to-end`** and **`- [ ] 4a — All spec-mandated test suites executed (full run, all pass)`** in **`process-checklist.md`**. Every line under **Test execution — all tiers in scope** must be `- [x]`.

## Step 5 — Validate — per-rule verdict required

Re-read every file in the spec's `rules/` and this skill's `rules/`. Run spec scanners when present:

```bash
python skills/common/scripts/run_scanners.py \
  --skill-root <spec-root> \
  --workspace <path-to-generated-code>
```

For each rule emit:

```
Rule: <rule-filename>  ->  PASS
Rule: <rule-filename>  ->  FAIL  <offending line or reason>
```

Fix every FAIL before declaring done.

When step **5** completes, tick **`- [ ] 5 — Validate rules and scanners`** and **`- [ ] 3 — Generate tests and production (all spec layers)`** in **`process-checklist.md`**. Every line in **`<scope-slug>-layers-checklist.md`** must be `- [x]`.

Then run [`common/reference/rule-checklist.md`](../../../../../common/reference/rule-checklist.md) and practice [`validate-checklist.md`](../../../reference/validate-checklist.md).
