Run the action on stories at acceptance_tests fidelity through the tools cli

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

## manage-customer-orders/examples.md

# Stories examples

Reference trees under this folder. Prefer generating fresh trees via
`Stories.transform` / `generate` at the active fidelity rather than copying
these verbatim when the hybrid layout differs.

## Markdown (`md/`) — discovery documents

| Path | What it shows |
|---|---|
| `md/story-map.md` | Discovery story map (verb–noun + actor before `-->`) |
| `md/thin-slice.md` | Vertical increments referencing map story names |
| `md/scenario-main-flow.md` | Main-flow scenario narrative |
| `md/scenario-outline.md` | Scenario outline + examples table |
| `md/scenario-inline.md` | Inline-examples scenario style |

## Python (`py/`) — exploration / specification / engineering layout

| Path | What it shows |
|---|---|
| `py/manage-customer-orders/` | Acceptance layout for one epic (story-spec leaf files + shared runner/types) |
| `py/manage-customer-orders/*/*/*_stories.py` | Regeneratable story-spec constants (`story`, `actor`, scenarios) |
| `py/manage-customer-orders/story_runner.py` | Runner that binds scenarios to tier implementations |
| `py/manage-customer-orders/story_types.py` | Shared story/scenario type shapes |

Prefer the hybrid leaf-file + tier shape from the code formatter over any legacy dict-only layout when they disagree.


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


## manage-customer-orders/py/manage-customer-orders/cancel-order/process-cancellation-refund/process_cancellation_refund_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


PROCESS_CANCELLATION_REFUND: Final = {
    "story":        "Process Cancellation Refund",
    "actor":        "System",
    "domain_terms": ("Cancellation", "Refund", "Refund Amount", "Payment Method"),
    "evidence":     (),
}


## manage-customer-orders/py/manage-customer-orders/cancel-order/request-order-cancellation/request_order_cancellation_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


REQUEST_ORDER_CANCELLATION: Final = {
    "story":        "Request Order Cancellation",
    "actor":        "Customer",
    "domain_terms": ("Order", "Cancellation Request", "Cancellation Reason", "Order Status"),
    "evidence":     ("Cancellation policy doc v2 #3", "Customer support call review 2026-05-18"),

    "cancellation_accepted_before_shipment": {
        "name":         "cancellation accepted while the order is still placed",
        "given": (
            "an Order \"ORD-4200080\" in status placed",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits a Cancellation Request with reason \"changed mind\"",
                ),
                "then": (
                    "the Order status changes to cancelled",
                    "And the Cancellation Request records reason \"changed mind\"",
                ),
            },
        ),
    },

    "cancellation_rejected_after_shipment": {
        "name":         "cancellation rejected once the shipment is on the way",
        "given": (
            "an Order \"ORD-4200081\" in status shipped",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits a Cancellation Request",
                ),
                "then": (
                    "the Cancellation Request is rejected",
                    "But the Order remains in status shipped",
                ),
            },
        ),
    },
}


## manage-customer-orders/py/manage-customer-orders/conftest.py

"""Test-root conftest - adds this folder to sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


## manage-customer-orders/py/manage-customer-orders/manage_customer_orders_helper.py

"""Epic-level helper for the Manage Customer Orders code examples.

Kept as a snake_case module because Python's import system does not accept
hyphens in module names. This is the single naming exception in the code
family - every other file and folder uses kebab-case (matching story slugs).

The helper collects shared type aliases and background factories that the
per-story `<slug>-stories.py` files can reuse. When those files are loaded
by hand (via importlib) rather than by `import` they still work; the epic
helper is the one module tests / adapters can import directly by name.

See: `context_tools/stories/src/formats/code/architecture-context.md`
"""
from __future__ import annotations

from typing import Literal, TypedDict, Union


class Given(TypedDict):
    given: str


class When(TypedDict):
    when: str


class Then(TypedDict):
    then: str


class And(TypedDict):
    and_: str  # `and` is a Python keyword; adapter maps this back to "and"


class But(TypedDict):
    but: str


Step = Union[Given, When, Then, And, But]
Background = tuple[Given, ...]


StoryStatus = Literal["stub", "exploration", "specification", "engineering"]


def default_background(customer_handle: str = "alex.morgan") -> Background:
    """Standard Background reused across most stories in this epic."""
    return (
        {"given": f'a Customer "{customer_handle}" is signed in with a populated Cart'},
    )


## manage-customer-orders/py/manage-customer-orders/place-new-order/add-item-to-cart/add_item_to_cart_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


ADD_ITEM_TO_CART: Final = {
    "story":        "Add Item To Cart",
    "actor":        "Customer",
    "domain_terms": ("Cart", "Product", "Cart Item", "Quantity"),
    "evidence":     (),
}


## manage-customer-orders/py/manage-customer-orders/place-new-order/browse-product-catalog/browse_product_catalog_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


BROWSE_PRODUCT_CATALOG: Final = {
    "story":        "Browse Product Catalog",
    "actor":        "Customer",
    "domain_terms": ("Product Catalog", "Product", "Category"),
    "evidence":     (),
}


## manage-customer-orders/py/manage-customer-orders/place-new-order/enter-shipping-address/enter_shipping_address_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


ENTER_SHIPPING_ADDRESS: Final = {
    "story":        "Enter Shipping Address",
    "actor":        "Customer",
    "domain_terms": ("Shipping Address", "Address Line", "Postal Code", "Country"),
    "evidence":     (),
}


## manage-customer-orders/py/manage-customer-orders/place-new-order/select-delivery-option/select_delivery_option_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


SELECT_DELIVERY_OPTION: Final = {
    "story":        "Select Delivery Option",
    "actor":        "Customer",
    "domain_terms": ("Delivery Option", "Delivery Speed", "Delivery Fee", "Estimated Arrival"),
    "evidence":     (),
}


## manage-customer-orders/py/manage-customer-orders/place-new-order/submit-order/submit_order_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


SUBMIT_ORDER_MAIN_FLOW: Final = {
    "story":        "Submit Order",
    "actor":        "Customer",
    "domain_terms": ("Order", "Cart", "Payment Method", "Order Confirmation", "Order Number"),
    "evidence":     ("Checkout workshop 2026-05-04 - happy-path wall walk",),

    "main_flow": {
        "name":         "order submitted with valid cart and payment",
        "given": (
            "a Cart with three Items totalling 149.98 USD",
            "And a Payment Method on file \"Visa ending 4242\"",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer confirms and submits the Order",
                ),
                "then": (
                    "an Order Confirmation is issued with an Order Number",
                    "And the Cart is emptied",
                ),
            },
        ),
    },
}

SUBMIT_ORDER: Final = {
    "story":        "Submit Order",
    "actor":        "Customer",
    "domain_terms": ("Order", "Cart", "Payment Method", "Order Number", "Order Status"),
    "evidence":     ("Checkout workshop 2026-05-04 - happy-path wall walk", "API spec v3 - POST /orders #\"submission errors\""),

    "submission_succeeds": {
        "name":         "order accepted for a valid cart and payment method",
        "given": (
            "a Cart \"CART-9001\" containing 3 Items totalling 149.98 USD",
            "And a Payment Method *\"Visa ****4242\" with status authorised*",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits the Order",
                ),
                "then": (
                    "an Order is created with status placed",
                    "And an Order Number matching pattern ORD-\\d{7} is returned",
                ),
            },
        ),
    },

    "submission_rejected_for_declined_card": {
        "name":         "order rejected when payment method is declined",
        "given": (
            "a Cart \"CART-9002\" totalling 89.50 USD",
            "And a Payment Method *\"MasterCard ****5150\" in status declined*",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits the Order",
                ),
                "then": (
                    "the Order is rejected with reason payment_declined",
                    "But the Cart contents are preserved for retry",
                ),
            },
        ),
    },
}

SUBMIT_ORDER_OUTLINE: Final = {
    "story":        "Submit Order - outline",
    "actor":        "Customer",
    "domain_terms": ("Order", "Payment Method", "Order Status"),
    "evidence":     ("API spec v3 - POST /orders #\"submission errors\"",),

    "outline": {
        "name":         "submission result varies with payment method status",
        "given": (
            "a Cart {cart_id} totalling {cart_total} {currency}",
            "And a Payment Method {payment_method} in status {payment_status}",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits the Order",
                ),
                "then": (
                    "the Order status is set to {order_status}",
                ),
            },
        ),
    },
}


## manage-customer-orders/py/manage-customer-orders/story-context.md

# Manage Customer Orders

**Status:** partially expanded

**Stories in scope:**
- *Place New Order*
- *Track Order Status*
- *Cancel Order*

**Context / notes:** Epic-root aggregate for the Python code-example tree that mirrors `examples/md/story-map.md` and `examples/ts/manage-customer-orders/`. Story data is pure data (dicts and tuples) so a code adapter can read it without importing a test framework. Folder names follow the kebab-case slug convention used across the code family; the epic helper is the sole snake_case exception because Python's import system does not accept hyphens in module names — see `context_tools/stories/src/formats/code/architecture-context.md`.


## manage-customer-orders/py/manage-customer-orders/story_runner.py

"""Generic scenario runner - the ONLY test-framework glue.

Every tier reuses this function; tier files just wire a Story constant, a
scenario key, and a factory that produces the tier's `TierImpl`. The runner:

1. Validates that every step string in the scenario has a matching key in
   `tier.given` / `tier.when` / `tier.then` - missing keys fail with the
   exact string and phase, so the author knows what's unimplemented.
2. Walks `given`, then each interaction's `when` steps, then dispatches one
   pytest test per `then` step (so each observable outcome is its own row).
3. Runs `cleanup` after every scenario, even on failure.

Sync and async step bodies both work - the runner awaits when needed.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Dict

import pytest

from story_types import Scenario, StepFn, Story, TierImpl


def _maybe_await(result: object) -> None:
    if inspect.isawaitable(result):
        asyncio.get_event_loop().run_until_complete(result)  # type: ignore[arg-type]


def _dispatch(step: str, table: Dict[str, StepFn], phase: str) -> None:
    fn = table.get(step)
    if fn is None:
        raise KeyError(
            f"Tier is missing a {phase!r} implementation for step {step!r}. "
            f"Add it to `tier.{phase}[{step!r}]`."
        )
    _maybe_await(fn())


def _label(kw: str, index: int, step: str) -> str:
    return f"{kw} {step}" if index == 0 else step


def run_scenario(
    story_name: str,
    scenario: Scenario,
    make_tier: Callable[[], TierImpl],
) -> None:
    """Emit one pytest class per scenario; one `test_*` method per `then` step.

    Call from a tier test file at module scope; pytest discovers the emitted
    class automatically.
    """
    tier_holder: Dict[str, TierImpl] = {}

    def setup_class() -> None:
        tier = make_tier()
        tier_holder["tier"] = tier
        for step in scenario["given"]:
            _dispatch(step, tier["given"], "given")
        for interaction in scenario["interactions"]:
            for step in interaction["when"]:
                _dispatch(step, tier["when"], "when")

    def teardown_class() -> None:
        tier = tier_holder.get("tier")
        if tier is not None:
            _maybe_await(tier["cleanup"]())

    methods: Dict[str, Callable[..., None]] = {}
    for interaction_index, interaction in enumerate(scenario["interactions"]):
        for then_index, step in enumerate(interaction["then"]):
            method_name = f"test_then_{interaction_index}_{then_index}"
            step_value = step

            def _method(self, _step: str = step_value) -> None:  # noqa: ANN001
                _dispatch(_step, tier_holder["tier"]["then"], "then")

            _method.__doc__ = _label("Then", then_index, step_value)
            methods[method_name] = _method

    cls = type(
        f"Test_{_slug(scenario['name'])}",
        (object,),
        {
            "setup_class": staticmethod(setup_class),
            "teardown_class": staticmethod(teardown_class),
            **methods,
        },
    )

    # Attach the class to the caller's module so pytest discovers it.
    frame = inspect.stack()[1].frame
    caller_globals = frame.f_globals
    caller_globals[cls.__name__] = cls
    cls.__module__ = caller_globals.get("__name__", cls.__module__)


def _slug(name: str) -> str:
    out = []
    prev_alnum = False
    for ch in name:
        if ch.isalnum():
            out.append(ch)
            prev_alnum = True
        else:
            if prev_alnum:
                out.append("_")
            prev_alnum = False
    return "".join(out).strip("_") or "scenario"


## manage-customer-orders/py/manage-customer-orders/story_types.py

"""Story types for Python spec-files.

Python's type system is dynamic - we can't produce a compile-time analogue of
TypeScript's `TierImpl<S>`. Instead the runner does runtime step-key
assertions (see `story_runner.py`): every step string in a scenario must
resolve to a callable in `tier.given` / `tier.when` / `tier.then`; missing
keys fail the run with a clear message.

The Story shape mirrors the TS reference architecture:

    STORY: Story = {
        "story": "Submit Order",
        "actor": "Customer",
        "domain_terms": ("Order", "Cart"),
        "evidence": ("Checkout workshop 2026-05-04",),

        "scenario_key": {
            "name": "order accepted for a valid cart and payment",
            "given": ("a Cart CART-9001 containing 3 Items totalling 149.98 USD",),
            "interactions": (
                {
                    "when": ("the Customer submits the Order",),
                    "then": ("an Order is created with status placed",),
                },
            ),
        },
    }

`given`, and every `when` / `then` inside an interaction, is a tuple of
plain-prose step strings. First step of each phase is unprefixed; continuation
steps carry their own `"And "` / `"But "` prefix inside the string, and the
tier's `given` / `when` / `then` dicts use the SAME string as the dispatch key.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Tuple, TypedDict, Union


StepFn = Callable[[], Union[None, Awaitable[None]]]
"""One step body. May be sync or async - the runner awaits either."""


class Interaction(TypedDict):
    """A when-then block within a scenario."""

    when: Tuple[str, ...]
    then: Tuple[str, ...]


class Scenario(TypedDict):
    """A behaviour walk-through under a story."""

    name: str
    given: Tuple[str, ...]
    interactions: Tuple[Interaction, ...]


# `Story` is a Story metadata dict merged with one Scenario per key. Python
# can't statically enforce the union like TS, so this is documented as a
# convention: unknown extra keys are treated as Scenario values by the runner.
Story = Dict[str, Any]


class TierImpl(TypedDict):
    """Tier contract - dispatch tables plus a cleanup hook.

    `given` / `when` / `then` are dicts keyed by the EXACT step strings from
    the scenario. `cleanup` runs after every scenario, regardless of outcome.
    """

    given: Dict[str, StepFn]
    when: Dict[str, StepFn]
    then: Dict[str, StepFn]
    cleanup: StepFn


## manage-customer-orders/py/manage-customer-orders/track-order-status/send-shipment-notification/send_shipment_notification_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


SEND_SHIPMENT_NOTIFICATION: Final = {
    "story":        "Send Shipment Notification",
    "actor":        "System",
    "domain_terms": ("Shipment", "Shipment Notification", "Tracking Number", "Notification Channel"),
    "evidence":     (),
}


## manage-customer-orders/py/manage-customer-orders/track-order-status/view-current-order-status/view_current_order_status_stories.py

"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


VIEW_CURRENT_ORDER_STATUS_MAIN_FLOW: Final = {
    "story":        "View Current Order Status",
    "actor":        "Customer",
    "domain_terms": ("Order", "Order Status", "Timeline Event"),
    "evidence":     ("Order tracking discovery session 2026-05-11",),

    "main_flow": {
        "name":         "customer sees the latest status of a placed order",
        "given": (
            "an Order \"ORD-4200077\" in status placed",
            "And a Timeline Event \"payment authorised\" recorded 10 minutes ago",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer opens the order detail view",
                ),
                "then": (
                    "the Order status placed is displayed prominently",
                    "And the Timeline shows the payment-authorised event",
                ),
            },
        ),
    },
}


## {epic-verb-noun}/{sub-epic-verb-noun}/{story-verb-noun}/{story_verb_noun}_story.ts

/**
 * Story: {Story Verb-Noun} (scenario fidelity - tier-neutral).
 * Calls helper-interface methods only - no assertions, no tier mechanism here.
 *
 * Tiers: {story_verb_noun}_test_helper.{tier}.ts implements {StoryVerbNoun}Helper
 * (tier ∈ domain | client | server | e2e | project-specific, e.g. api, db).
 */

import { scenario, story } from "../../../story-test";

export interface {StoryVerbNoun}Helper {
  givenPrecondition(): void | Promise<void>;
  whenAction(): void | Promise<void>;
  thenOutcome(): void | Promise<void>;
  thenAndOutcome(): void | Promise<void>;
}

export function create{StoryVerbNoun}Story(h: {StoryVerbNoun}Helper): void {
  story("{Story Verb-Noun}", () => {
    scenario("{main-flow outcome}", ({ given, when, then }) => {
      given("{given step text}", () => h.givenPrecondition());
      when("{when step text}", () => h.whenAction());
      then("{then step text}", () => h.thenOutcome())
        .and("{and step text}", () => h.thenAndOutcome());
    });
  });
}


## {epic-verb-noun}/{sub-epic-verb-noun}/{story-verb-noun}/{story_verb_noun}_test_helper.domain.ts

/** Tier: domain - {StoryVerbNoun}Helper backed by direct domain-class calls. */
import { describe } from "vitest";
import { create{StoryVerbNoun}Story, type {StoryVerbNoun}Helper } from "./{story_verb_noun}_story";

class DomainHelper implements {StoryVerbNoun}Helper {
  givenPrecondition(): void | Promise<void> {
    throw new Error("not implemented: givenPrecondition");
  }
  whenAction(): void | Promise<void> {
    throw new Error("not implemented: whenAction");
  }
  thenOutcome(): void | Promise<void> {
    throw new Error("not implemented: thenOutcome");
  }
}

describe("tier: domain", () => {
  create{StoryVerbNoun}Story(new DomainHelper());
});


## {epic-verb-noun}/{sub-epic-verb-noun}/{story-verb-noun}/{story_verb_noun}_test_helper.server.ts

/** Tier: server - {StoryVerbNoun}Helper backed by Supertest against the real route. */
import { describe } from "vitest";
import { create{StoryVerbNoun}Story, type {StoryVerbNoun}Helper } from "./{story_verb_noun}_story";

class ServerHelper implements {StoryVerbNoun}Helper {
  givenPrecondition(): void | Promise<void> {
    throw new Error("not implemented: givenPrecondition");
  }
  whenAction(): void | Promise<void> {
    throw new Error("not implemented: whenAction");
  }
  thenOutcome(): void | Promise<void> {
    throw new Error("not implemented: thenOutcome");
  }
}

describe("tier: server", () => {
  create{StoryVerbNoun}Story(new ServerHelper());
});


Separate tools run — toolset: `context_tools.clean_engineering.clean_engineering:CleanEngineering` action: `guidance` context.fidelity: `code`

Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.stories.stories:Stories
context:
  fidelity: acceptance_tests
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
  fidelity: acceptance_tests
action: generate
```
.\tools.ps1 run -
