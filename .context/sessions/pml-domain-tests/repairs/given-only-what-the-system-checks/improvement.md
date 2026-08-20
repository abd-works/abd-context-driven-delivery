# given-only-what-the-system-checks

- **tool:** Stories
- **error:** Given named a field the running system never uses for that decision (e.g. `metadata.verified` when routing keys off billing / cart / identity).
- **rule:** given-only-what-the-system-checks
- **what changed:**
  - **Prose — yes.** `stories.md`: Given states only conditions the running system actually checks for the behaviour under test.
  - **Sketch / template / example — yes.** `stories-sketch.md`: `given {precondition the running system actually checks}`.
  - **Detector — no.** Judgment against the live walk.
  - **Generator — no.**
