---
fidelity: [exploration, specification, engineering]
artifact: [ac, scenario, test]
scanner: scenario-coverage
kind: quality

---

# Rule: Scenario coverage

Every story must have walk-throughs (AC / scenarios / tests) that together cover **every behavioural path** the story implies. Three coverage axes:

1. **Happy path** — the main successful flow
2. **Error paths** — every reason the story can fail (invalid input, business rule violation, upstream failure)
3. **Boundaries** — edges of ranges, empty/full states, first/last, allowed/disallowed transitions
4. **Channels** — every channel the story is exposed on (web, mobile, API, back-office) uses channel-appropriate language

A walk-through-set that only covers happy path is under-explored. A walk-through-set that ignores a channel silently assumes it behaves the same as another channel — which is where bugs live.

## DO

- Enumerate every branch the story implies: at least one walk-through per branch of every business rule the story mentions
- Enumerate boundaries: for every numeric range, list first-below / at / first-above; for every state machine, list every transition
- Cover every channel the story is exposed on, using that channel's vocabulary (see channel section below)
- When two channels behave the same, say so explicitly — don't leave it inferred

## DON'T

- Ship a story with only a happy-path walk-through unless you are at *exploration* fidelity and specification is planned
- Enumerate every permutation for its own sake — see `scenario-outline-structure.md` for how to compress key examples
- Assume web-style vocabulary applies to API or mobile — each channel has its own vocabulary
- Skip a boundary because "the code handles it" — the walk-through documents the intent, the code enforces it

## Axes of coverage

### Happy path

Every story has exactly one happy path walk-through. It reads as the shortest successful sequence of `Given → When → Then` that produces the story's outcome.

### Error paths

For each of these, add a walk-through:

- Every **business rule violation** the story implies (over limit, wrong state, missing prerequisite)
- Every **input validation** failure the story owns (invalid format, missing required field)
- Every **upstream failure** the story handles (gateway timeout, downstream 5xx, event bus unavailable)

If the story does not handle an upstream failure explicitly, add a walk-through that documents the *deferred* behaviour (e.g. "propagates the error, retried by caller") or drop the upstream from the story.

### Boundaries

For every numeric range, add walk-throughs at:

- **Just below** the boundary
- **At** the boundary
- **Just above** the boundary

For every state machine, walk-throughs for:

- Every allowed transition
- At least one representative **disallowed** transition per state

### Channels

Every channel the story is exposed on gets its own walk-through, using channel-appropriate vocabulary:

| Channel | Vocabulary |
|---|---|
| Web | `sees`, `clicks`, `enters`, `is shown`, `is redirected to` |
| Mobile | `taps`, `swipes`, `receives push notification` |
| API | `POSTs`, `receives HTTP {code}`, `returns response body containing` |
| Back-office / admin | `looks up`, `overrides`, `approves`, `records audit entry` |
| Event / async | `emits event {name}`, `subscribes to`, `is eventually consistent when` |

Two channels sharing behaviour must state it: "the API channel behaves as the web channel, verified by scenario `<name>`".

## At each fidelity

**Exploration — AC:**
```
Story: Customer submits payment from web

WHEN the Customer enters a valid Amount and Recipient
AND the Customer clicks Submit
THEN the Confirmation Number is shown

BUT WHEN the Amount exceeds the daily Limit
THEN a rejection message names the daily Limit

BUT WHEN the Recipient is on the block list
THEN a rejection message names the Recipient status

# Coverage: happy path (1), business-rule failures (2), channel = web
```

**Specification — scenarios:**
- Same three walk-throughs as full scenarios
- Add boundary walk-throughs for the daily Limit: `Amount = Limit - 0.01`, `Amount = Limit`, `Amount = Limit + 0.01`
- Add a walk-through per additional channel (API, mobile) OR an explicit "same as web" citation

**Engineering — tests:**
- One `it` / `test` per walk-through, no more, no less (see `tests-implement-specification.md`)
- Missing test for an in-scope walk-through is a coverage gap
- Extra test not tied to a walk-through is a signal the walk-throughs are missing a case — add the walk-through first, then the test (see `bug-fix-test-first.md`)

## Cross-references

- `scenario-outline-structure.md` — how to compress an enumeration into a scenario outline instead of many separate scenarios
- `four-to-nine-children.md` — a story with 12 walk-throughs may be doing three stories' work
- `tests-implement-specification.md` — the engineering-fidelity version of "cover every walk-through"
