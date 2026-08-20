# extract-assertion-helper

- **entry_id:** cc225fd9
- **artifact:** tests/onboard-a-customer/sign-up-select-plan.e2e.ts
- **rule:** extract-assertion-helper — when the same assertion structure repeats more than twice, extract a named helper function with an anonymous data-bag parameter; the helper encapsulates the repetitive expect() calls; call sites pass only the concrete values as an object literal
- **wrong:** four identical plan-assertion blocks each repeating expect(plan.name), expect(plan.price), expect(plan.totalPrice), expect(plan.features).toHaveLength, expect(plan.features[i].text) inline in the .and() callback
- **status:** fixed
