# ddd-screen-interface-not-a-domain-object-3

- **entry_id:** a3c4d503
- **artifact:** tests/domain/dashboard/dashboard.ts (Dashboard interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** Dashboard modeled as its own interface with open(), isShowing(), dataSectionTitle(), dataConsumptionText(), unlimitedLabelVisible(), billsSectionTitle(), latestInvoiceAmount() — a screen driver, not a domain object. Dashboard displays Subscriber data (subscription usage, billing summary). These are read operations on Subscriber, Subscription, and Billing aggregates.
- **status:** fixed
