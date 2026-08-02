# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution. Deepen fidelity; never invent detail from a deeper level.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples (from CE `{Type}ExampleFactory` when available — never invent rows in story files).

| Fidelity | Default Format | Produce |
|---|---|---|
| **scaffold** | markdown | Thin epic index (artifact names + candidate story stubs) |
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | python | Main-flow scenarios per story (single or multiple); optional variations; fake + public seam |
| **acceptance_tests** | python | `*_spec` + `*_spec.{tier}` — CE runs alongside to produce matching production code |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`verb-noun-format`** — Name Epic / SubEpic / Story verb–noun; actor is metadata; base verb form.
- **`four-to-nine-children`** — 4–9 direct children (warn at 3/10; error ≤2 or ≥11).
- **`behavioral-observable-outcomes`** — Name and Then in domain-observable terms; never internals.
- **`branch-on-mechanical-uniqueness`** — Explore context relentlessly for distinct mechanics. Branch on mechanical uniqueness, dstinct mechanics in requirements require *distinct stories* for each mechanic. Different requirement entries with same mechanic is *one story only with different examples or scenarios*. Collapsing real mechanical variation, as well as mindlessly turning requirements into long lists of stories are **defect**
- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk.
- **`right-size-story-nodes`** — One demonstrable interaction per story.
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!

---


## scaffold

**Produce:** thin epic index — verb–noun epics + mid-level grounding story stubs (`StoryMap` → `Epic` → `SubEpic` → `Story` → `Scenario`).

Key rules: \ranch-on-mechanical-uniqueness\ — split on distinct mechanics, not catalog/requirements rows; ead-all-source-context-in-full\ — read segments in full before grouping.

## discovery

**Format:** markdown · **Produce:** named stories under activities + thin-slice order.

**Do:**
1. Build the map: verb–noun stories under each activity; assign actors.
2. Slice vertically — increments named for stakeholder-visible capability; copy story names **verbatim** from the map.
3. Mark spine vs optional; never slice horizontally (“finish epic A then B”).
4. Fill `templates/md/story-map.md` and `templates/md/thin-slice.md` (optional `.context/story-context.md` per activity folder).
5. Keep unmapped work in the **sketch** as `* approx N–M …`; drop approx as stories get named.

**Rules:** `story-map-shape` / `story-map-discipline` · `thin-slice-shape` / `thin-slice-increment-shape` / `thin-slice-ordering` · `story-name-exact-match` · apply `branch-on-mechanical-uniqueness` and `read-all-source-context-in-full` while grilling and sketching.

---

## exploration

**Format:** python · **Produce:** one runnable main-flow scenario per story — fake + public seam. No tier specs yet.

**Stories vs BDD:** Stories = acceptance (e2e / tier). BDD = object-level tests.

**Layout:** Epic / nested SubEpic / Story = folders; optional `.context/story-context.md` per folder.

```
{epic}/
  {epic}-helper.{ext}       # → {Type}ExampleFactory
  {story}/
    {story}_story.{ext}     # GWT; mode "fake" when entry
```

| File | Role |
|---|---|
| `*_story.{ext}` | Runnable GWT; **fake** `I{Type}` via helpers → factory; assert **public interface** only |

**Do:**
1. Export `create{Story}Story(mode)` registering `story` / `scenario` / `given` / `when` / `then`.
2. Run the story entry with `mode: "fake"`.
3. Route steps: helper → `{Type}ExampleFactory.load…({ mode })`.
4. Assert **Then** only on the public seam of `I{Type}` — no private fields, no hand-rolled Fakes.
5. Pull values from `examples[{example_key}]` — no story-local example tables.
6. Fill `templates/py|js/…/{story}_story.*` (md walk-through: `templates/md/scenario-main-flow.md` if documenting only).
7. **Optional — variation scenarios (off by default).** In the same `*_story.{ext}`, add alternate / error / boundary scenarios and shared backgrounds only when **one of these is true**:
   - The main-flow scenario already exists in the story file, **or**
   - Explicitly asked for.
   Apply the scenario rules below to any variation added here. Do not add variations before the main flow is confirmed.

**Rules (main-flow and any optional variations):**
- **`scenarios-shape`** / **`scenario-step-quality`** — Given / When / Then; domain-observable steps.
- **`factory-backed-examples`** — Values in `{Type}ExampleFactory`; steps may name the method or returned object.
- **`assert-public-interface`** — Then reads only the public seam of `I{Type}` (+ peers).
- **`scenario-coverage`** — Cover important variations, not only happy path (when optional step 7 is active).
- **`real-data-over-invented-values`** — Factory examples trace to domain / evidence.
- **`atomic-deltas-over-repetition`** — State the delta; do not copy-paste walls.
- **`alternate-actor-emphasis`** — Call out alternate actors when the path changes.
- **`factory-objects-in-scenarios`** — Obtain objects via helpers → `{Type}ExampleFactory.{method}` (fake mode).
- **`variations-after-main-flow`** — Never add alternate / boundary scenarios before the main-flow scenario exists and is confirmed.

---

## engineering

**Format:** python · **Produce:** write-once tier specs that re-run the same scenarios. Prefer RED until behaviour exists; drive green with minimum production code.

| File | Role |
|---|---|
| `{story}_story.*` | Tier-neutral GWT; entry runs **fake** (owned at explore/spec) |
| `{story}_spec.*` | Isolated — real `{Type}` + injected mocks; `create{Story}Story("isolated")` |
| `{story}_spec.{tier}.*` | Same scenarios; named tier (e.g. `…_spec.production.js`) |

**Do:**
1. Confirm language/framework (default pytest / `node --test`).
2. Scaffold `*_spec` (isolated) and/or `*_spec.{tier}` if missing — never overwrite existing bodies; each calls the shared story fn with matching mode.
3. Keep fake in the story file only; isolated = `{Type}` + injected mocks; other tiers via `*_spec.{tier}`.
4. RED → GREEN → REFACTOR one scenario at a time.
5. After **2 consecutive fix failures** — stop; call `diagnostic().diagnose()` before a third fix.
6. Run **validate**.

**Rules:** `tests-shape` · `tests-implement-specification` · `tier-bodies-implemented` · `assertions-against-real-behavior` · `scenarios-tied-to-runtime` · `bug-fix-test-first` · `tier-factory-kind` (call story with `isolated` or named tier — never invent Fake subclasses in tier bodies).

---

## Example factories (Clean Engineering)

Link to CE factories; do not invent Fakes or story-local example tables.

| Artifact | Emit |
|---|---|
| Epic helper | Import `{Type}ExampleFactory`; `given*` → `load*({ mode })` |
| Story (explore/spec) | GWT; `mode: "fake"`; assert public `I{Type}` |
| Tier spec | Same story fn; `mode: "isolated"` \| `"production"` |

**Chain:** steps → helper → `load…({ mode })` → `I{Type}` (+ peers) → assert public seam.

**Modes:** `fake` = mock/stub + `examples[{key}]` · `isolated` = `new {Type}(...mocks)` · `production` = `new {Type}(...real)`.

Declare on the model: `Epic.example_factories` / `SubEpic.example_factories`. Normalize via `code/example_factories.py`.

**Rules:** `helpers-import-factories` · `examples-multi-type-bundle` · `stories-do-not-own-ce-types` · `no-story-local-example-tables`.

---

# Generate

1. Confirm fidelity and format (defaults above).
2. Read this file — shared rules + active fidelity.
3. **MUST** follow base `generate` step 2: before any grill/iterate question, prove-read every relevant referenced context for that decision (segments, module-context, grill-answers, story-context, build-order, cited paths, …). Index mid-epic stubs are not inventory. Apply `read-all-source-context-in-full`.
4. Use peer actions when useful (`grill`, `sketch`, `iterate`; `templates/stories-sketch.md`).
5. Fill templates for the active fidelity.
6. Run **validate**.
