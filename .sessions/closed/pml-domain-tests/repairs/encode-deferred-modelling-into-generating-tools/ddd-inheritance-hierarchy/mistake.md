# ddd-inheritance-hierarchy

- **entry_id:** 5d57e45e
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (ddd) inheritance-hierarchy
- **wrong:** Customer is shown as a flat <<Entity>> with no inheritance relationship. Prospect and Subscriber both share identity, address, verification, and metadata — those common attributes belong in Customer as the base type, with Prospect and Subscriber inheriting from it. The diagram has no generalisation arrows showing this hierarchy.
- **status:** fixed