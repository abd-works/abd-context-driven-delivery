# ddd-screen-interface-not-a-domain-object-5

- **entry_id:** c5e6f705
- **artifact:** tests/domain/payment-method/payment-method.ts (PaymentMethodPage interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** PaymentMethodPage modeled as its own interface with open(), currentCardLastFour(), startChangeCard(), isUpdateStepShown() — a screen driver. Updating payment method is an operation on Payment (owned by Billing). currentCardLastFour is a read on Billing.defaultPayment.
- **status:** fixed
