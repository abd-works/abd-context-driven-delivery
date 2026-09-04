Run the action on cdd at discovery fidelity through the tools cli

Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd.
Call guidance on each stage child and pass that child to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

Provide guidance from contexts, examples, and templates.

# Contexts

## Stages (CDD fidelity)

| Fidelity | Intent | Default run scope |
|---|---|---|
| **discovery** | Whole-solution shape | Entire solution, or a large subsection |
| **explore** | Current increment | Increment, or a large subsection of it |
| **spec** | Narrow, concrete | ~sub-epic inside solution / increment |
| **engineer** | Working software | ~sub-epic inside solution / increment |

Grill and sketch work **much finer** inside that scope. Do not invent detail from a deeper stage.

### Stage → child fidelities

| CDD | stories | ddd | ux | clean_engineering | bdd |
|---|---|---|---|---|---|
| **discovery** | discovery | bounded_context | ia | modules | — |
| **explore** | exploration | building_blocks | mockup | model | **behavior** |
| **spec** | exploration | tactics | mockup | code | **development** |
| **engineer** | engineering | tactics | — | code | **development** |

UX has no engineering fidelity — production UI follows stories + clean_engineering at **engineer**, honouring the UX spec from **spec**.

### Sketch (one file)

Path: `{session.folder}/cdd-sketch.md` (see `templates/cdd-sketch.md`).

- **One file per engagement** — deepening fidelity (discovery → explore → spec → engineer) updates `fidelity:` at the top and deepens blocks in place. Never create a new file for a new fidelity.
- **Themes** — group lens blocks under one theme (epic, module, user goal, increment, or sub-epic).
- **`order-themes-by-journey`** — When the theme **is** the customer journey / epic, list themes in story-map experience order (Onboarding before Selfcare). Do not follow UX IA / sitemap order.
- **Beside each other** — lens blocks under a theme stay close and comparable; not separate files.
- **Flow** — after each chunk: more at this stage, or proceed. Recommend proceed only when views agree.
- **Trail** — `TODO` → `doing` → `pass #label` (or `skip #why`). Move passes to `## log` as `stage / scope / theme / …`.

### Rules

- **`stage-from-context`** — Infer CDD fidelity from workspace artifacts, sketch, and user intent; confirm when ambiguous.
- **`cdd-owns-grill-sketch`** — Grill and sketch at CDD level. When following a child `tools run`, skip nested child grill/sketch; apply the child generate body only.
- **`views-agree-before-proceed`** — Recommend proceed only when the views in play for the current scope agree; otherwise more at the same stage. User can override.
- **`todo-trail-in-sketch`** — Persist actions as TODO/doing/pass #label in the sketch; archive passes under `## log`.
- **`scaffold-before-content`** — **Hard gate.** Do not write `cdd-sketch.md` (or a file called `sketch.md`) until you have (1) **read** `templates/cdd-sketch.md` and each active child's `sketch_template` from `resolve_targets`, and (2) **AskQuestion** has confirmed which lenses are in play (`confirm-lenses-before-sketch`). Free prose instead of the scaffold is a defect.
- **`order-themes-by-journey`** — When the theme is the customer journey / epic, order themes by the story map / customer experience (Onboarding before Selfcare), not by UX IA.

---

## .context/module-context.md

# Module: examples

**Purpose:** Illustrate CDD orchestrator usage — `resolve_targets` → `tools run`, stage menus, and one-file sketch shape with TODO trail.

**Primary use case:** Agents and humans read `examples.md` before guessing request YAML shape for CDD.

## Seam

Markdown examples only — no Python package surface.

## Public API

- `examples.md` (documentation)

## Dependencies

None


## connect-story-examples/.context/module-context.md

# Module: connect-story-examples

**Purpose:** Hold regeneratable story-map data that demonstrates connecting stories to example factories (interface / factory-mode extensions).

**Primary use case:** Clean engineering + stories generators read these story constants when emitting "Generate Type Extending Interface" scenarios at Fake / Isolated / Production **modes**.

**Rationale:** Story data is regeneratable and must not invent Fake/Isolated/Production subclasses — those are factory modes on `{Type}ExampleFactory`.

## Seam

`GENERATE_TYPE_EXTENDING_INTERFACE` constant — story metadata + three mode scenarios (fake / isolated / production).

## Public API

- `GENERATE_TYPE_EXTENDING_INTERFACE` (Final dict)

## Dependencies

None (data only). Pattern owned by clean_engineering + stories generators.


## connect-story-examples/connected-contexts.md

stage 2
    
   




Stories   import helper domain
epic folder             
    epic_common_file   < import common objects and helpers
sub epic file          < import objects and helpers
    story classes      < import  unique objects and helpers (rare)
        background
            examples
        scenarios
            examples
            steps      

stories <--

clean_engineering — factory generation PATTERN (framework), not an ExampleLoader type

PATTERN
# {family}.{ext} — production
I{Type}                         // public seam
{Type}                          // production — implements I{Type}

# {type}_example_factory.{ext} — ALWAYS separate
{Type}ExampleFactory
  {example_method}(mode)
    // loads examples[{example_key}] -> I{Type}, I{OtherType}, …
    // Fake | Isolated | Production are modes — not subclasses
// Fake:       mock/stub framework creates I{Type}; feed examples
// Isolated:   new {Type}(...ctor-injected mocks/stubs...)
// Production: new {Type}(...real collaborators...)
// examples[{example_key}] = multi-type bundle (NOT examples[{Type}][…])

EXAMPLE
# cart
ICart / Cart
IProduct / Product
# cart_example_factory
CartExampleFactory
  cart_with_items(mode)
    // examples[cart_with_items] -> ICart, IProduct


    UX (story demo — locked)
        Play: call story given/when/then (same functions that prove the story)
        Interactive: same UI; StoryDemoControl runs whenStep.fn via story_steps (helper.given* only inside When fn)
        Shell: StoryDemoFrame left + ExplorerFrame right (epic → story → scenario → steps)
        After each step: story owns domain; bind via bound_field; emphasize via story_steps
        Play seam: PlayDualRunner (UX story-demo/play-dual-runner) — collect/playNext; node describe/it wrapper
        World/paint: expose(() => ({ …domain variables })); no world bag
        ThenFeedback: peer to PaintReflect — soft-fail Then → message + tint
        UX Story Demo submodule: StoryDemoPage / StoryDemoFrame / ExplorerFrame / StoryDemoControl
          (vanilla Page/Control stay product UX)
        StoryDemoControl.bound_field: display; story_steps: emphasize (Play) + When fn (Interactive)
        Play: explorer Play next only — product controls not invoked

        Primary sketch: context_tools/ux/.context/story-runner-sketch.md
          (themes by user journey; ce → bdd → ux under each)
        Also: ux-context.md · ux-model-sketch.md
        Implemented: UX story-demo (shell + play-dual-runner); sandbox holds engagement HTML wire only




## connect-story-examples/story-map.md

---
fidelity: [discovery, specification]
artifact: [story-map]
format: md
section: body
---

<!-- Deliverable: extend clean_engineering + stories generators.
     Cart/Product appear only as pattern examples — not an app under construction. -->

# Story Map — Connect Story Examples

**Sources / context:** cdd-sketch.md, connected-context_tools.md, clean_engineering + stories generator packages

---

(E) Connect Story Examples
    (E) Generate Interface Extensions
        (S) Generator --> Generate Type Extending Interface
            // scenarios: Fake | Isolated | Production for any {Type}
            // owned by context_tools/clean_engineering instructions/templates
    (E) Generate Stories That Import Factories
        (S) Generator --> Generate Epic That Imports Factories
        (S) Generator --> Generate Sub-Epic That Imports Factories
        (S) Generator --> Generate Scenario Steps That Call Factory Methods
            // owned by context_tools/stories — factory links + objects used in scenarios
        (S) Generator --> Generate Story-Unique Imports
            // rare
    (E) Demonstrate Story Scenarios
        * approx 3-4 more stories (demo runner — later increment)

---

## Scope boundary

**In scope:** Extending `context_tools/clean_engineering` so generation builds Fake/Isolated/Production for `{Type}`; extending `context_tools/stories` so generation emits example-factory links and uses those objects in scenarios.
**Out of scope:** Building a pet-store/cart product; UX demo runner (later).

---

## Thin slices

### Increment 1: Generator extensions for factories + story imports

**Outcome:** CE generator can emit Fake/Isolated/Production; Stories generator can emit epic/sub-epic helpers and scenario steps that call factories (Fake at explore/spec).

**Stories:**
- Generate Type Extending Interface
- Generate Epic That Imports Factories
- Generate Sub-Epic That Imports Factories
- Generate Scenario Steps That Call Factory Methods


## connect-story-examples/thin-slice.md

---
fidelity: [discovery, specification]
artifact: [thin-slice]
format: md
section: body
---

# Thin slicing — Connect Story Examples

## Product / context

**Product:** CDD generators — `clean_engineering` + `stories` (not a retail/cart app)

**Slicing intent:** Ship generator instructions/templates that emit Fake/Isolated/Production and story artifacts that link factories into scenarios. Pattern examples (Cart/Product) illustrate only.

**Spine vs optional:** CE Fake/Isolated/Production emission + Stories factory links/scenario use on the spine. Demo runner later.

## Increments

### Increment 1: Extend CE + Stories generators

**Outcome:** clean_engineering builds Fake/Isolated/Production for any `{Type}`; stories generates epic/sub-epic helpers and scenario steps that import factories and use returned objects (Fake at explore/spec; Isolated/Production per test tier).

**Stories in this increment:**

- *Generate Type Extending Interface*
- *Generate Epic That Imports Factories*
- *Generate Sub-Epic That Imports Factories*
- *Generate Scenario Steps That Call Factory Methods*

### Increment 2: Demonstrate story scenarios (later)

**Stories in this increment:**

- *approx 3-4 demo runner stories*


## example-factories/.context/module-context.md

# Module: example_factories

**Purpose:** Expose `{IType}`, production `{Type}`, and `{Type}ExampleFactory` seams so stories helpers can call factories. Fake / Isolated / Production are factory **modes**, not subclasses.

**Primary use case:** Explore/spec — scenario steps call a helper; helper calls `ICartExampleFactory.cart_with_items()`; factory returns fake `ICart` + `IProduct` (mock/stub framework + `examples[cart_with_items]`). Story-test tiers choose isolated (`Cart` + ctor-injected mocks) or production (`Cart` + real collaborators).

**Rationale:** Example data is keyed by `{example_key}` as a multi-type bundle (not `examples[{Type}][…]`). Factories are pattern-generated plain classes (no ExampleLoader base). Do not generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` classes.

## Seam

The seam is `IType` / `ICart` / `IProduct` / `ICartExampleFactory` — callers import factories and load named example methods; they do not invent domain objects in helpers.

Constraint: do not emit Fake/Isolated/Production subclasses of `I{Type}`. Build `I{Type}` via factory mode (fake = mock framework + examples; isolated = `{Type}` + ctor-injected mocks; production = `{Type}` + real collaborators). Bundles are multi-type by `{example_key}`.

## Public API

- `IType`
- `ICart`
- `IProduct`
- `ICartExampleFactory.cart_with_items(mode="fake") -> (ICart, IProduct)`

**Layout:** Pattern docs in this module; generated app code uses two files per type — `{family}.{ext}` (production) and `{type}_example_factory.{ext}` (factory + examples).

## Dependencies

None at modules fidelity (example data arrives with the generation pattern).

**Mechanism stereotype:** `{Type}ExampleFactory.{example_method}(mode)` → `examples[{example_key}]` → fake | isolated | production `I{Type}`


## example-factories/example-factories.md

<!-- @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source. -->
<!-- invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->

<!--
  clean_engineering model fidelity — Fake / Isolated / Production are factory modes, not subclasses.
  L = language companion (prose). Md = model (I{Type} seam). Production {Type} at specification+.
-->

# Example Factories                                                    <!-- L -->

---

## Language companion                                             <!-- L -->

The clean_engineering generator produces `{IType}`, production `{Type}`, and a pattern-generated `{Type}ExampleFactory` whose methods load multi-type example bundles. <!-- L -->
**Fake / Isolated / Production are modes** of how the factory builds `I{Type}` — not generated subclasses. <!-- L -->
There is no ExampleLoader framework type — load/fill is a generation pattern. <!-- L -->

### Module: example_factories                                      <!-- L -->

- Generates `{IType}` + `{Type}` in the production family file; `{Type}ExampleFactory` in a **sibling** `{type}_example_factory` file. <!-- L -->
- Does **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` classes. <!-- L -->
- Stories generator (separate) emits epics, scenarios, and steps that **import** these factories. <!-- L -->
- Seam: named factory methods return `I{Type}` filled from `examples[{example_key}]` bundles in a chosen mode. <!-- L -->
- **Constraint:** A bundle may include several types (e.g. cart and product), not one examples bag per type. Factories never sit in the production file. <!-- L -->

### IType                                                          <!-- L -->

- Public contract for a domain type. <!-- L -->
- Surface slots: constructor, public api, internals, dependencies. <!-- L -->

### Type (production)                                              <!-- L -->

- Production class implementing IType. <!-- L -->
- **Already works** — keep confirming; do not reinvent. <!-- L -->

### Modes (not types)                                              <!-- L -->

- **Fake** — mocking/stub framework creates `I{Type}`; feed `examples[{example_key}]`. <!-- L -->
- **Isolated** — `new {Type}(...ctor-injected mocks/stubs...)`. <!-- L -->
- **Production** — `new {Type}(...real collaborators...)`. <!-- L -->

### TypeExampleFactory                                             <!-- L -->

- Pattern-generated plain class (no base). <!-- L -->
- Methods load `examples[{example_key}]` and return `I{Type}` (+ peers) in fake / isolated / production mode. <!-- L -->

### CartExampleFactory                                             <!-- L -->

- Illustrative app factory (pattern example only — not a product deliverable). <!-- L -->
- **cart_with_items:** bundle ICart + IProduct; fake mode by default for stories. <!-- L -->

### ICart / Cart                                                   <!-- L -->

- Cart interface and production class; factory modes build ICart. <!-- L -->

### IProduct / Product                                             <!-- L -->

- Product interface and production class — often in the same example bundle as cart. <!-- L -->


## examples.md

# CDD examples

## resolve_targets → tools run

```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: explore
tool: resolve_targets
```

One row (example):

```yaml
context: ddd
fidelity: building_blocks
run:
  toolset: context_tools.ddd.ddd:Ddd
  context:
    fidelity: building_blocks
  action: generate
  arguments:
    plan: CDD explore → ddd@building_blocks
    slug: ddd
```

Pipe `run` to `python -m tools run -`. Mark sketch `doing #ddd` → `pass #ddd`.

## BDD after clean_engineering (explore+)

`resolve_targets(fidelity="explore")` includes bdd at `behavior` after clean_engineering.  
`spec` / `engineer` use `development`. Discovery has no bdd.

## One sketch — theme, flow, TODO trail

Lens bodies use **child generator notation** (from `resolve_targets[].sketch_template`), not prose.

```
fidelity: explore
scope: Increment 1 — place order

flow:
  status: in-progress
  recommend: more-same-stage
  next: explore
  note: screens and stories still disagree on when delivery is chosen
  open:
    - TODO delivery picker layout  #theme-place-order
  done:
    - pass #ddd

=========
theme: Place New Order  (sub-epic)
---------
stories:
    Manage Customer Orders
        Place New Order
            Customer --> Select Delivery Option
                select delivery shows available options
                    given an Order with Cart.items
                    when the Customer selects a Delivery Option
                    then Order.deliveryOption is set
            Customer --> Submit Order
            * approx 2-3 more stories (address, review)
---
ddd:
    Ordering
      aggregates: Order, DeliveryOption
    pass #ddd
---
ux:
    checkout
      └─ [action] choose delivery → delivery picker
    [ delivery picker ]                              form
      ┌─────────────────────────────┐
      │ option · fee · arrival      │
      │ [ Continue ]                │
      └─────────────────────────────┘
---
ce:
    OrderService
      place_order cart payment
      select_delivery order option
=========

## log
- explore / Increment 1 / Place New Order / pass #ddd
```


Separate tools run — toolset: `context_tools.stories.stories:Stories` action: `guidance` context.fidelity: `story_map`

Separate tools run — toolset: `context_tools.ddd.ddd:Ddd` action: `guidance` context.fidelity: `bounded_context`

Separate tools run — toolset: `context_tools.ux.ux:Ux` action: `guidance` context.fidelity: `ia`

Separate tools run — toolset: `context_tools.clean_engineering.clean_engineering:CleanEngineering` action: `guidance` context.fidelity: `modules`

Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: discovery
tool: <tool name>
arguments:
  <if needed>
```

Run: python -m tools run -

Before following the suggested flow, display the tools made available to this chat in your user-visible reply — each tool name and what it is for. Do not only follow them silently or rediscover them by remanifesting.

Tools made available:
- guidance

Suggested flow (repeat and reorder as the story needs):

1. tool: guidance

2. tool: guidance

3. tool: guidance

4. tool: guidance

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: discovery
action: generate
```
.\tools.ps1 run -
