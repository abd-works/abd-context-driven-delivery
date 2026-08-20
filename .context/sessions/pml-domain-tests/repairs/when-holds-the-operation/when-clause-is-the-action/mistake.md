# when-clause-is-the-action

- **entry_id:** ecbc8016
- **artifact:** tests/onboard-a-customer/sign-up-select-plan.e2e.ts
- **rule:** when-clause-is-the-action — the when block must contain the actual domain operation being exercised; empty when blocks with comments (e.g. "// getAvailablePlans() handles navigation internally") are a defect; domain operations that can be lifted into when must be lifted; then blocks are for assertions only
- **wrong:** when block was empty with a comment; getAvailablePlans() was called repeatedly inside each then block instead of once in when; then blocks performed I/O instead of asserting on already-fetched data
- **status:** fixed
