### Rule: Testing architecture names the stub boundary as an architectural decision

The Testing Architecture section at blueprint fidelity exists to name **where, in the codebase, tests stop using real components and start using stubs** — and to make that line an architectural decision the rest of the codebase can rely on. The tiers (unit, sandbox, integration) are scaffolding; the stub boundary is the architectural content. Passing means a developer writing a new test knows, from this section alone, exactly which file or interface they should stub for their tier and which they must leave real. Failing means the section catalogues tools and frameworks ("we use Jest, Supertest, Sinon") without ever saying where the line between real and stubbed actually falls.

A stub boundary that is named in the blueprint becomes the single contract every per-folder file and every test author can reference. A stub boundary that is left implicit is renegotiated in every PR.

#### DO

- Name the exact file, interface, or layer where each tier replaces real with stub. The name must be specific enough to be uncopyable.

  **Example (pass):** "Sandbox tests start the real Express server with real middleware; outbound HTTP is stubbed at `services/Axios/factory.ts` — every entity controller uses a stub axios instance constructed by the factory, and no test mocks per-call." A reader can find this file and verify; a test author knows exactly what to do.

- State, for each tier, what is *real* alongside what is *stubbed*. The pairing is what makes the architecture decision legible.

  **Example (pass):** "Unit tier — only the file under test is real; every imported module that performs I/O is replaced via `require.cache` patching (ADR-003). Sandbox tier — the full server is real; only the outbound HTTP factory is stubbed."

- Treat the stub boundary as a constraint on production code as well as on tests. If a downstream call cannot be reached through the named stub boundary, that is a defect in the *production code*, not the test.

#### DO NOT

- List test frameworks or test file conventions instead of naming the boundary.

  **Example (fail):** "Tests live in `*.spec.ts` files alongside source, run under Jest, and use Supertest for HTTP." Tooling and file layout tell a reader nothing about where the architectural line falls.

- Define a tier by what it *intends* rather than what it touches.

  **Example (fail):** "Integration tests verify end-to-end behaviour." Intent without a named boundary leaves every developer to guess what counts as integration; the answer drifts.

- Leave the boundary at a generic phrase like "external dependencies are mocked".

  **Example (fail):** "Unit tests stub external dependencies." Which external dependencies? Stubbed how? At which seam? Without specificity, the rule cannot be enforced and the architecture is not actually decided.

**Source:** A test tier is a tooling label; the stub boundary is the architecture. Naming the boundary is what makes testing part of the system's design rather than a downstream concern.
