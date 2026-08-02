## Top-level artifacts (this lens)

**Subjects** — domain things, states, or observable conditions (top-level `describe`s per `bdd.md`). Thin: subject + candidate `that` / `with` + TODOs. Not full `it should` suites.

Key rules: `state-not-when` — nest by the state or condition that enables an observation, never by a `when` trigger; `nest-by-enabling-events` — sub-groupings are conditions that unlock further behavior, not implementation steps.
