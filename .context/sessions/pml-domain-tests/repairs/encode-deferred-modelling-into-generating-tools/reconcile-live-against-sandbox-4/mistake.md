# reconcile-live-against-sandbox-4

- **entry_id:** 121683f3
- **artifact:** tests/onboard-a-customer/pick-number.md
- **rule:** (process) reconcile-live-against-sandbox
- **wrong:** Staging spec referenced GET /mv/numbers for MSISDN inventory; live app calls GET /mv/inventory/msisdn (useGetNumbers.ts axios.get on env.midtier.mavenir.inventory + '/msisdn').
- **status:** fixed