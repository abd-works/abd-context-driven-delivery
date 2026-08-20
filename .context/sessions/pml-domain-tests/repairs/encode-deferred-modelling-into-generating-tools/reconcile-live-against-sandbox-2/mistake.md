# reconcile-live-against-sandbox-2

- **entry_id:** da130f62
- **artifact:** tests/onboard-a-customer/select-sim.md
- **rule:** (process) reconcile-live-against-sandbox
- **wrong:** First scenario Given only required cart.bundle; live stub mode redirects away from /onboarding/select-sim unless cart also has msisdn (or portability) because env.MODE is stub so redirectToCurrentStep is NOT short-circuited (that only happens when MODE===development).
- **status:** fixed