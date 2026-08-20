# ddd-invented-types-not-domain-concepts

- **entry_id:** 6f91af0f
- **artifact:** tests/domain/order/order.ts (OrderResult, OrderRepository)
- **rule:** (ddd) invented-types-not-domain-concepts
- **wrong:** OrderResult is a separate type with { status, payUpFront, verified } — these are fields that belong on Order itself. OrderRepository exists but Order is created from Cart.checkout() and read as the checkout outcome — no independent repository lifecycle is needed.
- **status:** open
