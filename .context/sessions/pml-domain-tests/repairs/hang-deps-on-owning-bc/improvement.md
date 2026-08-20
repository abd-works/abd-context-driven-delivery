# hang-deps-on-owning-bc

- **tool:** Ddd
- **error:** Cross-context arcs were parked in a free-form Cross-Context Relationships dump instead of hanging on the owning contexts.
- **rule:** hang-deps-on-owning-bc
- **what changed:**
  - **Prose — yes.** `ddd.md`: each dependency is `Source → Target` under `## Dependencies` (and `cross-agg` / `cross-bc` on the aggregate). Do not invent a dump section.
  - **Sketch / template / example — yes.** `ddd-sketch.md` and `bounded-context-template.md` comment on hanging arcs; template already had `## Dependencies` as Source → Target.
  - **Detector — no.**
  - **Generator — no.**
