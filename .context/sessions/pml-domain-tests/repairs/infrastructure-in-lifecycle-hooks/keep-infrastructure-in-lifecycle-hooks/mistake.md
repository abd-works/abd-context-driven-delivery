# keep-infrastructure-in-lifecycle-hooks

- **entry_id:** b3f72e19
- **artifact:** tests/onboard-a-customer/sign-up-create-account.e2e.ts, tests/onboard-a-customer/sign-up-select-plan.e2e.ts
- **rule:** keep-infrastructure-in-lifecycle-hooks — given blocks must contain domain operations only; infrastructure setup (browser session init, app wiring) belongs in beforeAll/afterAll lifecycle hooks, never inside a Gherkin-labelled given
- **wrong:** given('the prospect is unauthenticated') contained paradise = await ParadiseMobileE2e.initialize(config) — label described a domain state but the body was pure infrastructure init with no relation to authentication
- **status:** fixed
