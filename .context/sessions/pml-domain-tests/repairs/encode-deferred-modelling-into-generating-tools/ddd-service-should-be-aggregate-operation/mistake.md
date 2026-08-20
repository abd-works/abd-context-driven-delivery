# ddd-service-should-be-aggregate-operation

- **entry_id:** 2b5d320b
- **artifact:** tests/domain/checkout/checkout.ts (CheckoutService interface)
- **rule:** (ddd) service-should-be-aggregate-operation
- **wrong:** CheckoutService modeled as a separate service with seedPayment() and capturePayment(). capturePayment() is the domain operation of placing an order — it belongs on Checkout (or Cart). seedPayment() is test seeding infrastructure, not a domain operation. OrderResult as a separate type is not a domain concept — its fields (payUpFront, verified) belong on Order.
- **status:** fixed