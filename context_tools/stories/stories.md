# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity is derived from these behaviours, so a map of tasks or requirement rows becomes a model of operations nobody performs and tests nobody can observe.

---

## Guidance

**Think hierarchically** and use stories to progressively explore a problem and solution surface at multiple levels of detail: **Epics** (business capabilities or end-to-end outcomes), often decomposed into **Sub-Epics**, and then **Stories** (a discrete user or system action and observable system response). Stories get decomposed into **Scenarios**, and each scenarios are made up of **Steps**. `Manage User Accounts` → `Register New User` → `Enter Contact Details` → `Accept valid contact details` → `System confirms sucessful save of contact details`. The levels keep the system understandable at any granularity and traceable end to end — collapse for the business outcome, expand into the implementing detail.

**Write action-oriented interactions** between users and systems; at every level the thinking pattern is the same: actor–action–subject with an optional qualifier. A noun-only node — `Payments` — does not say what done looks like or how you would know it is working; you should understand a story at a glance without looking inside of it. An epic, a sub-epic, a story, a scenario, and each step in a scenario, all are saying the same thing at a different horizon and different level of detail. Size each level so it contains no more than 7–9 items at the next level down — too many creates cognitive overload; too few means passing through too many nodes to reach too little. When a node has too many children, promote it or break it up; when it has too few, absorb it into its parent.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present. One shared definition gets expanded and reused by every story; invent your own words and each story has to be interpreted from scratch.
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory! Titles show you words, not mechanics, and every later fidelity inherits the hierarchy you build from them.
- **`do-not-invent-requirements`** — Only write stories for behaviours the source describes or the user explicitly asks for. Do not add statuses, warning badges, maintenance chores, or extra data fields the source never mentions. Invented scope becomes real stories, screens, and tests nobody asked for.

---

## story_map

**Default format:** markdown

**Produce:** Story map.

**Goal:** Define a visual, hierarchical model of how users and systems interact with a product or service; as a hiererachy of — `Epic` → nestable `SubEpic` → `Story`. It is much easier to change the map while stories are still titles than after scenarios, screens, and tests have been written under them. Missing scope shows up here as a gap, not as rework halfway through the build.


**Actors** are users or systems that interact with the system.

**Epics** are major capability areas — containers for flows. Named verb–noun: `Manage Customer Orders`, `Process Payments`. Epics nest into **SubEpics**,  then **Stories** — each a discrete, observable behavior independently testable. Stories are verb–noun (`Place Order`, `Validate Payment`); and are behaviors, not tasks.

### Guidance

**Decompose the hierarchy** using user and system interactions  — epics covering the full capability surface. Ground each epic with a few confirming stories that prove the epic is real and the scope is right — an ungrounded epic is a heading nobody can disagree with.  **Then find the spine** — the smallest end-to-end slice that works and delivers business value. Validate it early, then grow later increments from what users actually use and what you learned about the architecture and design — without a spine you spread effort across features before anything works end to end. Keep increments small by spliting along Actors, Data, Workflow, Channel, Interfaces, NFRs, or Business Rules.

**Consider the full scope** Map all the interactions required to achieve a business outcome — not just the primary user's forward path. Include supporting actors (administrators, call centre agents, operations) and the activities that make the product work: configuring catalogs, setting up pricing rules, onboarding partners. Then check for the reverse and defensive paths: cancellations, refunds, escalations, error recovery. A forward-path-only map looks finished, so that work arrives after the model and screens are already shaped around the happy path. For multi-system solutions, map each distinct system-to-system hop as its own story using the same behaviour-oriented language: `Validate Payment Eligibility`, `Authorize Card Transaction`.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates.

Rough story-map outline for a **partition** pass or first cut — **names only**: verb–noun epics + story names (`StoryMap` → `Epic` → `SubEpic` → `Story`). No scenarios, no thin-slice increments, no scope prose yet.

Key rules: `branch-on-mechanical-uniqueness` — split on distinct mechanics, not one story per catalog or requirements entry; `read-all-source-context-in-full` — read segments in full before grouping.

### Rules

- **`verb-noun-format`** — Name Epic / SubEpic / Story verb–noun; actor is metadata; base verb form. A noun-only name does not say what done looks like, how to test it, or how to tell it is working — you cannot understand the story at a glance without looking inside of it.
- **`four-to-nine-children`** — 4–9 direct children (warn at 3/10; error ≤2 or ≥11). Too many creates cognitive overload; too few means passing through too many nodes to reach too little — both make the map harder for a reader or agent to reason about.
- **`branch-on-mechanical-uniqueness`** — Explore context relentlessly for distinct mechanics. Branch on mechanical uniqueness, dstinct mechanics in requirements require *distinct stories* for each mechanic. Different requirement entries with same mechanic is *one story only with different examples or scenarios*. Collapsing real mechanical variation, as well as mindlessly turning requirements into long lists of stories are **defect** — a collapsed mechanic is work nobody planned; one story per requirement entry multiplies scenarios and tests over behaviour one story already covers.
- **`right-size-story-nodes`** — One demonstrable interaction per story. Bigger needs several Whens; smaller is a step in somebody else's story.
- **`behaviours-not-one-time-tasks`** — A Story is a repeatable stakeholder/system interaction you can specify Given/When/Then against more than once. One-time maintainer chores (rename X to Y, copy/migrate an asset once, one-off repo surgery) are not Stories — keep them in the plan/todos. Once done, the result is ordinary inventory the remaining stories already cover.
- **`do-not-invent-requirements`** — same rule as Shared.

**Stop reading this skill when scaffolding.**
---

## scenarios

**Default format:** python

**Goal:** Refine stories into scenarios based on real world examples. A scenario with examples is both the requirement and the test — written before any code. Scenarios are clearer than ungrounded system description; examples spell out what to build and convert straight into automated tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.py` — one GWT file per story. No `{story}/` folder and no `*_story` / `*_test_helper` split. Pass `format markdown` only when the strategy command names it.


### Guidance
Write scenarios that clearly articulate the preconditions required to start, the triggering conditions and steps to complete, and the resulting outomes.

**Create testable specifications** grounded in user and system interactions through **concrete scenarios** with preconditions (**Given**), a triggering action (**When**), and observable outcomes (**Then**) — state the starting conditions, the event, and the reaction separately; leaving these out makes it hard to tell whether something failed because the setup was wrong, the trigger was wrong, or the outcome was wrong.  **And** continues a block; start a new **When** when the actor or trigger changes so it is clear which action produced which outcome. Use **Background** to put shared setup in one place so scenarios show only what differs.

**Start from the main-flow** scenario for each story — the happy path through Given/When/Then. Write the scenario concrete enough that a domain expert and a developer would not argue about whether the output is correct. **Then walk the full interaction surface** — every distinct user-visible behavior: inline rule checklists and how they change while typing, field-level validation errors clearing as input conforms, cross-field rules (confirm password, paste mismatch), submit-button gating, and server-side error surfaces. A story that only codifies the happy path when the screen has rich client-side validation is incomplete — branch into additional scenarios (or scenario outlines with examples) per mechanical variation. Use separate Scenarios whenever the flow structure diverges. Unnamed behaviour still gets implemented — from guesswork, and untested.

**Provide concrete examples** add examples to scenarios with real concrete data. An abstract step passes review because nobody can be wrong about it; the errors stay uncaught until users actually test it. Use **Scenario Outline** with `{column_name}` tokens in steps and an **Examples** table when the steps are the same and only the data changes — This allows the table to carry the variation in functionality without having to copying the same scenario n times. Relate example columns across the relational structure so relationships show up in the examples, not only in a diagram later. Use plain **Scenario** when the flow itself changes in a story (happy path, rejection, edge case) — so a different sequence of steps does not hide in a table cell.


**Ground scenarios in domain language**  Reuse terms and operations from the domain language and model when they exist; when a step has no name yet, still phrase it in domain-observable terms- a signal to update the domain model. This aligns scenarios to how the business speaks and what engineers will code.

### Rules

- **`gwt-steps-trace-to-domain-operations`** — Write every Given / When / Then in domain-observable terms that map to a named domain operation or property — never internals, routes, or framework mechanics. If a step cannot be traced, that is a modelling gap — add the operation or property; do not gloss over it. A hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
- **`explore-full-interaction-surface`** — Before locking scenarios (and again before acceptance_tests), walk every distinct user-visible behavior on the full interaction surface. Happy path alone is insufficient; branch scenarios to cover mechanical variations. An unspecified behaviour gets built from guesswork with no test watching it.
- **`given-only-what-the-system-checks`** — Write given statements using only conditions the system can validate. No user backstory or other off-system history; for example, no *Given the user previously browsed products* when the system does not check that behavior. A precondition the system never requires hides the ones it does require.
- **`when-holds-the-operation`** — When holds the domain operation being exercised. An empty When with a comment, or the operation called inside Then, is a defect. Then only asserts on what When already produced — no I/O in Then. With the trigger inside the assertion, the test cannot fail for the reason it claims to check.
- **`when-names-intent-not-interface-gesture`** — When names the actor's domain intent and subject, not the button gesture used to trigger it. Write `the User activates their account using the validation code`, not `the User clicks Activate account`; write `the User resends the validation code`, not `the User clicks Resend`. Keep click/tap details in UX artifacts unless the physical interaction itself is the required behavior.
- **`and-chaining`** — The first precondition uses `given`, event uses `when`, and outcome uses `then()`; every later Given, When, or Then in the same block uses `.and()`. Repeated `given.. when... then..` blocks break the narrative. Markdown `And` stays `And`. Restarted blocks read as several steps in one, hiding which trigger produced which outcome.
- **`typescript-step-labels-are-plain-english`** — Preserve Markdown term markers in Markdown artifacts only. Generated TypeScript Given / When / Then strings contain plain English with no `++…++`, links, bold, italics, or other formatting syntax because test reporters render those characters literally.
- **`seed-prior-story-as-given`** — A later story's Given picks up where prior stories left off — seed it from fixtures (`givens.py` / `examples/`) or the final Then examples, not by replaying prior scenarios. Replaying prior When steps re-tests behaviour already covered and chains tests together so you cannot run one story in isolation.
---

## acceptance_tests

**Default format:** python

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`. A running test either passes or fails — there is no ambiguous middle. Driving the code from tests makes whether each requirement is met unambiguous.

**Guidance:** Follow `@stories` `#scenarios` § Guidance — acceptance_tests covers the same explored interaction surface. Take a TDD apporach and Design the code through failing scenario tests: call the realcode even when it does't exist yet. The test must fail initially (RED) — the failure message reveals the API design. Then make it pass (GREEN). Example data in tests traces to the spec's Examples table via shared fixtures — never inline invented values.

Follow the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/` — real standup first, then stub TDD, then e2e swap on request.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.py` — one GWT file per story.

### Rules

Apply every rule in `@stories` `#scenarios` § Rules where it applies at acceptance_tests fidelity.

- **`shared-example-fixtures`** — Share example data across story tests through `examples/` fixtures and import them from each story's test code. One file per domain concept at the folder level where that concept is shared — sub-epic when only those stories need it, epic when the whole epic shares it, higher when broader. Without shared fixtures the same concept gets rewritten in every story test and the copies stop matching.
- **`extract-assertion-helper`** — The same assertion shape more than twice becomes a named helper that takes a data bag. Call sites pass only the concrete values. The copy you miss keeps passing against behaviour the system no longer has.
- **`infrastructure-in-lifecycle-hooks`** — Browser boot, app wiring, and `initialize` live in `beforeAll` / `afterAll`. `given(` is domain state only. Setup dressed as a Given hides what the behaviour actually requires.

---
