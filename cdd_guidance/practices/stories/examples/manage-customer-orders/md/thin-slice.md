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
