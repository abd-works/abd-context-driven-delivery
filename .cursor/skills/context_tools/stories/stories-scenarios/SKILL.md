---
name: stories-scenarios
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-scenarios

Use stories guidance at `scenarios` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-story_map
@stories-scaffold

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | typescript | Main-flow scenarios per story (single or multiple); optional variations; `examples/` + `givens.ts`. Pass `format markdown` when the strategy asks for a markdown view. |
| **acceptance_tests** | typescript | `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam (`front-end`, `back-end`, or another system name). No story folder. Fixtures: `examples/` + `givens.ts`. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.ts` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## scenarios

**Default format:** typescript

**Goal:** Main-flow scenarios per story (single or multiple) with optional variations.

**Produce:** Same `{story}.{tier}.ts` tree as acceptance_tests. Pass `format markdown` only when the strategy command names it.

### Rules

- **`behavioral-observable-outcomes`** — Name and Then in domain-observable terms; never internals.
- **`explore-full-interaction-surface`** — Scenarios are not complete when only the main-flow GWT from the sketch is written. Before locking scenarios (and again before acceptance_tests), walk the real UI and model **every distinct user-visible behavior**: inline rule checklists and how they change while typing, field-level validation errors clearing as input conforms, cross-field rules (confirm password, paste mismatch), submit-button gating, and server-side error surfaces. A story that only codifies the happy path when the screen has rich client-side validation is a **defect** — branch into additional scenarios (or scenario outlines with examples) per mechanical variation, not one paragraph that mentions "validation" in passing.
- **`gwt-steps-trace-to-domain-operations`** — Every Given / When / Then maps to a named domain operation or property. If a step cannot be traced, that is a modelling gap — add the operation or property; do not gloss over it. A hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
- **`reconcile-live-immediately`** — The running app wins. When a walk-through disagrees with the sketch, fix the sketch in that increment before locking the test.
- **`explain-deep-link-arrival`** — A scenario that navigates to a parameterized route (`/sign-up/:planId`) must say how a user actually arrives: in-app navigation, marketing/external deep-link, or a wizard step with no URL change. Do not write `When they navigate to X` as if it were a button.
- **`given-only-what-the-system-checks`** — Given states conditions the **running system actually uses** for the behaviour under test. Do not Given a field the code never reads for that decision (`metadata.verified` when routing actually keys off `customer.billing.id`).
- **`when-holds-the-operation`** — When holds the domain operation being exercised. An empty When with a comment, or the operation called inside Then, is a defect. Then only asserts on what When already produced — no I/O in Then.
- **`then-and-chaining`** — The first outcome uses `then()`; every later outcome on the same interaction chains `.and()`. Repeated `then()` calls break the Gherkin narrative. Markdown `And` stays `And`.
- **`extract-assertion-helper`** — The same assertion shape more than twice becomes a named helper that takes a data bag. Call sites pass only the concrete values.
- **`infrastructure-in-lifecycle-hooks`** — Browser boot, app wiring, and `initialize` live in `beforeAll` / `afterAll`. `given(` is domain state only.
- **`load-with-identity-in-hand`** — `load` takes the identity already in hand. Do not assume a browser session. Load once at the highest Given that needs the aggregate and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- **`seed-prior-story-as-given`** — A later story's Given is seeded from prior-story fixtures (`givens.ts` / `examples/`), not a replay of that story's When.
- **`reuse-owning-aggregate-stubs`** — For a non-core aggregate, take stubs from **that aggregate's folder / source repository** (`domain/{bounded-context}/{aggregate}/stubs/{system}/`). Do not invent a test-local stub. Do not stub the seam you are proving.

---

## Templates

### markdown

## components/evidence-table.md

---
fidelity: [exploration, specification]
artifact: [story-scenarios]
format: md
section: footer
---

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | `<source>` | `<location>` |


## components/story-header.md

---
fidelity: [exploration, specification]
artifact: [story-scenarios]
format: md
section: header
---
## Story: `<Verb–Noun Title>`

**Story type:** user | system | technical

**Sources / context:** `<pointer to domain source, AC, or conversation>`

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).


## scenario-inline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

## Behaviors

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Scenario 1: `<outcome-oriented scenario name>`

*Given* a ++`<ConceptA>`++ *`<value>`*  
  *And* that ++`<ConceptA>`++ *`<value>`* has a ++`<ConceptB>`++ *`<value>`*  
*When* the ++`<ConceptA>`++ *`<value>`* `<triggering action>`  
    using ++`<ConceptB>`++ *`<value>`*  
*Then* the ++`<observed concept>`++ is `<observable outcome>`  
  *And* the ++`<related concept>`++ is `<additional outcome>`  
  *But* no ++`<concept>`++ is `<what does not happen>`

### Scenario 2: `<alternate outcome-oriented scenario name>`

*Given* `<alternate setup state>`  
*When* `<alternate triggering action>`  
*Then* `<alternate observable outcome>`  
  *And* `<additional outcome>`


## scenario-main-flow.md

---
fidelity: [exploration]
artifact: [story-scenarios]
format: md
section: body
---

### Domain terms

- ++`<Concept>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

## Behaviors

### Scenario Outline: `<main-flow outcome name>`

*Given* a ++`<Concept>`++ from `helper.given<Concept…>({ mode: "fake" })`  
  *And* that ++`<Concept>`++ {`<concept_field>`}  
*When* the **`<Actor>`** `<triggering action>`  
*Then* `<observable outcome on the public interface of I{Concept}>`  
  *And* `<additional observable outcome>`

### Examples

| scenario   | `<concept_field>` | `<result_field>` |
|------------|-------------------|------------------|
| ++Scenario 1++ | `<value>`         | `<value>`        |

> Examples table documents the representative row. Code loads the same values from ExampleFactory (AI fills stubs).


## scenario-outline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Evidence

| Source | Note |
|--------|------|
| `<pointer>` | `<why it matters>` |

### Background

*Given* a ++`<ConceptX>`++ from `helper.given<ConceptX…>({ mode: "fake" })`  
  *And* that ++`<ConceptX>`++ exposes `<public property / operation>`  

---

### Behaviors

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++`<ConceptA>`++ with {`<field_1>`}  
  *And* the ++`<ConceptB>`++ for that ++`<ConceptA>`++ is {`<field_2>`}  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ `<outcome>` is visible on the public interface  
  *And* a ++`<related concept>`++ shows {`<field_3>`}

### Examples

| scenario   | `<field_1>` | `<field_2>` | `<field_3>` |
|------------|-------------|-------------|-------------|
| ++Scenario 1++ | `<value>`   | `<value>`   | `<value>`   |
| ++Scenario 2++ | `<value>`   | `<value>`   | `<value>`   |

> Markdown keeps examples tables for documentation. Code wires values via `{Type}ExampleFactory` (AI fills helper/story method bodies). Do not copy inventable `examples: [{ … }]` literals into code story files.

#### Scenario: `<variation — delta from main flow>`

*Given* … (only the delta from the main flow)  
*When* …  
*Then* …

### python

## scenario-template.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# # Params — fill before writing code
# epic:       {epic-verb-noun}           # kebab folder under tests/
# sub_epic:   {sub-epic-verb-noun}       # kebab folder under epic/ (omit level if story hangs off epic)
# story:      {story-verb-noun}          # Verb Noun title from the story map
# story_file: {story_snake_slug}         # snake file slug, e.g. sign_up_create_account
# tier:       e2e | front-end | back-end | {system}
#
# # Artifact layout (artifacts-mirror-story-hierarchy)
# tests/
#   {epic-verb-noun}/
#     examples/                          # epic-shared ExampleFactory values (when shared)
#     givens.py                          # epic-shared background Given helpers
#     whens.py                           # epic-shared When helpers (when shared)
#     {sub-epic-verb-noun}/              # omit this level when the story file lives under epic/
#       examples/{topic}_examples.py     # lowest shared folder for this story's fixtures
#       givens.py                        # background Given helpers for this sub-epic/story
#       whens.py                         # When helpers for this sub-epic/story
#       {story_snake_slug}.{tier}.py     # THIS FILE — one GWT file per story per tier
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Examples module        → examples/{topic}_examples.py (concrete values, not inline in GWT)
# - Epic helper (py only)  → {epic_snake}_helper.py — sole snake_case naming exception
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: mirror sign-up-create-account.e2e.ts (Mamba/RSpec via story_test).

from __future__ import annotations

from expects import be_none, equal, expect
from mamba import after, before, description

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from examples.{story_verb_noun}_examples import (
    invalid_{field}_example,
    valid_{aggregate}_example,
    valid_{field}_example,
)
from givens import {background_given_fn}
from story_test import background, scenario, story
from whens import {primary_when_fn}


with description("{Story Verb-Noun}") as story_ctx:
    story_ctx.{app_camel}: {AppPascal} | None = None
    story_ctx.{aggregate_camel}: {AggregatePascal} | None = None

    with before.all:
        def _boot() -> None:
            story_ctx.{app_camel} = {AppPascal}E2e.initialize(config)

    with after.all:
        def _shutdown() -> None:
            if story_ctx.{app_camel} is not None:
                story_ctx.{app_camel}.close()

    def _story_body() -> None:
        def _background(given):  # type: ignore[no-untyped-def]
            given("{background given step}", lambda: {background_given_fn}(story_ctx.{app_camel}))

            def _validation_branch(steps):  # type: ignore[no-untyped-def]
                when, then = steps["when"], steps["then"]

                when("{primary when step}", lambda: _primary_when())
                when("{follow-on when step}", lambda: _invalid_input())
                then("{validation message on domain object}", lambda: expect(
                    story_ctx.{aggregate_camel}.errors.{field}
                ).to(equal({ERROR_CONSTANT}_MESSAGE)))

            scenario("{validation branch while typing}", _validation_branch)

            def _clears_when_valid(steps):  # type: ignore[no-untyped-def]
                when, then = steps["when"], steps["then"]

                (
                    when("{primary when step}", lambda: _primary_when())
                    .and_("{prior invalid state}", lambda: _invalid_input())
                )
                when("{corrective action}", lambda: _valid_input())
                then("{error cleared on domain object}", lambda: expect(
                    story_ctx.{aggregate_camel}.errors.{field}
                ).to(be_none))

            scenario("{validation clears when input conforms}", _clears_when_valid)

            def _main_flow(steps):  # type: ignore[no-untyped-def]
                when, then = steps["when"], steps["then"]

                when("{primary when step}", lambda: _primary_when())
                when("{submit operation on domain object}", lambda: _submit())
                then("{post-condition on loaded aggregate}", lambda: _expect_state())

            scenario("{main-flow outcome}", _main_flow)

        background(_background)

    def _primary_when() -> None:
        story_ctx.{aggregate_camel} = {primary_when_fn}(story_ctx.{app_camel})

    def _invalid_input() -> None:
        creds = story_ctx.{aggregate_camel}
        creds.{field} = invalid_{field}_example
        creds.validate()

    def _valid_input() -> None:
        creds = story_ctx.{aggregate_camel}
        creds.{field} = valid_{field}_example
        creds.validate()

    def _submit() -> None:
        creds = story_ctx.{aggregate_camel}
        creds.{field} = valid_{aggregate}_example.{field}
        creds.{operation}()

    def _expect_state() -> None:
        {entity_camel} = story_ctx.{app_camel}.{repository}().load(story_ctx.{aggregate_camel})
        expect({entity_camel}.is_at_{state}("{StateName}")).to(equal(True))

    story("{Story Verb-Noun}", _story_body)

See examples in `context_tools/stories/examples/` if needed.