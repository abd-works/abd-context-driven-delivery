# load-with-identity-in-hand

- **tool:** Ddd, Stories
- **error:** Wraps loaded aggregates from ambient browser session (`load()` with no id, `cartRepository().current()`), then re-loaded the same object in every step.
- **rule:** load-with-identity-in-hand
- **what changed:**
  - **Prose — yes.** Stories + DDD **Document** / tactics: `load` takes the identity already in hand; do not assume a session; load once at the highest Given and reuse the variable; a cart has no identity outside its prospect. This is wrap / current-state modelling — not CE constructor injection (`use-explicit-dependencies`).
  - **Sketch / template / example — no.**
  - **Detector — no.**
  - **Generator — no.**
