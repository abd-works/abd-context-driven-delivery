# reconcile-live-against-sandbox-5

- **entry_id:** b0dfee62
- **artifact:** tests/onboard-a-customer/pick-number.md
- **rule:** (process) reconcile-live-against-sandbox
- **wrong:** Staging spec said PATCH /mv/customer sets cart.portability on port submit; live flow POSTs /mv/customer/portability (useNumberPortability.ts) and updates client recoil via updateCustomer ??? no cart PATCH until later.
- **status:** open
