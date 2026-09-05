---
name: stories-story_map
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-story_map

Use stories guidance at `story_map` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-scaffold

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | python | Main-flow scenarios per story — `{story}.{tier}.py` GWT files. Pass `format markdown` only when the strategy asks for a markdown view. |
| **acceptance_tests** | python | Same `{story}.{tier}.py` tree as scenarios. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.py` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## story_map

**Default format:** markdown

**Goal:** Shape the hierarchy — `Epic` → nestable `SubEpic` → `Story` — decomposed on real mechanical variation, not requirement-row bookkeeping.

**Produce:** Story map + thin-slice.

### Rules

- **`verb-noun-format`** — Name Epic / SubEpic / Story verb–noun; actor is metadata; base verb form.
- **`four-to-nine-children`** — 4–9 direct children (warn at 3/10; error ≤2 or ≥11).
- **`branch-on-mechanical-uniqueness`** — Explore context relentlessly for distinct mechanics. Branch on mechanical uniqueness, dstinct mechanics in requirements require *distinct stories* for each mechanic. Different requirement entries with same mechanic is *one story only with different examples or scenarios*. Collapsing real mechanical variation, as well as mindlessly turning requirements into long lists of stories are **defect**
- **`right-size-story-nodes`** — One demonstrable interaction per story.
- **`behaviours-not-one-time-tasks`** — A Story is a repeatable stakeholder/system interaction you can specify Given/When/Then against more than once. One-time maintainer chores (rename X to Y, copy/migrate an asset once, one-off repo surgery) are not Stories — keep them in the plan/todos. Once done, the result is ordinary inventory the remaining stories already cover.
- **`do-not-invent-requirements`** — same rule as Shared: no invented Status/stale/warning-badge concepts; no competing command/invoke surface beside one already specified; unconfigured = no row + existing fallback.

---

## Templates

### markdown

## story-map.md

---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories.
     Do not wrap epic, sub-epic, story, or actor names in backticks. -->

# Story Map — Product / Feature Name

**Sources / context:** context files used

---

(E) Epic Verb–Noun
    (E) Sub-Epic Verb–Noun
        (S) Actor --> Story Verb–Noun
        (S) Actor --> Story Verb–Noun
    (E) Sub-Epic Verb–Noun
        (S) Actor --> Story Verb–Noun

---

## Scope boundary

**In scope:** what is included
**Out of scope:** what is explicitly excluded

---

## Thin slices

### Increment 1: Marketable outcome

**Outcome:** What users or the business can do after this ships

**Stories:**
- Story Verb–Noun
- Story Verb–Noun


## thin-slice.md

---
fidelity: [discovery]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — `<Product / Feature Name>` incremental backlog

## Product / context

**Product:** `<one-line product / feature description>`

**Slicing intent:** `<why these slices in this order — value logic, learning goals, risk gates>`

**Spine vs optional:** `<the mandatory sequential flow for core value>` sits on the spine. `<alternate channels, enhancements, non-happy-path depth>` are real work but not required for the smallest marketable slice.

## Increments

### Increment 1: `<Marketable outcome name>`

**Outcome:** `<one line — what users or the business can do after this ships>`

**Slicing notes:** `<manual steps, stubs, single channel, reduced NFRs, which slicing dimension was used>`

**Stories in this increment** *(order reflects flow within the slice):*

- *`<First story verb-noun>`*
- *`<Second story verb-noun>`*
- *`<Third story verb-noun>`*

### Increment 2: `<Next marketable outcome>`

**Outcome:** `<capability after this increment>`

**Slicing notes:** `<optional>`

**Stories in this increment:**

- *`<Story verb-noun>`*
- *`<Story verb-noun>`*

See examples in `context_tools/stories/examples/` if needed.