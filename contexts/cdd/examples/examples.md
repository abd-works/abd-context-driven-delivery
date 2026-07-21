# CDD examples

## resolve_targets → tools run

```yaml
toolset: contexts.cdd.cdd:Cdd
context:
  fidelity: explore
tool: resolve_targets
```

One row (example):

```yaml
context: ddd
fidelity: building_blocks
run:
  toolset: contexts.ddd.ddd:Ddd
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
