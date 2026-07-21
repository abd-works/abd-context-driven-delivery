---
fidelity: [discovery]
artifact: [story-map]
format: md
example-of: eval-fail
---

# Story Map — Manage Customer Orders (actor in story name)

<!--
Violates: verb-noun-format.

Story names start with the actor noun (`Customer …`) even though the actor
is already declared before `-->`. Actor belongs as metadata before the arrow,
never inside the story name.
-->

(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Customer Browse Product Catalog
        (S) Customer --> Customer Add Item To Cart
        (S) Customer --> Customer Submit Order
    (E) Track Order Status
        (S) Customer --> Customer View Current Order Status
