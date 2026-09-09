---
name: stories-acceptance-tests
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-acceptance_tests

Use stories guidance at `acceptance_tests` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-scenarios
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

## acceptance_tests

**Default format:** project language

**Produce:** Runnable acceptance specifications and the production code that makes them pass.

**Goal:** Turn agreed Scenarios into executable evidence and working production behavior. For greenfield work, begin with a failing test that calls the intended production interface. For brownfield capture, first preserve observed behaviour and mark intended changes explicitly.

### Guidance

Apply `@stories` `#scenarios` § Guidance and § Rules to acceptance tests. Use the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/`: start with the real application when it is available, use deterministic external-system stubs while developing, and replace them with end-to-end boundaries when requested.

**Develop the behaviour, not only the test.** Acceptance-test work owns both the executable specification and the production code that satisfies it. Take one Scenario at a time: write the failing acceptance test, invoke the Clean Engineering companion at `code` fidelity, implement the smallest production change that can pass, rerun the test, refactor when it is green, and then continue to the next behaviour. After two failed fix attempts, diagnose the failure before changing more code.

Refer to [`../language-tools.md`](../language-tools.md) for language-specific test tools and idioms.

### Rules

- **`examples-trace-domain-model`** - Shape every fixture from the domain model and its owning system. Use the external system's record shape at that boundary and the product's aggregate shape inside the domain, because convenient mixed objects conceal mapping errors.
- **`examples-declare-seed-vs-interaction`** - Identify each fixture as **Seed** state owned by a system or **Interaction** data entered, displayed, or validated through the product. Use both when the Story needs both, because persisted records and user-facing data often represent the same concept differently.
- **`shared-example-fixtures`** - Represent each named example as one reusable code fixture for its domain concept, because acceptance data must remain aligned with the Scenario instead of drifting through copied values.
- **`seed-state-at-its-real-owner`** - Seed and inspect state through the component that owns it in the production architecture. When a rich domain layer integrates with an external system, seed the external test adapter and exercise production behaviour through the aggregates and repositories above it. When the repository is itself the storage boundary and no separate system exists, direct repository setup and loading are appropriate, because tests should reflect the architecture rather than create an extra layer.
- **`separate-test-controls-from-production-contracts`** - Keep seed, reset, and inspection operations off the production repository or adapter contract. Add them to a testable extension, test adapter, or stub when acceptance setup needs them, because test control is useful without becoming a production domain capability.
- **`system-stubs-domain-real`** - Before creating an external-system stub, inspect the real integration contract again and identify the boundary that production code calls. Make the stub reproduce that boundary's operations, request and response structures, identifiers, state changes, and failure behaviour; do not invent a simpler test API. Keep domain aggregates, repositories, validation, mapping, and state transitions real, because an inaccurate stub, silent no-op, or test-only domain operation can make a test pass without implementing production behaviour.
- **`assert-domain-behavior-not-seeded-state`** - Exercise the product's domain entry point after seeding its underlying state owner and assert the product result. Inspect that owner for stored data or outbound effects only after the product initiated them, because reading back data inserted during Given proves only that the fixture was stored.
- **`infrastructure-in-lifecycle-hooks`** - Put browser startup, application wiring, and shutdown in lifecycle hooks; keep Given for domain state. Load an aggregate once at the highest Given that needs it and reach owned entities through their aggregate root, because infrastructure and shortcut lookups obscure the behaviour's real state.
- **`inline-simple-gwt-bodies`** - Keep simple Given, When, and Then bodies inline and use example exports directly. Extract a helper only for non-trivial setup or repeated behaviour, because pass-through helpers add names without adding meaning.
- **`extract-assertion-helper`** - Extract the same assertion shape after it appears more than twice and pass its concrete values as data, because copied assertions become inconsistent when behaviour changes.

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