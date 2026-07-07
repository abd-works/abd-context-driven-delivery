---
fidelity: [shaping, discovery, engineering]
artifact: [story-map, thin-slice, story-tests]
scanner: right-size
kind: quality

---

# Rule: Right-size story nodes

Every node in the story hierarchy — outcome, activity, story, test case — must hold **one concern**. Not fewer (superficial trivial nodes), not more (monolithic nodes covering distinct mechanics).

Two failure modes to detect and fix:

1. **Merged distinct mechanics** — two things that behave differently share one node. Split.
2. **Superficial repetition** — several nodes are trivial variants of the same behavior. Merge.

This rule pairs with `four-to-nine-children.md` (which counts children) — right-sizing is what you *do* when the count is off.

## DO

- Split a node when it covers **two distinct mechanics** (different actors, different data, different failure modes, different channels)
- Merge nodes that are **trivial variants of one behavior** (naming difference only, same actor and same reaction)
- Expand under-explored nodes by asking what happy path / error / boundary / channel is missing
- When splitting a story, check whether the split reveals a new *activity* — the map may need to grow up, not just sideways

## DON'T

- Merge two stories because they *look* similar in name — check the mechanics
- Keep a story that names an outcome the parent activity already implies
- Leave a node under-populated because "we'll add more later" — either add now or drop the parent
- Split a node purely to hit a child-count band (see `four-to-nine-children.md`)

## Distinguishing marker: distinct mechanics vs. superficial variants

A mechanic is distinct if **any of these** are true:

- Different **actor** performs the action
- Different **domain entity** is the target
- Different **failure mode** applies
- Different **channel** (web, API, mobile) requires different steps
- Different **downstream side effect** (different notification, different audit trail)

If none apply, the variation is superficial and should merge.

## At each fidelity

**Shaping — outcomes / activities:**
```
Wrong — superficial split
Outcome: Move money
  Activity: Send small payment
  Activity: Send medium payment
  Activity: Send large payment
(size is not a distinct mechanic here)

Correct — merged
Outcome: Move money
  Activity: Send payment
```

**Discovery — stories under an activity:**
```
Wrong — merged distinct mechanics
Activity: Submit payment
  Story: Customer submits payment (from web or API, valid or invalid)

Correct — split by mechanic
Activity: Submit payment
  Story: Customer submits payment from web
  Story: Customer submits payment from partner API
  Story: System rejects payment when daily limit exceeded
```

```
Wrong — superficial variants
Activity: Submit payment
  Story: Customer submits payment on Monday
  Story: Customer submits payment on Tuesday
  Story: Customer submits payment on Wednesday

Correct — merged
Activity: Submit payment
  Story: Customer submits payment on any business day
```

**Engineering — test cases:**
```
Wrong — superficial parameterisation as separate tests
it('submits payment for $10')
it('submits payment for $20')
it('submits payment for $30')

Correct — one parameterised test (see scenario-outline-structure.md)
it.each([10, 20, 30])('submits payment for $%d', ...)
```

## Cross-references

- `four-to-nine-children.md` — the count band that triggers a right-size review
- `atomic-deltas-over-repetition.md` — repetition in *step wording* is the sentence-level version of superficial-variant nodes
- `revising-story-map.md` (behavior) — splits/merges may cascade upward
