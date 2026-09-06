# ddd-screen-interface-not-a-domain-object-2

- **entry_id:** 8c2b3f02
- **artifact:** tests/domain/inventory/pick-number.ts (PickNumber, PortNumber interfaces)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** PickNumber and PortNumber modeled as separate screen interfaces with open(), isShowing(), goToPortNumber() — screen drivers, not domain objects. Picking a number is an operation on Cart (selectNumber). Porting is an operation on Cart (port). These should be operations on the Cart aggregate.
- **status:** fixed
