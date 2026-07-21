---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Manage Customer Orders (UX example)

**Home:** `contexts/ux/examples/manage-customer-orders/`  
Connected lenses: Stories (exploration) · Clean Engineering (modules) · UX (mockup + Story Demo shell).  
Thin slice: `.context/thin-slice.md`

---

(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Select Product
        (S) Customer --> Add Item To Cart
        (S) Customer --> Remove Item From Cart
        (S) Customer --> Submit Order

---

## Scope boundary

**In scope:** Increment 1 cart spine for the Story Demo shell.  
**Out of scope:** Shipping, delivery, track, cancel (not in this example package).
