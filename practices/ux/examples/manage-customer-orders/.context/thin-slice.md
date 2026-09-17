---
fidelity: [discovery]
artifact: [thin-slice]
format: md
---

# Thin slicing — Manage Customer Orders (UX example)

## Product / context

**Product:** Manage Customer Orders — catalog → cart → checkout (UX example; runs in the Story Demo shell).

**Slicing intent:** Increment 1 proves the ShoppingCart public seam (select, add, remove, submit) before shipping / cancel depth. Cart total is always visible on the cart screen — not a separate story.

**Spine vs optional:** Spine is **Select Product → Add Item To Cart → Remove Item From Cart → Submit Order**. Shipping, delivery, tracking, and cancel are out of this example package.

## Increments

### Increment 1: Shop and submit a cart

**Outcome:** Customer selects a Product, manages Cart lines (total always shown), and submits an Order.

**Slicing notes:** Fake ExampleFactory + browser Story Demo only. No shipping address or delivery options yet.

**Stories in this increment** *(order reflects flow within the slice):*

- *Select Product*
- *Add Item To Cart*
- *Remove Item From Cart*
- *Submit Order*
