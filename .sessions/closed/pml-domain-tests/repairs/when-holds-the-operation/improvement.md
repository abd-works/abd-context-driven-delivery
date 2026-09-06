# when-holds-the-operation

- **tool:** Stories
- **error:** When was left empty (or a comment) and the domain operation ran inside Then, so Then did I/O instead of asserting.
- **rule:** when-holds-the-operation
- **what changed:**
  - **Prose — yes.** `stories.md`: When holds the domain operation; empty When is a defect; Then only asserts on what When already produced.
  - **Sketch / template / example — yes.** `stories-sketch.md`: `when {the domain operation}`.
  - **Detector — no.**
  - **Generator — no.**
