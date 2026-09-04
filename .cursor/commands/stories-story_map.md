Run the action on stories at story_map fidelity through the tools cli

Provide guidance for creating story maps, scenarios, and acceptance tests.
At scaffold fidelity: write epic, sub-epic, and story names only.
At story_map fidelity: write the story map and thin-slice only.
At scenarios fidelity: write main-flow scenarios (single or multiple per story) with optional variations; fixtures live in examples/ and givens.ts at the lowest shared epic/sub-epic/story folder.
At acceptance_tests fidelity: write tests/{epic}/{sub-epic}/{story}.{tier}.ts (one GWT file per story per seam, no story folder). When those files are written, call guidance on the CE companion and pass that companion to this action as a separate tools run so wrap classes under domain/ stay in sync.
If the same acceptance scenario is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (tier wiring, stale Story constant, vocabulary drift, or transform that fixed the map while the leaf still fails).
When this Stories work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

Provide guidance from contexts, examples, and templates.

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

## manage-customer-orders/md/story-map.md

---
fidelity: [shaping, discovery]
artifact: [story-map]
format: md
example-of: story-map
---

# Story Mapping — Example

## Example story map

(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
        (S) Customer --> Add Item To Cart
        (S) Customer --> Enter Shipping Address
        (S) Customer --> Select Delivery Option
        (S) Customer --> Submit Order
    (E) Track Order Status
        (S) Customer --> View Current Order Status
        (S) System --> Send Shipment Notification
    (E) Cancel Order
        (S) Customer --> Request Order Cancellation
        (S) System --> Process Cancellation Refund

## What to notice

- Epic names are **verb–noun**, no actor in the name
- Actor goes before `-->`, not in the story name
- Each story is one observable behavior — not a task or feature
- Sub-epics group stories into coherent flows


## manage-customer-orders/md/thin-slice.md

---
fidelity: [discovery]
artifact: [thin-slice]
format: md
example-of: thin-slice
---

# Thin slicing — PawPlace incremental backlog

## Product / context

**Product:** PawPlace — online pet store with in-store adoption visits.

**Slicing intent (by value, store-first):** Each increment must put a working capability in the hands of a real store. Earlier increments deliberately leave out polish, payment depth, accounts, pets, returns, and marketing so that a store gets a usable product on day one and revenue and learning compound with each release. *Pet appointments* — the adoption side — are explicitly held back until the e-commerce spine is real.

**Spine vs optional:** The mandatory commerce spine is **catalog → store → cart → pay → fulfill**. Pets, accounts, multi-vendor payments, returns, marketing, reviews, and admin polish are real work but **not** required for the smallest store-supporting slice; they ride later increments.

## Increments

### Increment 1: `Walk-in driver — find the store, see what's in stock`

**Outcome:** A customer can find their nearest *store*, browse the *product catalog*, see *real-time stock availability* for a product at that store, and walk in to ask for it. Drives foot traffic with zero checkout, payment, or accounts infrastructure. Store gets value on day one.

**Slicing notes:** Single payment-free, account-free vertical slice. Manual stock updates by staff via a bare-bones admin form. Categories only — no keyword search yet. No cart, no checkout, no notifications. Validates the *catalog* data model, the *store* + geo model, the *stock availability* contract, and that customers find this useful enough to walk in. Risk validated: real customer traffic to real stores.

**Stories in this increment** *(order reflects flow within the slice):*

- *View Store Map*
- *View Store List*
- *Calculate Distance to Store*
- *View Product Details*
- *Display Real-Time Stock Availability*
- *Update Product Stock Levels*

### Increment 2: `Click-and-collect — buy online, pick up at the store`

**Outcome:** A customer can put products in a *shopping cart*, pay online with a card, and pick the order up at a chosen *store*. The store gets online revenue without anyone solving home-delivery logistics. Single payment vendor (StripeWave) so the integration is real but bounded.

**Slicing notes:** *Guest checkout* only — no accounts yet. Single payment vendor. Confirmation email from a static template. No shipping address, no delivery option fan-out — pickup is the only fulfillment path. Manual pick-prep by store staff. Validates the riskiest payment integration on a real card-present journey end-to-end.

**Stories in this increment:**

- *Add Product to Cart*
- *Update Cart Quantity*
- *Remove Product from Cart*
- *Select Click-and-Collect Store*
- *Check Out as Guest*
- *Enter Billing Address*
- *Select Payment Method*
- *Process Card Payment via StripeWave*
- *Confirm Order and Send Confirmation Email*
- *Prepare Click-and-Collect Orders for Pickup*
- *Fulfill Click-and-Collect Order*

### Increment 3: `Ship to home — full standard-delivery e-commerce`

**Outcome:** A customer can complete the same purchase journey but have it **shipped** to a delivery address. Standard delivery only. Now the store reaches customers outside its catchment.

**Slicing notes:** Still *guest checkout*, still StripeWave-only. Standard delivery only — defer express and same-day. Manual shipping label creation by staff. Validates the order lifecycle past pickup: shipping notifications, tracking, and an order-status view.

**Stories in this increment:**

- *Enter Shipping Address*
- *Select Delivery Option*
- *View and Process Incoming Orders*
- *Send Shipping Notification with Tracking Number*
- *Track Order Status*


## story-context.md

---
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: [story-map]
---

# `<Epic / Sub-Epic Verb–Noun>`

**Status:** `<not yet expanded | partially expanded | fully expanded>`

**Stories in scope:**
- *`<Story Verb–Noun>`*
- *`<Story Verb–Noun>`*

**Context / notes:** `<anything the folder structure cannot express — domain constraints, dependencies, open questions>`


## story-map.md

---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories.
     Shaping outline maps use templates/md/story-map-outline.md instead.
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


Separate tools run — toolset: `context_tools.clean_engineering.clean_engineering:CleanEngineering` action: `guidance` context.fidelity: `code`

Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.stories.stories:Stories
context:
  fidelity: story_map
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

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.stories.stories:Stories
context:
  fidelity: story_map
action: generate
```
.\tools.ps1 run -
