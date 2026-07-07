---
fidelity: [exploration, specification]
artifact: [story-scenarios]
scanner: atomic-deltas
kind: quality

---

# Rule: Atomic Deltas Over Repetition

State the general case **once**; follow-on scenarios and AC describe only the
**delta** from it — the error, the boundary, the alternate path. Do not repeat
the happy-path steps across every scenario.

## DO

- Write the happy path in full
- For each follow-on: write only the steps that differ (the changed `When`, the
  changed `Then`, the new `But`)
- Assume the reader has read the happy path first

## DON'T

- Copy the entire happy path into each error scenario with one line changed
- Restate identical `Given` blocks across scenarios (use `Background` when three
  or more scenarios share the same setup)
- Duplicate outcomes that hold across all scenarios

## At each fidelity

**Exploration — AC:**
```
# Happy path (full)
When the Customer submits the Order with valid Payment
Then the Order is confirmed
And the Cart is cleared

# Error path (delta only)
When the Payment Authorization fails
Then the Order is not confirmed
But the Cart is retained
```

**Specification — scenarios:**
Use `Background` for shared `Given` across three or more scenarios. Each
scenario states only the steps that differ from the happy path.
