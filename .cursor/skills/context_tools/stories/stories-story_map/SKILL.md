---
name: stories-story_map
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-story_map

Use stories guidance at `story_map` fidelity only.

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

---

## Mental model

**Think hierarchically** and use stories to progressively explore a problem and solution surface at multiple levels of detail: **Epics** (business capabilities or end-to-end outcomes), often decomposed into **Sub-Epics**, and then **Stories** (a discrete user or system action and observable system response). Stories get decomposed into **Scenarios**, and each scenarios are made up of **Steps**. `Manage User Accounts` → `Register New User` → `Enter Contact Details` → `Accept valid contact details` → `System confirms sucessful save of contact details`.

**Write action-oriented interactions** between users and systems; at every level the thinking pattern is the same: actor–action–subject with an optional qualifier. An epic, a sub-epic, a story, a scenario, and each step in a scenario, all are saying the same thing at a different horizon and different level of detail. Size each level so it contains no more than 7–9 items at the next level down. When a node accumulates too many children, promote it or break it up; when it has too few, absorb it into its parent.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.py` files (no per-story directory).
- **`kebab-case-paths`** — Epic and SubEpic **folder** names, story **file** stems, and tier segments use lowercase kebab-case (`sign-up`, `front-end`). No `snake_case` folders or `PascalCase` paths. **Exception:** Python epic helper only — `{epic_slug}_helper.py` at the epic folder root; nothing else may use underscores.
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render.

---

## story_map

**Default format:** markdown

**Produce:** Story map.

**Goal:** Define a visual, hierarchical model of how users and systems interact with a product or service; as a hiererachy of — `Epic` → nestable `SubEpic` → `Story`.


**Actors** are users or systems that interact with the system.

**Epics** are major capability areas — containers for flows. Named verb–noun: `Manage Customer Orders`, `Process Payments`. Epics nest into **SubEpics**,  then **Stories** — each a discrete, observable behavior independently testable. Stories are verb–noun (`Place Order`, `Validate Payment`); and are behaviors, not tasks.

### Mental model

**Decompose the hierarchy** using user and system interactions  — epics covering the full capability surface. Ground each epic with a few confirming stories that prove the epic is real and the scope is right.  **Then find the spine** — the thinnest end-to-end path that delivers core value. Sketch later increments to show where the remaining scope lands.   Keep increments small by spliting along Actors, Data, Workflow, Channel, Interfaces, NFRs, or Business Rules.

**Consider the full scope** Map all the interactions required to achieve a business outcome — not just the primary user's forward path. Include supporting actors (administrators, call centre agents, operations) and the activities that make the product work: configuring catalogs, setting up pricing rules, onboarding partners. Then check for the reverse and defensive paths: cancellations, refunds, escalations, error recovery. For multi-system solutions, map each distinct system-to-system hop as its own story using the same behaviour-oriented language: `Validate Payment Eligibility`, `Authorize Card Transaction`.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates. 

Rough story-map outline for a **partition** pass or first cut — **names only**: verb–noun epics + story names (`StoryMap` → `Epic` → `SubEpic` → `Story`). No scenarios, no thin-slice increments, no scope prose yet.

Key rules: `branch-on-mechanical-uniqueness` — split on distinct mechanics, not catalog/requirements rows; `read-all-source-context-in-full` — read segments in full before grouping.

### Rules

- **`verb-noun-format`** — Name Epic / SubEpic / Story verb–noun; actor is metadata; base verb form.
- **`four-to-nine-children`** — 4–9 direct children (warn at 3/10; error ≤2 or ≥11).
- **`branch-on-mechanical-uniqueness`** — Explore context relentlessly for distinct mechanics. Branch on mechanical uniqueness, dstinct mechanics in requirements require *distinct stories* for each mechanic. Different requirement entries with same mechanic is *one story only with different examples or scenarios*. Collapsing real mechanical variation, as well as mindlessly turning requirements into long lists of stories are **defect**
- **`right-size-story-nodes`** — One demonstrable interaction per story.
- **`behaviours-not-one-time-tasks`** — A Story is a repeatable stakeholder/system interaction you can specify Given/When/Then against more than once. One-time maintainer chores (rename X to Y, copy/migrate an asset once, one-off repo surgery) are not Stories — keep them in the plan/todos. Once done, the result is ordinary inventory the remaining stories already cover.
- **`do-not-invent-requirements`** — same rule as Shared: no invented Status/stale/warning-badge concepts; unconfigured = no row + existing fallback.

**Stop reading this skill when scaffolding.**
---

## Sketching

When sketching, use the sketch template at `stories/templates/stories-sketch.md`. Do not use the produce templates below — stop reading this skill when sketching.

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

See examples in `context_tools/stories/examples/` if needed.