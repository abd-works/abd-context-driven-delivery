# ddd-flaccid-data-object-no-behavior

- **entry_id:** 3c6e430c
- **artifact:** tests/domain/cart/cart.ts (Cart interface)
- **rule:** (ddd) flaccid-data-object-no-behavior
- **wrong:** Cart is a pure data interface with only properties (id, bundle?, msisdn?, simType?, iccid?, portingInfo?) and zero behavior methods. All operations (selectPlan, selectNumber, save) are pushed to CartRepository. This is an anemic domain model — Cart should own its behavior: selectPlan(), selectNumber(), selectSim(), port(), checkout().
- **status:** fixed
