# Contexts

Stories look at the product through human and system interactions — behaviours required to produce a solution — mapped hierarchically at increasing fidelity.

**Canonical model** (reuse, do not reinvent): `StoryMap` → `Epic` → `SubEpic` (nested sub-epics allowed) → `Story` → `Scenario`, plus `Increment` on the map. Scenarios carry `background`, `given`, `interactions`. Stories may have an actor (`users`). Concrete example values live in Clean Engineering `{Type}ExampleFactory` — not as invented rows inside story files.

**Layout (code):** Epic = folder; nested SubEpic = folder; Story = folder; optional `.md` context per folder.

**Hybrid file kinds (code):**
1. **Story file** (`*_story.{ext}`) — explore / specification. Runnable Given / When / Then against **fake** `I{Type}` via helpers → `{Type}ExampleFactory`. Assert the **public interface** only.
2. **Isolated spec** (`*_spec.{ext}`) — engineering default; factory mode `isolated` (real `{Type}` + injected mocks).
3. **Tier spec** (`*_spec.{tier}.{ext}`) — engineering; other tiers (`production`, …). Same scenarios; calls the shared story function with that mode.

**Stories vs BDD:** Stories = acceptance tests at e2e or tier/layer. BDD = object-level tests.

---

This skill operates at **multiple levels of fidelity**. Start from grill + sketch and deepen. Each level **adds** artifacts — do not invent detail from a deeper fidelity.

| Fidelity | Default format | Output |
|---|---|---|
| **discovery** | markdown | Story map + thin-slice increments |
| **exploration** | python | Runnable story — one main-flow scenario per story (fake + public interface) |
| **specification** | python | Same story files deepened — variations; still fake + public interface |
| **engineering** | python | Isolated spec (`*_spec`) + tier specs (`*_spec.{tier}`) |

**Templates (AI generate):** `templates/md/` (full stories/scenarios/domain terms/examples tables), `templates/py/`, `templates/js/` (and ts/java via channels). Code emitters and templates share one shape: runnable `*_story` + `*_spec` / `*_spec.{tier}`. Markdown↔code: md keeps documentation tables; code emits structure/stubs for AI to fill.

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

**Goal:** One runnable main-flow scenario per story — wired to **fakes**, asserting the **public interface** of domain objects. Not tier implementations yet.

### Shape (code)

```
{epic}/
  {epic}-helper.{ext}          # → {Type}ExampleFactory
  {story}/
    {story}_story.{ext}        # GWT; mode "fake" when this file is the entry
```

- Export a story function `create{Story}Story(mode)` (or language equivalent) that registers `story` / `scenario` / `given` / `when` / `then`.
- Story file runs with **`mode: "fake"`** when it is the test entry (not when a tier imports it).
- Steps call epic helpers → `{Type}ExampleFactory.load…({ mode })`.
- **Then** asserts only through the public seam of `I{Type}` (getters / operations callers use) — not private fields, not invented Fake subclasses.
- Concrete values come from factory `examples[{example_key}]` — **do not** invent story-local example tables or copy ranks/names into the story file.
- No specs yet (`*_spec` / `*_spec.{tier}` appear at engineering).
- Fill: `templates/py/…/{story}_story.py` or `templates/js/…/{story}_story.js`; md walk-throughs under `templates/md/scenario-main-flow.md` when documenting only.

### Rules

Follow the scenario rules under **specification** (shape, step quality, factory-backed values). At exploration, apply them to the **main-flow scenario only** — no variation scenarios yet.

---

## specification

**Default format:** python

**Goal:** Deepen the same runnable story files — variations (errors, boundaries), shared setup — still **fake** + **public interface**.

- Add scenarios for important variations inside the same `*_story.{ext}`.
- Expected values still come from ExampleFactory methods (or peers in the same factory bundle) — not invented inline tables.
- Backgrounds / shared givens where the same setup applies across scenarios.
- Deepen helper factory links: epic helper imports factories; scenario steps name objects returned from helpers.
- Do **not** invent a parallel pure-data `*_stories` file. The story file *is* the specification at this fidelity.

### Rules

- **`scenarios-shape`** / **`scenario-step-quality`** — Given / When / Then present; steps are domain-observable.
- **`factory-backed-examples`** — Concrete values live in `{Type}ExampleFactory.examples` / `load*` methods. Story files do not invent parallel example tables. Steps may name the factory method or the domain object it returns.
- **`assert-public-interface`** — Then steps read only the public seam of `I{Type}` (and peers returned with the bundle). No reaching into private implementation.
- **`scenario-coverage`** — Important variations covered; not only happy path.
- **`real-data-over-invented-values`** — Factory examples trace to domain / evidence.
- **`atomic-deltas-over-repetition`** — Variations state the delta, not copy-paste walls.
- **`alternate-actor-emphasis`** — Alternate actors called out when the path changes.
- **`factory-objects-in-scenarios`** — When CE factories exist, scenario givens/outcomes obtain objects via helpers → `{Type}ExampleFactory.{example_method}` (**fake** mode at explore/spec).

---

## engineering

**Default format:** python

**Goal:** Add write-once **tier specs** that re-run the same scenarios against production types. Tests should fail (RED) unless reverse-engineering existing behaviour. Drive to green with minimum production code.

1. Confirm language/framework (default pytest for python; `node --test` for JS).
2. Scaffold `*_spec.{ext}` (isolated) and/or `*_spec.{tier}.{ext}` if missing — never overwrite existing bodies. Each calls the shared story function with the matching mode.
3. Factory mode: **isolated** (`{Type}` + ctor-injected mocks/stubs) via `*_spec`; other tiers via `*_spec.{tier}` (e.g. **production**). Fake stays in the story file only.
4. RED → GREEN → REFACTOR one scenario at a time.
5. If a test fails after **2 consecutive fix attempts** — stop. Read `diagnose.md` immediately.
6. Run **validate**.

### Rules

- **`tests-shape`** — Story folder holds `*_story` + `*_spec` (+ `*_spec.{tier}` as needed); hierarchy mirrored on disk.
- **`tests-implement-specification`** — Every story scenario is exercised by each declared spec.
- **`tier-bodies-implemented`** — No TODO / not-implemented placeholders left when claiming done.
- **`assertions-against-real-behavior`** — Assert observable outcomes through the public interface at that tier.
- **`scenarios-tied-to-runtime`** — Steps resolve to real runtime behaviour, not fiction.
- **`bug-fix-test-first`** — Bug fixes start with a failing acceptance test.
- **`tier-factory-kind`** — Specs call the story with **isolated** (`*_spec`) or a named tier (`*_spec.{tier}`) — never invent Fake subclasses in tier bodies.

### Naming

| File | Role |
|---|---|
| `{story}_story.py` / `.js` | Tier-neutral GWT; entry runs **fake** |
| `{story}_spec.py` / `.js` | Isolated objects — `create{Story}Story("isolated")` |
| `{story}_spec.{tier}.py` / `.js` | Tier-specific — e.g. `…_spec.production.js` |

---

## Example factories (link to Clean Engineering)

When Stories consume CE types, generation emits **links to factories** and **uses factory objects in scenarios** — it does not invent Fake subclasses or story-local example tables.

| Artifact | Generate |
|---|---|
| Epic helper | Import `{Type}ExampleFactory`; expose `given*` methods that call `load*({ mode })` |
| Story file (explore/spec) | Runnable GWT; `mode: "fake"`; assert public `I{Type}` |
| Tier spec (engineering) | Same story function; `mode: "isolated"` \| `"production"` |

Declare factories on the model: `Epic.example_factories` / `SubEpic.example_factories` (names like `CartExampleFactory`). Collect/normalize via `code/example_factories.py`; each converter emits imports and accessors.

**Chain (explore/spec):** steps → helper → `{Type}ExampleFactory.load…({ mode: "fake" })` → fake `I{Type}` (+ peers from the bundle) → assert public interface.

**Modes (not subclasses):** fake = mock/stub framework + `examples[{example_key}]`; isolated = `new {Type}(...injected mocks…)`; production = `new {Type}(...real collaborators…)`.

### Rules

- **`helpers-import-factories`** — Helpers import CE `{Type}ExampleFactory` from the sibling `{type}_example_factory` file (not from the production family file); they do not hand-roll Fake subclasses or invent domain objects.
- **`examples-multi-type-bundle`** — Align with CE: `examples[{example_key}]` holds all types a method needs.
- **`stories-do-not-own-ce-types`** — `I{Type}` / `{Type}` (production file) and `{Type}ExampleFactory` (factory file) live in `clean_engineering` generation; Stories only links and uses them.
- **`no-story-local-example-tables`** — Do not put `examples: [{ rank: '0', … }]` (or equivalent) in story files when a factory already owns that data.

---

# Generate

1. Confirm fidelity (`discovery` → `engineering`) and format (defaults above). All formatters available via the same CLI.
2. Read § Contexts — shared rules and the active fidelity (including its Rules).
3. Grill and sketch when useful (`@grill_with_context`, `sketch-template.md`).
4. Fill templates for the active fidelity (runnable story through specification; tier specs at engineering only).
5. Run **validate**.
