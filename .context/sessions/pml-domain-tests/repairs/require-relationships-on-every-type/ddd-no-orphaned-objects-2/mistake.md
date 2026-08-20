# ddd-no-orphaned-objects-2

- **entry_id:** bb88f3ba
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (ddd) no-orphaned-objects
- **wrong:** Credentials and Session are orphaned Value Objects with no relationship to any aggregate, entity, or service. Every domain object must have at least one relationship. Credentials and Session are used by AuthenticationService — they should be connected with dependency or composition arrows.
- **status:** fixed
