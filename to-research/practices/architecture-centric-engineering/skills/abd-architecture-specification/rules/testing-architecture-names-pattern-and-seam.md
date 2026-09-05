---
scanner: testing-architecture-pattern-and-seam
---

### Rule: The test-helpers context file names a test pattern and a stub boundary

The test-helpers `architecture-context.md` MUST name the testing pattern in use (e.g. Sandbox, Unit + Integration, BDD via Gherkin, Component-test pyramid) AND the exact boundary at which external systems are stubbed (e.g. axios layer, repository interfaces, HTTP transport, partner SDK). Without both facts, a new engineer cannot write a test that fits the suite — they invent their own boundary and the suite becomes inconsistent. The two facts are also what the central spec's `## Testing Architecture` paragraph quotes; without them in the test-helpers file, the central spec has nothing to point at. Passing means both the pattern name and the stub boundary appear as concrete, code-checkable statements. Failing means the file describes tooling without naming the pattern, or names the pattern but leaves the stub boundary implicit.

#### DO

- Name the testing pattern and the stub boundary together, with concrete file or library references.

  **Example (pass):**
  ```markdown
  # Test Helpers

  **Pattern:** Sandbox. Domain fixtures drive the real Express app via
  Jest + Supertest; the application stack runs unmodified.

  **Stub boundary:** outbound HTTP is stubbed at the `axios.request`
  boundary in `/tests/helpers/axios-sandbox.ts`; Cognito JWT verification
  is stubbed at the `CognitoService.verify` boundary in
  `/tests/helpers/cognito-sandbox.ts`. Nothing else is stubbed.
  ```

- Name the layer-to-tech mapping so the reader can reproduce the suite locally.

  **Example (pass):** "Runner: Jest 29 (`jest.config.ts`). HTTP exercise: Supertest. Stubs: `jest.mock` registered in helper modules. Fixtures: domain test objects in `/tests/domain-helpers/`. Coverage: c8 with 80 % branch threshold."

#### DO NOT

- Name the framework but skip the boundary.

  **Example (fail):** "Tests use Jest with Supertest." — Silent on what runs for real and silent on what is mocked. A new engineer guesses the boundary and the suite drifts.

- Describe the boundary in prose without naming the file or function.

  **Example (fail):** "Outbound calls are stubbed somewhere near the HTTP layer." — Which layer? Which file? "Somewhere" is not a boundary.

- Describe what tests should achieve without naming how the suite is built.

  **Example (fail):**
  ```markdown
  # Test Helpers

  Tests should verify behaviour, not implementation. Aim for high
  coverage and use meaningful names.
  ```
  These are sentiments, not the architecture. A reader cannot reproduce the suite from this file.

**Source:** Hexagonal / Ports & Adapters — the stub boundary is the architectural seam under test; if it isn't named, the suite has no shape.
