# do-not-mint-a-bounded-context-per-aggregate

- **tool:** Ddd
- **error:** Catalog (a real language/team name) was treated as “wrong” because it had one aggregate (Plan), so the model wanted a bounded context per aggregate — or to rename the BC to Plan.
- **rule:** one-meaning-per-context (existing — did not distinguish context vs aggregate)
- **what changed:**
  - **Prose — yes.** `context_tools/ddd/ddd.md` bounded_context: a bounded context is one model/language/team; an aggregate is a consistency cluster **inside** it; several aggregates sharing that language stay in the same context; do not mint a BC per aggregate. `one-meaning-per-context` restates that. Input trap: a new BC for each aggregate.
  - **Sketch — yes.** `context_tools/ddd/templates/ddd-sketch.md` names the BC, then the aggregates it holds (two roots in the example). Dropped the one-root-per-context example that taught 1:1 wrap.
  - **Detector — no.** Did **not** add `bc-name-matches-sole-aggregate`.
  - **Generator — no.**
