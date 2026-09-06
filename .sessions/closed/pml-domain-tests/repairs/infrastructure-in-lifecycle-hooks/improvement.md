# infrastructure-in-lifecycle-hooks

- **tool:** Stories
- **error:** `given(` described domain state but the body was browser/app `initialize` — infrastructure dressed as a Gherkin step.
- **rule:** infrastructure-in-lifecycle-hooks
- **what changed:**
  - **Prose — yes.** `stories.md`: boot / `initialize` / app wiring live in `beforeAll` / `afterAll`; `given(` is domain state only.
  - **Sketch / template / example — no.**
  - **Detector — no.**
  - **Generator — no.**
