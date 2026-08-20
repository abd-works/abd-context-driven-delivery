# reconcile-live-against-sandbox-6

- **entry_id:** 83a71d38
- **artifact:** tests/onboard-a-customer/pick-number.md
- **rule:** (process) reconcile-live-against-sandbox
- **wrong:** Staging spec said prospect proceeds to /onboarding/select-plan after picking a number; live app navigates to /onboarding/select-sim via useReserveNumber.ts navigate('../onboarding/select-sim').
- **status:** fixed