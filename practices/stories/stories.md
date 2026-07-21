# Concepts

Stories look at the product through human and system interactions — behaviours required to produce a solution — mapped hierarchically at increasing fidelity.

**Canonical model** (reuse, do not reinvent): `StoryMap` → `Epic` → `SubEpic` (nested sub-epics allowed) → `Story` → `Scenario`, plus `Increment` on the map. Scenarios carry `background`, `given`, `interactions`, `example_rows`. Stories may have an actor (`users`).

**Layout (code):** Epic = folder; nested SubEpic = folder; leaf SubEpic = file(s); Story = class; Scenario = test operation. Optional `.md` context per folder.

**Hybrid file kinds (code):**
1. **Regeneratable** — test flow + examples/data (safe to rewrite from the model).
2. **Tier files** — write-once, AI/human authored; call production code. Added at **engineering**.

**Stories vs BDD:** Stories = acceptance tests at e2e or tier/layer. BDD = object-level tests.

---

This skill operates at **multiple levels of fidelity**. Start from grill + sketch and deepen. Each level **adds** artifacts — do not invent detail from a deeper fidelity.

| Fidelity | Default format | Output |
|---|---|---|
| **discovery** | markdown | Story map + thin-slice increments |
| **exploration** | python | Regeneratable test flow — main-flow scenario per story |
| **specification** | python | Regeneratable flow deepened — variations, outlines, examples |
| **engineering** | python | Write-once **tier** files that call production (should fail unless reverse-engineering) |

**Templates (AI generate — same as Clean Engineering):** **markdown + python only** under `templates/md/` and `templates/py/`. Other languages are not templated for generate — use code channels / `transform` (seeds live under `code/{lang}/seeds/`).

**Cross-language scanners:** channels parse into the canonical model; scanners read model fields only — never language syntax.

---

## Shared rules

- **`verb-noun-format`** — Epic / SubEpic / Story names are verb–noun; actor is metadata, never in the name; base verb form.
- **`four-to-nine-children`** — Every parent has 4–9 direct children (warning at 3/10; error at ≤2 or ≥11).
- **`behavioral-observable-outcomes`** — Names and Then steps state what a stakeholder can observe in domain terms; never internals.
- **`vocabulary-traces-to-domain-source`** — Domain terms trace to domain language / model sources when those exist.
- **`emphasise-domain-significant-terms`** — Bold domain concepts in scenario steps; keep vocabulary aligned.
- **`artifacts-mirror-story-hierarchy`** — Folders/files mirror Epic → SubEpic → Story structure.
- **`right-size-story-nodes`** — A story is one demonstrable interaction, not a bundle.

---

## discovery

**Default format:** markdown

**Goal:** Named stories under activities, plus a thin-slice delivery order.

- Story map has verb–noun stories under each activity with an actor assigned.
- Thin slice: vertical increments named for stakeholder-visible capability; story names copied verbatim from the map.
- Spine vs optional marked; no horizontal “finish epic A then B” slicing.
- Fill `templates/md/story-map.md` and `templates/md/thin-slice.md`. Optional `templates/md/story-context.md` per folder.
- Unmapped remainder stays in the **sketch** as `* approx N–M …` — not a separate outline map. Drop approx lines as stories get named.

### Rules

- **`story-map-shape`** / **`story-map-discipline`** — Hierarchy is Epic → SubEpic → Story; named stories under each activity (approx gaps belong in sketch, not the discovery map).
- **`thin-slice-shape`** / **`thin-slice-increment-shape`** / **`thin-slice-ordering`** — Increments are vertical, ordered, story names exact-match the map.
- **`story-name-exact-match`** — Thin-slice story strings match map names character-for-character.

---

## exploration

**Default format:** python

**Goal:** Regeneratable test-flow artifacts — one main-flow scenario per story. Scenario ops describe the walk-through (flow + placeholders); not tier implementations yet.

- Leaf sub-epic files hold story classes; scenario methods are the main flow.
- Scenario Outline style: placeholders in steps; one representative examples row.
- No tier files yet.
- Fill regeneratable templates: `templates/md/scenario-main-flow.md` / `scenario-outline.md`, or `templates/py/…/{lowest_sub_epic}_stories.py`. Prefer outline; use `scenario-inline.md` only when explicitly requested. Other languages → `transform` from python/markdown.
- Examples table: **one representative row** (main flow only).

### Rules

Follow the scenario rules under **specification** (shape, step quality, no-inline-examples, outline structure). At exploration, apply them to the main-flow outline only — one example row, no variation scenarios yet.

---

## specification

**Default format:** python

**Goal:** Deepen regeneratable flow — variations (errors, boundaries), outlines, real example rows from domain sources.

- Add scenarios for important variations; keep regeneratable (no tier overwrite).
- Example values are real/domain-grounded, not invented placeholders.
- Backgrounds where shared setup applies across scenarios.
- Deepen the same md/py regeneratable story files (outlines + examples tables); do not invent a parallel shape.

### Rules

- **`scenarios-shape`** / **`scenario-step-quality`** — Given / When / Then present; steps are domain-observable.
- **`scenarios-no-inline-examples`** — Concrete values live in examples, not inline in steps (unless inline format explicitly requested).
- **`scenario-outline-structure`** — Outline + examples table is the default.
- **`scenario-coverage`** — Important variations covered; not only happy path.
- **`real-data-over-invented-values`** — Examples trace to domain / evidence.
- **`atomic-deltas-over-repetition`** — Variations state the delta, not copy-paste walls.
- **`alternate-actor-emphasis`** — Alternate actors called out when the path changes.

---

## engineering

**Default format:** python

**Goal:** Add write-once **tier** files that implement steps against production code. Tests should fail (RED) unless reverse-engineering existing behaviour. Drive to green with minimum production code.

1. Confirm language/framework (default pytest for python).
2. Scaffold tier file(s) from `templates/py/…/test_{lowest_sub_epic}_{layer}.py` if missing — never overwrite existing tier bodies. Other languages → channel scaffold / `transform`.
3. Wire literal step strings in test methods (`tier.given["…"]()` discipline, or equivalent helper calls).
4. RED → GREEN → REFACTOR one scenario at a time.
5. If a test fails after **2 consecutive fix attempts** — stop. Read `diagnose.md` immediately.
6. Run **validate**.

### Rules

- **`tests-shape`** — Story = test class; scenario = test method; hierarchy mirrored on disk.
- **`tests-implement-specification`** — Every regeneratable scenario has a tier test method.
- **`tier-bodies-implemented`** — No TODO / not-implemented placeholders left when claiming done.
- **`assertions-against-real-behavior`** — Assert observable outcomes through the tier boundary.
- **`scenarios-tied-to-runtime`** — Steps resolve to real runtime behaviour, not fiction.
- **`bug-fix-test-first`** — Bug fixes start with a failing acceptance test.

---

# Generate

1. Confirm fidelity (`discovery` → `engineering`) and format (defaults above). All formatters available via the same CLI.
2. Read § Concepts — shared rules and the active fidelity (including its Rules).
3. Grill and sketch when useful (`@grill_with_context`, `sketch-template.md`).
4. Fill `templates/md/…` or `templates/py/…` for the active fidelity (regeneratable through specification; py tier templates at engineering only).
5. Run **validate**.
