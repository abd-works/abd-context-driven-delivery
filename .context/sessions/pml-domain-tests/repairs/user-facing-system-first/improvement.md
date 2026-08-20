# user-facing-system-first

- **tool:** Ddd
- **error:** The context map started at external systems of record (vendor column at the left) and put the consumer app last.
- **rule:** user-facing-system-first
- **what changed:**
  - **Prose — yes.** `ddd.md` bounded_context + Document: the wrapping / user-facing system sits first (left / upstream); vendors sit downstream.
  - **Sketch / template / example — yes.** `ddd-sketch.md` and `bounded-context-template.md` say consumer app first.
  - **Detector — no.** Layout is a judgment call, not a pixel scanner.
  - **Generator — no.**
