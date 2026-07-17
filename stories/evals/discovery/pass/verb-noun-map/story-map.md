---
fidelity: [discovery]
artifact: [story-map]
format: md
example-of: eval-pass
---

# Story Map — Manage Customer Orders

**Sources / context:** discovery eval pass fixture

---

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

---

## Scope boundary

**In scope:** place, track, and cancel customer orders
**Out of scope:** inventory replenishment, returns after delivery

---

## Thin slices

### Increment 1: Place a first order

**Outcome:** A customer can browse, cart, and submit an order

**Stories:**
- Browse Product Catalog
- Add Item To Cart
- Enter Shipping Address
- Select Delivery Option
- Submit Order
