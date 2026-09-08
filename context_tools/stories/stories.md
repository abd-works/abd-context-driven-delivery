# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

---

## Guidance

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

### Guidance

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

## scenarios

**Default format:** python

**Goal:** Main-flow scenarios per story (single or multiple) with optional variations.

**Produce:** `tests/{epic}/{sub-epic}/{story}.py` — one GWT file per story. No `{story}/` folder and no `*_story` / `*_test_helper` split. Pass `format markdown` only when the strategy command names it.

Create testable specifications grounded in user system interactions through **concrete scenarios** with preconditions (**Given**), a triggering action (**When**), and observable outcomes (**Then**). **And** continues a block; start a new **When** when the actor or trigger changes. Use **Background** only when 3+ scenarios share identical starting state (Given/And only — no When/Then). Use **Scenario Outline** with `{column_name}` tokens and an **Examples** table when variation is real and steps are identical; use plain **Scenario** for distinct flows (happy path, rejection, edge case).

Use scenarios to ground the domain model. Concept names in examples must match model language exactly. Example table columns should relate data across relational structure as well.

### Guidance
Write scenarios that clearly articulate the preconditions required to start, the triggering conditions and steps to complete, and the resulting outomes.

**Start from the main-flow** scenario for each story — the happy path through Given/When/Then. Write the scenario concrete enough that a domain expert and a developer would argue about whether the output is correct. **Then walk the full interaction surface** — every distinct user-visible behavior: inline rule checklists and how they change while typing, field-level validation errors clearing as input conforms, cross-field rules (confirm password, paste mismatch), submit-button gating, and server-side error surfaces. A story that only codifies the happy path when the screen has rich client-side validation is incomplete — branch into additional scenarios (or scenario outlines with examples) per mechanical variation. Use separate Scenarios whenever the flow structure diverges.

**Provide concrete examples** add examples to specific steps in line or use a **Scenario Outline** with an Examples table when the same flow produces different outcomes based on input variation. 

**Ground scenarios in domain language** Maximize proper domain language in every Given / When / Then and in example tables. Reuse terms and operations from the domain language and model when they exist; when a step has no name yet, still phrase it in domain-observable terms — that gap signals what to add. Relate example columns across the relational structure, not one concept's fields in isolation.

### Rules

- **`gwt-steps-trace-to-domain-operations`** — Write every Given / When / Then in domain-observable terms that map to a named domain operation or property — never internals, routes, or framework mechanics. If a step cannot be traced, that is a modelling gap — add the operation or property; do not gloss over it. A hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
- **`explore-full-interaction-surface`** — Before locking scenarios (and again before acceptance_tests), walk every distinct user-visible behavior on the full interaction surface. Happy path alone is insufficient; branch scenarios to cover mechanical variations.
- **`given-only-what-the-system-checks`** — Write given statementys only conditions the system can validate. No user backstory, other off-system history E.g. no *Given the user previously browsed products* - to capture a buying behavior system will not check.
- **`when-holds-the-operation`** — When holds the domain operation being exercised. An empty When with a comment, or the operation called inside Then, is a defect. Then only asserts on what When already produced — no I/O in Then.
- **`when-names-intent-not-interface-gesture`** — When names the actor's domain intent and subject, not the button gesture used to trigger it. Write `the User activates their account using the validation code`, not `the User clicks Activate account`; write `the User resends the validation code`, not `the User clicks Resend`. Keep click/tap details in UX artifacts unless the physical interaction itself is the required behavior.
- **`and-chaining`** — The first precondtion uses `given`, event uses `when`, outcome uses `then()`; every later give, when/then in a pair on the scenario uses `.and()`. Repeated `given..  when... then..` right after each other break the narrative. Markdown `And` stays `And`.
- **`typescript-step-labels-are-plain-english`** — Preserve Markdown term markers in Markdown artifacts only. Generated TypeScript Given / When / Then strings contain plain English with no `++…++`, links, bold, italics, or other formatting syntax because test reporters render those characters literally.
- **`seed-prior-story-as-given`** — A later story's Given is seeded from prior-story fixtures (`givens.py` / `examples/`), not a replay of that story's When.
---

## acceptance_tests

**Default format:** python

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Guidance:** Follow `@stories` `#scenarios` § Guidance — acceptance_tests covers the same explored interaction surface. Take a TDD apporach and Design the code through failing scenario tests: call the realcode even when it does't exist yet. The test must fail initially (RED) — the failure message reveals the API design. Then make it pass (GREEN). Example data in tests traces to the spec's Examples table via shared fixtures — never inline invented values.

Follow the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/` — real standup first, then stub TDD, then e2e swap on request.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.py` — one GWT file per story.

### Rules

Apply every rule in `@stories` `#scenarios` § Rules where it applies at acceptance_tests fidelity.

- **`shared-example-fixtures`** — Name concrete values in `examples/` fixtures — one file per domain concept — and import them; never inline literals in scenario files. Place each fixture at the highest epic, sub-epic, or story folder that shares it.
- **`extract-assertion-helper`** — The same assertion shape more than twice becomes a named helper that takes a data bag. Call sites pass only the concrete values.
- **`infrastructure-in-lifecycle-hooks`** — Browser boot, app wiring, and `initialize` live in `beforeAll` / `afterAll`. `given(` is domain state only.

---
