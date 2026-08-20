# no-ambient-session-state

- **entry_id:** a28bfbb5
- **artifact:** tests/onboard-a-customer/sign-up-select-plan.e2e.ts
- **rule:** no-ambient-session-state — never assume that a universal browser session implicitly connects repositories across domain aggregates; each repository must be loaded with an explicit reference obtained from what has already been loaded in the current test; assuming session state is invisible coupling that breaks when tests run out of order or across boundaries
- **wrong:** prospectRepository.load() called with no arguments after catalog.select(), implicitly relying on the browser session to know which prospect to return; no explicit identity reference was passed
- **status:** fixed
