# ddd-screen-interface-not-a-domain-object-4

- **entry_id:** b4d5e604
- **artifact:** tests/domain/billing/billing.ts (BillingPage interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** BillingPage modeled as its own interface with open(), isShowing(), latestInvoiceAmount(), paymentMethodLastFour(), expandPastInvoices(), pastInvoiceMonthLabels() — a screen driver. Billing already exists as a domain entity with invoices, transactions, and defaultPayment. These are read operations on the Billing aggregate.
- **status:** fixed
