# Rule: Lightweight and Precise

**Scanner:** Manual review

Create **lightweight but precise** documentation during shaping. Focus on structure and scope, not detailed specifications.

## DO

Make the map easy to walk through — it tells a story. Show hierarchy and flow without detailed specifications.

```
(E) Manage Orders
  (SE) Place Order
    (S) Validate Order Items
  (SE) Review Order
    (S) View Order Summary
    (S) Modify Order Items
```

This shows hierarchy and flow — that is enough at shaping stage.

## DON'T

Do not add:
- Detailed API specs
- Database schema
- UI mockups
- Validation rules with detail
- Technical implementation notes

Example of over-elaboration (wrong at shaping):
```
(E) Manage Orders
  → Detailed API specs: POST /orders with JSON body {item_id, quantity, customer_id}
  → Database: orders table with FK to customers
  → UI: Modal with item picker and quantity stepper
```

If you have this kind of detail from context, put it in `notes` with a `context_source` citation — not in the story structure itself.
