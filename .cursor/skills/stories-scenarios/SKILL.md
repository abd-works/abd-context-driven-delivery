---
name: stories-scenarios
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-scenarios

Use stories guidance at `scenarios` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-story_map

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

---

## Guidance

**Think hierarchically.** Use **Epics** for business capabilities or end-to-end outcomes, **Sub-Epics** for outcomes within an Epic, and **Stories** for discrete user or system interactions with observable results. Decompose Stories into **Scenarios**, then express each Scenario as **Given**, **When**, and **Then** steps. The hierarchy lets a reader move from the business outcome to the behaviour that implements it without losing traceability.

**Write action-oriented interactions.** At every level, name the actor, action, and subject when the format includes actor metadata; name nodes with a base-form verb and a noun. `Manage Customer Orders` says what the Epic achieves, while `Orders` does not. Keep 4-9 direct children under a node, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because shallow chains and crowded nodes both hide the shape of the work.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** - Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.
- **`read-all-source-context-in-full`** - Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.
- **`do-not-invent-requirements`** - Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.
- **`evidence-distinguishes-observed-inferred-and-intended`** - Label behaviour as observed, inferred, or intended and cite its source. When available evidence cannot exercise required behaviour, write the intended GWT and state the limitation, because an unobserved expectation must not be presented as a fact.

---

## scenarios

**Default format:** project language

**Produce:** Scenario specifications in the requested format.

**Goal:** Refine Stories into concrete examples with preconditions, triggering operations, and observable outcomes. A Scenario defines both the required behaviour and the evidence that will show whether it works.

### Guidance

**Create testable specifications.** Use **Given** for state the system already has, **When** for the operation under test, and **Then** for results a person or another system can observe. Use **And** to continue the current kind of step. Use **But** for a missing record or an action not taken. Start a new **When** only when a new interaction begins, because each outcome must trace to the operation that produced it.

**Start with the main flow, then inspect every variation.** Cover the successful path first, then validation, field-level errors, cross-field rules, operation gating, service failures, reversals, and recovery that the sources or running product contain. Use separate Scenarios when the flow changes and a Scenario Outline when the same flow applies to many data combinations.

**Use concrete examples.** Put real domain values in Examples so domain experts and developers can agree on the expected result. Relate examples through domain keys when the model relates them. Acceptance tests represent the same named examples as code fixtures rather than inventing new values. Every example field must change an input, rule, or expected result, because unused data makes the behaviour harder to see.

**Use the correct evidence mode.** For brownfield capture, inspect the running product when it exists and reconcile the Story Map and Scenarios with observed behaviour before finalizing them. For greenfield specification, agreed Scenarios define intended behaviour before production code exists.

### Rules

- **`gwt-steps-trace-to-domain-operations`** - Map every Given, When, and Then to a named domain operation or property. Express continuation as an operation on the aggregate that receives control, because routes, waits, and framework calls do not describe domain behaviour.
- **`behavioral-and-system-observable-outcomes`** - Write each Then as a result a person or another system can observe, such as changed information, a returned response, or a changed interface state. Keep internal flags and function-local state out of Then, because they do not prove delivered behaviour.
- **`explore-full-interaction-surface`** - Before finalizing Scenarios and again before generating acceptance tests, inspect every distinct visible behaviour required by the source or running product. Add Scenarios for distinct mechanics, because a happy path cannot protect validation and failure behaviour.
- **`reconcile-live-immediately`** - In brownfield work, update the map and Scenario in the same increment when the running product contradicts the current description. Mark intended changes separately, because observed and desired behaviour are different evidence.
- **`flagged-writes-intended-gwt`** - When available evidence cannot exercise required behaviour, write the intended Given, When, and Then and state what evidence is missing, because an evidence gap must not erase the requirement or turn an expectation into an observed fact.
- **`scenario-names-continuation`** - Put the main flow first and make each continuing Then name the next Story on the map. Add a missing map node when a live path continues without one, because Scenarios are alternate flows within Stories rather than substitutes for Stories.
- **`given-only-what-the-system-checks`** - Describe the activity and state that the system actually uses for this behaviour, including state left by a prior Story. Omit off-system history, orphan data, screen names used as state, and fields the decision never reads, because irrelevant setup hides the real preconditions.
- **`given-names-complex-state-root-first`** - Begin complex Given state with the aggregate root, then describe its owned parts in their current state, because an owned entity does not have independent context outside its aggregate.
- **`but-marks-missing-state`** - Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects.
- **`when-holds-the-operation`** - Put the operation under test in When and, in Then, assert only results it has already produced. For downstream system Stories, describe the request arriving at that system instead of replaying the original user action. Specify enablement and activation as separate behaviours when both are observable, because triggers inside assertions and combined operations hide which action caused the result.
- **`when-names-intent-not-interface-gesture`** - Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable.
- **`expressive-system-interactions`** - Describe each system's When and Then in that system's vocabulary. A caller's Then names the result it receives; a translating intermediary names the incoming caller concept and the returned caller-facing result, because "calls the service" does not explain the work performed.
- **`and-chaining`** - Start each state, interaction, and result block with Given, When, and Then, then continue later steps of the same kind with And. Keep Given conditions in root-first order, start a new When for a new interaction, and keep one interaction's observable results in one Then/And block. Use Background only when more than one Scenario shares the state, because repeated keywords hide which conditions, actions, and results belong together.
- **`outline-requires-many-permutations`** - Use a Scenario Outline when many data combinations follow the same steps. Use separate steps or Scenarios for two alternatives or a changed flow, and keep only example fields that affect behaviour, because examples should show variation rather than conceal structure.
- **`plain-english-gwt-steps`** - Write each step as a readable sentence with a named actor and observable behaviour. Use the plain-English example name rather than a code identifier, because test reports must make sense without source code.
- **`explain-deep-link-arrival`** - When a Scenario starts at a parameterized route or equivalent application state, name the real arrival path: product navigation, an external deep link, or a preceding flow state. A route is not a user action.
- **`seed-prior-story-as-given`** - Seed a later Story from examples produced by prior Stories instead of replaying their When steps. Reuse fixtures from the owning domain concept and keep the boundary under test real, because each Story must run independently while proving its own behaviour.

---

## Sketching

When sketching, use the sketch template at `stories/templates/stories-sketch.md`. Do not use the produce templates below — stop reading this skill when sketching.

## Templates

### markdown

## scenario-template.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

<!-- Default: Scenario Outline + Examples table. Alternate: inline sibling scenarios below.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story-kebab-slug}.py|md
     — kebab-case folders and file stems; one file per story; no {story}/ folder.
     Exception: Python epic helper only — {epic_slug}_helper.py at epic root.

     Outcome chaining: first *Then* on a step; further outcomes on the same *When* use *And*
     (not a second *Then*). New *When* when actor or trigger changes. -->

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

## Behaviors

### Default — Scenario Outline

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++`<ConceptA>`++ with {`<field_1>`}  
  *And* the ++`<ConceptB>`++ for that ++`<ConceptA>`++ is {`<field_2>`}  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ `<outcome>` is visible on the public interface  
  *And* a ++`<related concept>`++ shows {`<field_3>`}

#### Examples

| scenario   | `<field_1>` | `<field_2>` | `<field_3>` |
|------------|-------------|-------------|-------------|
| ++Scenario 1++ | `<value>`   | `<value>`   | `<value>`   |
| ++Scenario 2++ | `<value>`   | `<value>`   | `<value>`   |

> Markdown keeps examples tables for documentation. Code wires values via `{Type}ExampleFactory` (AI fills helper/story method bodies). Do not copy inventable `examples: [{ … }]` literals into code story files.

#### Scenario: `<variation — delta from the outline>`

*Given* … (only the delta from the outline)  
*When* …  
*Then* …

---

### Alternate — inline scenarios

Use when an examples table adds no value — express mechanical variation as sibling scenarios instead.

#### Scenario 1: `<outcome-oriented scenario name>`

*Given* a ++`<ConceptA>`++ *`<value>`*  
  *And* that ++`<ConceptA>`++ *`<value>`* has a ++`<ConceptB>`++ *`<value>`*  
*When* the ++`<ConceptA>`++ *`<value>`* `<triggering action>`  
    using ++`<ConceptB>`++ *`<value>`*  
*Then* the ++`<observed concept>`++ is `<observable outcome>`  
  *And* the ++`<related concept>`++ is `<additional outcome>`  
  *But* no ++`<concept>`++ is `<what does not happen>`

#### Scenario 2: `<alternate outcome-oriented scenario name>`

*Given* `<alternate setup state>`  
*When* `<alternate triggering action>`  
*Then* `<alternate observable outcome>`  
  *And* `<additional outcome>`

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
# ## Artifact layout (`artifacts-mirror-story-hierarchy`)
#
# Mirror Epic → SubEpic → Story on disk:
#
# ```
# tests/
#   {epic-verb-noun}/                    # kebab-case folder
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story-kebab-slug}.py            # one GWT file per story — no {story}/ folder
#
# # Machinery — copy once per tests/ tree if missing (do not inline in skills):
#   context_tools/stories/templates/py/story_test.py → tests/story_test.py
# ```
#
# ## Path naming (`kebab-case-paths`)
#
# Epic and SubEpic **folders**, story **file** stems, and tier segments: lowercase kebab-case
# (`sign-up`, `front-end`). No `snake_case` folders or `PascalCase` paths.
# **Exception:** Python epic helper only — `{epic_slug}_helper.py` at the epic folder root.
#
# ## Outcome chaining (`then-and-chaining`)
#
# First outcome: `then(...)`. Every later outcome on the same interaction: `.and_(...)`.
# Do not repeat `then()` for the same When. Markdown *And* stays *And*.
#
# ## Lifecycle hooks (`infrastructure-in-lifecycle-hooks`)
#
# Browser boot, app wiring, and `initialize` live in `before.all` / `after.all` — not in `given()`.
#
# ## Assertion helpers (`extract-assertion-helper`)
#
# The same assertion shape more than twice → named helper that takes a data bag; call sites pass values only.
#
# ## Example fixtures (`shared-example-fixtures`)
#
# Named domain fixtures live under `examples/` at the lowest **shared** folder:
#   `{epic}/examples/` — seeds shared across the epic
#   `{epic}/{sub-epic}/examples/` — catalog / givens shared by stories in the sub-epic
#   `{epic}/{sub-epic}/{story}/examples/` — fixtures unique to this story
# One file per domain concept (`account-credentials.examples.py`). Import in the story file;
# never repeat literals across scenarios. Golden layout: `context_tools/stories/examples/telco-website/`.
#
# from .examples.account_credentials_examples import valid_account_credentials
#
# Pattern: GWT structure only — replace pass with real code under each with.

from __future__ import annotations

from mamba import after, before

from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        pass  # infrastructure — boot / wiring (not domain Given)

    with after.all:
        pass  # infrastructure — teardown

    with background.each:
        with given("{background given step}"):
            pass  # domain state only

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with then("{observable surface outcome}"):
                pass  # test code goes here

            with and_("{further outcome on same interaction}"):
                pass  # chain with and_, not a second then()

        with scenario("{validation branch while typing}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with and_("{follow-on when step}"):
                pass  # test code goes here

            with then("{validation message on domain object}"):
                pass  # test code goes here

        with scenario("{validation clears when input conforms}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with and_("{prior invalid state}"):
                pass  # test code goes here

            with when("{corrective action}"):
                pass  # test code goes here

            with then("{error cleared on domain object}"):
                pass  # test code goes here

        with scenario("{main-flow outcome}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with when("{submit operation on domain object}"):
                pass  # test code goes here

            with then("{post-condition on loaded aggregate}"):
                pass  # test code goes here

See examples in `context_tools/stories/examples/` if needed.