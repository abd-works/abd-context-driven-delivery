# Grill me — abd-story-acceptance-test

**Mechanics:** [`common/reference/grill-me-with-practice-skill.md`](../../../../common/reference/grill-me-with-practice-skill.md) — one question at a time; generate-to-learn when enough is shared.

Ask until test intent and fixtures are unambiguous:

- Which behaviours are we actually proving — are there paths nobody has walked through yet?
- At boundaries depending on another system: what responses are realistic vs assumed?
- Where are we using test doubles — do they behave like production, or a fantasy?
- Are fixture values production-plausible, or "foo" and "123"?
- What does failure look like — timeout, partial success, concurrent conflict — or only happy path?
- Does every value trace to a spec Examples table — and do stubs use those exact values?
