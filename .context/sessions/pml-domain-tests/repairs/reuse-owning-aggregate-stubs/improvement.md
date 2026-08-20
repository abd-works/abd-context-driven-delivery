# reuse-owning-aggregate-stubs

- **tool:** Stories, strategy
- **error:** The test invented a local stub (or named the wrong contract) instead of taking the stub from the non-core aggregate's own folder / source repository.
- **rule:** reuse-owning-aggregate-stubs
- **what changed:**
  - **Prose — yes.** `stories.md` and `.context/context-as-code-strategy.md`: for a non-core aggregate, take stubs from `domain/{bounded-context}/{aggregate}/stubs/{system}/` (that aggregate's source). Do not invent a test-local stub. Do not stub the seam you are proving. (Wrong original title: stub-fidelity-mirrors-real-api-contract.)
  - **Sketch / template / example — no.** Folder layout already had `stubs/{system}/` on the aggregate.
  - **Detector — no.**
  - **Generator — no.**
