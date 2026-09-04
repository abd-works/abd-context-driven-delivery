Run the action on stories at scaffold fidelity through the tools cli

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

## acceptance_tests

**Default format:** typescript

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Produce:** `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam. `{tier}` is `front-end`, `back-end`, or any other system name you are proving. No `{story}/` folder and no `*_story` / `*_test_helper` split. Fixtures live in `examples/` and `givens.ts` at the lowest shared epic / sub-epic / story folder.

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

## manage-customer-orders/md/scenario-inline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
example-of: scenario-inline
---

<!-- Worked example — plain scenario with real domain values inline. -->
<!-- Shows the shape templates/md/scenario-inline.md produces once filled in. -->

## Story: Apply For a Payment Product Agreement

**Story type:** user

### Domain terms

- *Customer* — account holder applying for the agreement
- *DDA Account* — demand deposit account; must be valid and eligible
- *Payment Product Agreement* — contract under review after submission
- *Owner* — named responsible party on the agreement
- *Contact Details* — email or phone used to notify the **Owner**

## Behaviors

### Scenario 1: Agreement submitted with valid DDA Account and Owner

*Given* a **Customer** *Jane Doe* exists  
  *And* that **Customer** *Jane Doe* has a valid **DDA Account** *DDA-001*  
*When* the **Customer** *Jane Doe* applies for a **Payment Product Agreement**  
    using **DDA Account** *DDA-001*  
    with **Owner** *John Doe*  
      that has **Contact Details** *john@acme.com*  
*Then* the **Payment Product Agreement** is submitted for review  
  *And* the **Owner** *John Doe* is notified at *john@acme.com*  

### Scenario 2: Agreement rejected when DDA Account is invalid

*Given* a **Customer** *Jane Doe* exists  
  *And* that **Customer** *Jane Doe* has **DDA Account** *DDA-999* with status *Invalid*  
*When* the **Customer** *Jane Doe* applies for a **Payment Product Agreement**  
    using **DDA Account** *DDA-999*  
*Then* the **Payment Product Agreement** is *rejected*  
  *And* **Customer** *Jane Doe* is notified that the **DDA Account** is *not eligible*  

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | *Payment Product Requirements* | §"Application flow", p. 12 |
| Scenario 2 | *Payment Product Requirements* | §"Rejection cases", p. 14 |


## manage-customer-orders/md/scenario-main-flow.md

---
fidelity: [exploration]
artifact: [story-scenarios]
format: md
example-of: scenario-main-flow
---

# Acceptance Criteria — Example

Worked example using the same **Manage Customer Orders** domain as the shaping-level story-map-example.md.

Below is one story in full so agents can read a single complete pattern.

---

## Story: Browse Product Catalog

**Story type:** user

### Domain terms

- *Product Catalog* — browsable list of products available to order
- *Category* — grouping used to narrow what the customer sees
- *Product Detail* — name, description, price, and image for one product
- *Out Of Stock* — product not available to add to an order right now

### Acceptance criteria

1. **WHEN** the customer opens the *Product Catalog*
   **THEN** the system displays available products grouped by *Category*
   **AND** each row shows at least product name and price
   **Evidence:** Order Management Workshop — whiteboard "Place order" flow, 2026-03-15, sticky "browse by category"

2. **WHEN** the customer selects a *Category*
   **THEN** the *Product Catalog* lists only products in that *Category*
   **Evidence:** Order Management Workshop — same session, "filter catalog by category"

3. **WHEN** the customer selects a product from the *Product Catalog*
   **THEN** the system shows *Product Detail* for that product
   **Evidence:** Order Management Workshop — "click through to product detail"

4. **WHEN** a product is *Out Of Stock*
   **THEN** the *Product Catalog* and *Product Detail* show that the product cannot be added to an order
   **BUT** the customer can still browse other products
   **Evidence:** Order Management Workshop — "don't block browsing when one SKU is gone"

## What to notice

- Stories match **verb-noun** names from the story map; actor is in **Story type**, not the title
- **Domain terms** are defined before AC; the same *italic* terms appear in the criteria
- **when / then / and / but** — negatives use **but**; no **given** in AC
- Each AC is a **delta** or distinct case — general browse flow once, then category, detail, and out-of-stock paths
- **Evidence** cites a concrete source even for workshop-derived discovery

---

## Same story in `*-stories.ts` code format

```typescript
import type { Step, AcceptanceCriterion, Background } from '../../story-types'

export const BROWSE_PRODUCT_CATALOG = {
  story: `Browse Product Catalog`,
  actor: `Customer`,

  acceptance_criteria: [
    [
      { when: `the *customer* opens the **Product Catalog**` },
      { then: `the system displays available products grouped by **Category**` },
      { and:  `each row shows at least product name and price` },
    ],
    [
      { when: `the *customer* selects a **Category**` },
      { then: `the **Product Catalog** lists only products in that **Category**` },
    ],
    [
      { when: `the *customer* selects a product from the **Product Catalog**` },
      { then: `the system shows **Product Detail** for that product` },
    ],
    [
      { when: `a product is **Out Of Stock**` },
      { then: `the **Product Catalog** and **Product Detail** show the product cannot be added` },
      { but:  `the *customer* can still browse other products` },
    ],
  ] as const satisfies readonly AcceptanceCriterion[],

  domain_terms: ['Product Catalog', 'Category', 'Product Detail', 'Out Of Stock'] as const,
  evidence: [
    'Order Management Workshop — whiteboard "Place order" flow, 2026-03-15',
    'Order Management Workshop — "filter catalog by category"',
    'Order Management Workshop — "click through to product detail"',
    'Order Management Workshop — "don\'t block browsing when one SKU is gone"',
  ] as const,

  customerOpensProductCatalogSystemDisplays: {
    name: `customer opens product catalog system displays`,
    steps: [
      { when: `the *customer* opens the **Product Catalog**` },
      { then: `the system displays available products grouped by **Category**` },
      { and:  `each row shows at least product name and price` },
    ] as const satisfies readonly Step[],
  },

  customerSelectsCategoryProductCatalogLists: {
    name: `customer selects category product catalog lists`,
    steps: [
      { when: `the *customer* selects a **Category**` },
      { then: `the **Product Catalog** lists only products in that **Category**` },
    ] as const satisfies readonly Step[],
  },

  customerSelectsProductProductDetail: {
    name: `customer selects product product detail`,
    steps: [
      { when: `the *customer* selects a product from the **Product Catalog**` },
      { then: `the system shows **Product Detail** for that product` },
    ] as const satisfies readonly Step[],
  },

  productOutOfStockProductCatalogShows: {
    name: `product out of stock product catalog shows`,
    steps: [
      { when: `a product is **Out Of Stock**` },
      { then: `the **Product Catalog** and **Product Detail** show the product cannot be added` },
      { but:  `the *customer* can still browse other products` },
    ] as const satisfies readonly Step[],
  },

} as const
```

The `acceptance_criteria` array and the named scenario objects contain **identical steps** — the criteria drive what the scenarios test.


## manage-customer-orders/md/scenario-outline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
example-of: scenario-outline
---

<!-- Worked example — Scenario Outline with normalized Examples tables. -->
<!-- Shows the shape templates/md/scenario-outline.md produces once filled in. -->

## Story: Submit Payment and Validate Against Account Limit

**Story type:** user

### Domain terms

- ++Account++ — enterprise sub-account with an activation status
- ++Transactional Limit++ — maximum amount rule attached to an ++Account++
- ++Wire Payment++ — payment request submitted by the user
- ++Payment Amount++ — value entered for the ++Wire Payment++
- ++Validation Status++ — outcome after limit check (*successful* or *rejected*)

### Examples

#### ++Account++:

| scenario      | enterprise_name | account_name       | activation_status |
|---------------|-----------------|--------------------|-------------------|
| ++Scenario 1++    | Acme Corp       | Acme Operating     | Active            |
| ++Scenario 2++    | Acme Corp       | Acme Payroll       | Active            |

#### ++Transactional Limit++:

| scenario      | account_name       | limit_name  | max_amount   | currency |
|---------------|--------------------|-------------|--------------|----------|
| ++Scenario 1++    | Acme Operating     | daily_wire  | 500000.00    | USD      |
| ++Scenario 2++    | Acme Payroll       | weekly_wire | 2000000.00   | USD      |

#### ++Wire Payment++:

| scenario      | amount      | currency | formatted_display | validation_status |
|---------------|-------------|----------|-------------------|-------------------|
| ++Scenario 1++    | 10000.00    | USD      | $10,000.00        | successful        |
| ++Scenario 2++    | 500000.01   | USD      | $500,000.01       | rejected          |

### Background

*Given* a ++User++ {user_name} is logged into ChannelOne 2.0  
  *And* that ++User++ {user_name} is representing ++Enterprise++ {enterprise_name}  

### Behaviors

#### Scenario Outline 1: Submit Payment and Validate Against Account Limit

#### Steps

*Given* an ++Account++ {account_name} with ++Activation Status++ {activation_status}  
  *And* the ++Transactional Limit++ for that ++Account++ is {max_amount} {currency}  
*When* the ++User++ enters a ++Payment Amount++ of {amount} {currency}  
*Then* the ++Wire Payment++ is marked as {validation_status}  
  *And* a ++Report++ is sent with formatted display {formatted_display}  

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | *Order Management Workshop* | Whiteboard "submit flow", 2026-03-15 |
| Scenario 2 | *API Spec* v2 | p. 8, §"Limit exceeded" |


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
  fidelity: scaffold
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
  fidelity: scaffold
action: generate
```
.\tools.ps1 run -
