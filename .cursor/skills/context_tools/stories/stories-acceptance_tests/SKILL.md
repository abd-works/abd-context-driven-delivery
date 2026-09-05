---
name: stories-acceptance_tests
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-acceptance_tests

Use stories guidance at `acceptance_tests` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-scenarios
@stories-story_map

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map |
| **scenarios** | python | Main-flow scenarios per story — `{story}.{tier}.py` GWT files. Pass `format markdown` only when the strategy asks for a markdown view. |
| **acceptance_tests** | python | Same `{story}.{tier}.py` tree as scenarios. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.py` files (no per-story directory).
- **`kebab-case-paths`** — Epic and SubEpic **folder** names, story **file** stems, and tier segments use lowercase kebab-case (`sign-up`, `front-end`). No `snake_case` folders or `PascalCase` paths. **Exception:** Python epic helper only — `{epic_slug}_helper.py` at the epic folder root; nothing else may use underscores.
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## acceptance_tests

**Default format:** python

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.{tier}.py` — one GWT file per story per seam. `{tier}` is `front-end`, `back-end`, or any other system name you are proving. No `{story}/` folder and no `*_story` / `*_test_helper` split.

### Rules

- **`behavioral-observable-outcomes`** — same rule as **scenarios**: assertions stay in domain-observable terms, never internals.
- **`explore-full-interaction-surface`** — same rule as **scenarios**: acceptance_tests must cover the explored interaction surface, not just translate the first main-flow scenario into Playwright. Trace react-hook-form rules, shared validation components, and stubbed failure modes during the sandbox walk-through; add a `scenario()` per distinct behavior.
- **`gwt-steps-trace-to-domain-operations`** — same rule as **scenarios**: each step in the test traces to a named domain operation or property. A hop to the next step is a named operation on the arriving aggregate, not a route or `waitForCompletion()`.
- **`reconcile-live-immediately`** — same rule as **scenarios**: live disagreement updates the sketch before the test is locked.
- **`explain-deep-link-arrival`** — same rule as **scenarios**.
- **`given-only-what-the-system-checks`** — same rule as **scenarios**.
- **`when-holds-the-operation`** — same rule as **scenarios**.
- **`then-and-chaining`** — same rule as **scenarios**.
- **`extract-assertion-helper`** — same rule as **scenarios**.
- **`infrastructure-in-lifecycle-hooks`** — same rule as **scenarios**.
- **`load-with-identity-in-hand`** — same rule as **scenarios**.
- **`seed-prior-story-as-given`** — same rule as **scenarios**.
- **`reuse-owning-aggregate-stubs`** — same rule as **scenarios**.

---

## Sketching

When sketching, use the following sketch template. Do not use the produce templates below — stop reading this skill when sketching.

# Stories sketch — match active fidelity

**MUST:** Read all source context in full before drafting or refining. **MUST:** Branch on **mechanical uniqueness** only — split distinct mechanics; do not mint one story per TOC / catalog / requirements row. **MUST:** Do not invent requirements — no Status/stale/warning-badge stories or columns unless source already requires them; no second command/invoke surface beside one already specified (no co-equal YAML Invoke block next to a locked `/{skill} <action> {fidelity}` line — secondary formats are a subsidiary link only). Unconfigured = no row + existing fallback. See `stories.md`: `read-all-source-context-in-full`, `branch-on-mechanical-uniqueness`, `do-not-invent-requirements`.

Sketch the story hierarchy first, then deepen only as far as the active fidelity needs. Confirm epics and sub-epics (the e2e journey), then drill into exact stories by risk or uncertainty — unique **mechanical** flows first, then scaffold patterns already encountered.

Sketch increments next if there will be more than one.

Then detail groups of related stories together — e.g. stories for a sub-epic in a particular increment. Narrate in e2e flow order.

When detailing stories, start with the main-flow scenario (including domain objects usable for examples); then other scenarios, real example data, etc. Given names only conditions the running system actually checks. When is the domain operation. Then asserts; further outcomes are `And` / `.and()`.

**Unmapped areas** live here as `* approx N–M stories…` lines — not in a separate outline map. Discovery materializes named stories; drop approx lines once those stories are named on the real map.

**Order:** epics → sub-epics → confirming stories + approx gaps → thin-slice order → main-flow scenario → variations / shared setup (`specification`) → tier notes (`engineering` only).

Do **not** tag lines with fidelity markers. Depth is what you fill:

| Fidelity | Fill |
|---|---|
| **discovery** | Epic / SubEpic / named stories + thin-slice; clear approx gaps as you name stories |
| **exploration** | Main-flow Given / When / Then under each confirming story; objects from ExampleFactory fakes; assert public interface. No shared background yet. |
| **specification** | Extra scenarios, shared setup / background; still fake + public interface; values from factories |
| **engineering** | Which tier(s) (`domain` / `client` / `server` / `e2e` / project-specific); not full impl in the sketch |

**Notation:** indent = nesting · `{Actor} --> {Verb Noun}` story · `* approx N–M …` unmapped · `~>` increment · `//` note.

---

## Template

```
{Epic verb-noun}
    * approx N–M total stories
    {Sub-epic verb-noun}
        {Actor} --> {Confirming story verb-noun}
            given {shared setup}                    // specification only
            {main scenario name}
                given {precondition the running system actually checks}
                    and {precondition with object.object.field}
                    and …
                when {the domain operation}
                    and …
                then {observable outcome {object.field=descriptive term}}
                    and {next observable outcome}
            {next scenario name}                    // specification only
                …
        {Actor} --> {Confirming story verb-noun}
        * approx N–M more stories (what unmapped work likely includes)
    {Sub-epic verb-noun}
        * approx N–M more stories (what unmapped work likely includes)
~> Increment 1: {capability outcome}: {Story verb-noun}, {Story verb-noun}, …
```

---

## Example

```
Manage Customer Orders
    * approx 18-22 total stories
    Place New Order
        Customer --> Browse Product Catalog
            browse catalog shows available products
                given a Catalog with published Products
                    and a Customer with an empty Cart
                when the Customer browses the Catalog
                then available Products are listed with price
                    and Product.name and Product.price are shown
        Customer --> Submit Order
            given a Cart with line items and a Payment Method   // specification only
            order accepted for valid cart and payment
                given a Cart with Items totalling amount.currency
                    and a Payment Method with status authorised
                when the Customer submits the Order
                then an Order is created with status placed
                    and an Order.number is returned
            order rejected when payment declined                // specification only
                given a Cart with Items totalling amount.currency
                    and a Payment Method with status declined
                when the Customer submits the Order
                then the Order is rejected with reason payment_declined
                    and the Cart contents are preserved
        * approx 4-5 more stories (cart, address, delivery, review)
    Track Order Status
        * approx 3-4 more stories (pending, shipped, delivered)
    Cancel Order
        Customer --> Request Order Cancellation
        * approx 2-3 more stories (refund, partial cancel, policy)
~> Increment 1: Customer can place a paid order: Browse Product Catalog, Submit Order
```

## Templates

### markdown

## scenario-template.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

<!-- Default: Scenario Outline + Examples table. Alternate: inline sibling scenarios below. -->

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
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story_snake_slug}.{tier}.py     # one GWT file per story per tier
#
# # Machinery — copy once per tests/ tree if missing (do not inline in skills):
#   context_tools/stories/templates/py/story_test.py → tests/story_test.py
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: GWT structure only — replace pass with real code under each with.

from __future__ import annotations

from mamba import after, before

from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        pass  # boot — test code goes here

    with after.all:
        pass  # teardown — test code goes here

    with background.each:
        with given("{background given step}"):
            pass  # test code goes here

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with then("{observable surface outcome}"):
                pass  # test code goes here

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