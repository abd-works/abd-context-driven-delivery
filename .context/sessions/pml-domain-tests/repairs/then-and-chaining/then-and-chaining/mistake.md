# then-and-chaining

- **entry_id:** ebae71c7
- **artifact:** tests/onboard-a-customer/sign-up-select-plan.e2e.ts
- **rule:** then-and-chaining — in a scenario with multiple outcome assertions, only the first outcome uses then(); every subsequent outcome chains with .and(); repeated then() calls break the Gherkin narrative and ignore the DSL's StepChain return value
- **wrong:** five consecutive then() calls in the Catalog scenario instead of one then() followed by four .and() chains
- **status:** fixed
