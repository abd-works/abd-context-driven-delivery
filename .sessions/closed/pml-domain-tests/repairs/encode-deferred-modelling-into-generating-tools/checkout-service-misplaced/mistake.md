# checkout-service-misplaced

- **entry_id:** 0d1d9c44
- **artifact:** tests/domain/.context/domain-model.md
- **rule:** checkout-service-misplaced
- **wrong:** CheckoutService <<Domain Service>> with placeOrder(cart, prospect, payment) as a top-level domain service; OrderResult <<Value Object>> as a separate type
- **status:** fixed