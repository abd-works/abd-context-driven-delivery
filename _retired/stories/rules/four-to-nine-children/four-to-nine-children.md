---
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: [story-map, thin-slice, story-scenarios, story-tests]
scanner: four-to-nine-children
kind: shape

---

# Rule: 4–9 children per parent

Every parent in the story hierarchy should have **4–9 direct children**. Fewer than 4 signals under-exploration or a parent that isn't really a parent; more than 9 signals a parent that should split.

The band comes from short-term memory heuristics — a reviewer can hold 4–9 items in mind at once. It applies to *every* level of the hierarchy, not just acceptance criteria.

## Where it applies

| Fidelity | Parent | Children counted |
|---|---|---|
| shaping | outcome | activities |
| shaping | activity | (n/a until discovery) |
| discovery | activity | stories |
| discovery | thin-slice increment | stories in the increment |
| exploration | story | acceptance criteria (`When` / `And` beats) |
| specification | story | scenarios (main flow + variations) |
| specification | scenario | steps (Given/When/Then/And/But lines) |
| specification | scenario outline | example rows in the table |
| engineering | story | test cases (`it` / `test` blocks) |
| engineering | test file | assertions per test case |

## Bands

- **4–9** — target
- **3 or 10** — warning; look for a missing child or a candidate to move up/down
- **≤2 or ≥11** — error; the parent is either not really a parent or must split

Under-count and over-count are equally bad. A story with 2 scenarios is under-explored; a story with 12 scenarios is doing the job of three stories.

## DO

- Split a parent that grows past 9 by finding the natural sub-grouping (a sub-activity, a sub-story, a sub-scenario)
- Expand an under-populated parent by asking what's missing — happy path, errors, edges, alternates
- Collapse a lone child up into its parent when it turns out there's nothing to group

## DON'T

- Pad with trivial or redundant children to hit the band
- Let a monolithic parent stay monolithic because splitting it "feels like work"
- Leave a single-child parent standing — either it's a false parent or it's under-explored

## At each fidelity

**Shaping — outcome → activities:**
```
Wrong — 2 activities under one outcome
Outcome: Move money
  Activity: Send payment
  Activity: Receive payment

Correct — 5 activities
Outcome: Move money
  Activity: Initiate payment
  Activity: Authorise payment
  Activity: Route payment
  Activity: Settle payment
  Activity: Reconcile payment
```

**Discovery — activity → stories:**
```
Wrong — 12 stories under one activity (should split the activity)
Activity: Initiate payment
  Story 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

Correct — split into two activities of 6 each, or collapse repetition
```

**Exploration — story → acceptance criteria:**
```
Wrong — 2 AC beats
When the Customer submits a Payment
Then the Payment is queued

Correct — 5 AC beats covering happy path, error, edge
When the Customer submits a Payment
And the Amount is within the daily Limit
Then the Payment is queued
And the Confirmation Number is returned
But when the Amount exceeds the daily Limit the Payment is rejected
```

**Specification — scenario → steps:** same 4–9 rule applied to Given/When/Then/And/But lines within a single scenario.

**Engineering — story → tests:** each story's test file should have 4–9 `it` / `test` cases mirroring its scenarios.

## Cross-references

- Splits caused by this rule should trigger `revising-story-map.md` — the map changes when a parent breaks the band
- `atomic-deltas-over-repetition.md` — when children look repetitive, the count is padded, not real
