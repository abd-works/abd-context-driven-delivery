# ddd-flaccid-data-object-no-behavior-2

- **entry_id:** 4d7f540d
- **artifact:** tests/domain/subscriber/subscriber.ts (Subscriber, Subscription, Billing interfaces)
- **rule:** (ddd) flaccid-data-object-no-behavior
- **wrong:** Subscriber, Subscription, and Billing are pure data interfaces with zero behavior methods. Subscriber has no updateContactDetails(), port(), portabilityStatus(). Subscription has no changePlan(). Billing has no pay(), updatePaymentMethod(). All these are domain operations that belong on these aggregates.
- **status:** fixed
