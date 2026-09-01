# hang-deps-on-owning-bc



- **tool:** Ddd

- **error:** Cross-context arcs were parked in a free-form Cross-Context Relationships dump instead of hanging on the owning aggregate.

- **rule:** hang-deps-on-owning-bc

- **what changed:**

  - **Prose — yes.** `ddd.md`: each aggregate lists upstream contexts under `#### Dependencies` (pattern, what crosses, concrete integration). Cross-aggregate refs stay on the aggregate. No global `## Dependencies` section.

  - **Sketch / template / example — yes.** `ddd-sketch.md` uses `depends:` on each aggregate; `bounded-context-template.md` and `examples.md` show `#### Dependencies` under each `###` aggregate.

  - **Map card format — yes.** Context cards use **Vendor** + **Scope**; aggregates use bulleted **Boundary members** and **Refs** (no owning team, implementation, protected invariants, or consistency labels on the bounded_context card). Rules: `vendor-not-implementation`, `aggregate-root-and-members`, `refs-not-consistency-labels`.

  - **Catalog — yes.** `catalog/fidelities/ddd-bounded_context.html` and `ddd-building_blocks.html` embedded templates match; guidance rules updated.

  - **Detector — no.**

  - **Generator — no.**


