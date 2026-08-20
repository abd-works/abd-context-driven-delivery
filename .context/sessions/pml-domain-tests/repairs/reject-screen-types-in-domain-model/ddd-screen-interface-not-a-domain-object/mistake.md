# ddd-screen-interface-not-a-domain-object

- **entry_id:** 4f1a0e01
- **artifact:** tests/domain/cart/cart.ts (SelectSim interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** SelectSim modeled as its own interface with open(), isShowing(), selectEsim(), selectPhysicalSim(), continueWithEsim(), continueWithPhysicalSim() — a screen driver, not a domain object. Selecting a SIM type is an operation on Cart.
- **status:** fixed
