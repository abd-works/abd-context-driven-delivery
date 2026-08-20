# seed-prior-story-as-given

- **tool:** Stories
- **error:** A later story replayed a prior story's When to reach signed-in (or equivalent) instead of seeding that state as Given from fixtures.
- **rule:** seed-prior-story-as-given
- **what changed:**
  - **Prose — yes.** `stories.md`: a later story's Given is seeded from prior-story fixtures (`givens.ts` / `examples/`), not a replay of that story's When.
  - **Sketch / template / example — no.** Layout already has `givens.ts` + `examples/` at epic / sub-epic.
  - **Detector — no.**
  - **Generator — no.**
