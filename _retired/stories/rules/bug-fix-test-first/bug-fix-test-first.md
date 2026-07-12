---
fidelity: [engineering]
artifact: [test]
scanner: bug-fix-test-first
kind: quality

---

# Rule: Bug-fix test first

When a bug is found in production or in review, the fix workflow is:

1. **Add the walk-through** — the scenario (or example row) that describes the bug's observable behaviour, phrased as the *correct* outcome. Cite the bug source.
2. **Write the failing test** from the walk-through. Confirm it fails against current code with the expected wrong behaviour.
3. **Fix the code** until the test passes.
4. **Verify the walk-through** — check other walk-throughs still pass; check the walk-through itself accurately describes the fixed behaviour.

Never fix the code first. Never write a test that codifies the buggy behaviour.

## DO

- Add or update the scenario that names the observed bug behaviour, with citation to the bug report / ticket / observation
- Confirm the test fails with a message that clearly points at the wrong behaviour, before touching the code
- Keep the walk-through visible in the specification even after the fix — the bug case is now a permanent coverage case
- If the bug reveals a missing story or activity, revise the map (see `right-size-story-nodes.md`, `revising-story-map.md`)

## DON'T

- Ship a fix without a walk-through — this is how bugs re-appear
- Write a test that just captures the current (fixed) code and calls it done — the test must have first *failed* on the bug
- Convert the bug into a comment or a code guard without a walk-through — the specification never learns about the bug
- Delete the walk-through after the fix — it stays as coverage against regression

## The four-step workflow

### 1. Add the walk-through

The walk-through describes the **correct** behaviour, not the wrong one. Cite the bug:

```gherkin
Scenario: Payment is rejected when Amount is exactly zero
  # Bug: BUG-1234 — zero-amount payments were being accepted and recorded
  # Reported: 2026-06-30, Ops team observation
  Given a Customer with an active Account
  When the Customer submits a Payment of 0.00
  Then the Payment is rejected
  And the rejection reason names the minimum Amount
```

If the bug is a scenario-outline row rather than a whole scenario, add the row with a comment:

```gherkin
  Examples:
    | amount | expected     | note                     |
    | 100    | accepted     |                          |
    | 0.01   | accepted     | minimum                  |
    | 0.00   | rejected     | BUG-1234 fixed 2026-07-02 |
```

### 2. Write the failing test

Translate the walk-through into a test (see `tests-implement-specification.md`). Run it against the current code — it must fail. Note the failure output:

```
FAIL: Payment is rejected when Amount is exactly zero
  Expected outcome.status to be 'rejected', received 'accepted'
```

If the test passes on unchanged code, either the bug is already fixed, or the test doesn't actually exercise the bug — refine before proceeding.

### 3. Fix the code

Modify production code until the test passes. Do not modify the test to make it pass. Do not modify other tests unless the fix legitimately changes their expected behaviour (in which case the *walk-throughs* for those scenarios need to change too, not just the tests).

### 4. Verify

Run the full test suite. Confirm:

- The new bug-fix test passes
- No previously-passing test now fails without a corresponding walk-through update
- The walk-through's Then wording matches the actual fixed behaviour — if the fix subtly changed the reason string, update the walk-through

## When the bug is a walk-through / specification error

Sometimes the "bug" turns out to be that the specification was wrong. Same workflow:

1. Update the walk-through to the *now-correct* behaviour, citing the source of the correction
2. Write a test for the corrected behaviour — it may pass immediately if the code was right and the spec was wrong
3. Update other affected walk-throughs and tests
4. Cite: `_Corrected: 2026-07-02 per <source>. Previously: <old wording>_`

## Cross-references

- `tests-implement-specification.md` — the walk-through-to-test translation
- `scenario-coverage.md` — new bug cases become coverage cases
- `document-observed-quirks.md` — bugs that can't be fixed immediately become documented quirks
- `right-size-story-nodes.md` — a bug that reveals a missing story triggers map revision
