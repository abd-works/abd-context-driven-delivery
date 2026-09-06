# ddd-screen-interface-not-a-domain-object-6

- **entry_id:** d6f70806
- **artifact:** tests/domain/pay-now/pay-now.ts (PayNow interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** PayNow modeled as its own interface with open(), confirmPayment(), isSuccessShown() — a screen driver. Making a payment is an operation on Billing (pay(amount)).
- **status:** fixed
