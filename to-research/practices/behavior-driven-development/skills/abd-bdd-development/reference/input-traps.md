# Input traps — abd-bdd-development

Pre-flight only — not grill questions.

- **Signature completeness** — Are all `// BDD: SIGNATURE` markers present? Partial implementation makes RED pass look done when it is not.
- **Test isolation** — Does each test arrange its own state, or is state leaking through shared objects?
- **Observable behavior vs. internals** — Are assertions checking public outcomes or private implementation details?
- **Mock boundaries** — Are mocks at architecture module boundaries, or are domain classes being mocked?
- **Code minimalism** — Is production code adding features no test requires?
