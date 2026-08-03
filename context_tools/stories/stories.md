# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution. Deepen fidelity; never invent detail from a deeper level.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples (from CE `{Type}ExampleFactory` when available — never invent rows in story files).

| Fidelity | Default Format | Produce |
|---|---|---|
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

# Scaffold

A scaffold produces a thin epic index — verb–noun epics + mid-level grounding story stubs (`StoryMap` → `Epic` → `SubEpic` → `Story` → `Scenario`).

Key rules: `branch-on-mechanical-uniqueness` — split on distinct mechanics, not catalog/requirements rows; `read-all-source-context-in-full` — read segments in full before grouping.
