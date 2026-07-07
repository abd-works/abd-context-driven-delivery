---
fidelity: [engineering]
artifact: [test]
scanner: tests-implement-spec
kind: shape

---

# Rule: Tests implement the specification

At engineering fidelity, the **tests are the specification, running**. Each test case corresponds to exactly one scenario (or one example row of a scenario outline). Test wording matches scenario wording. Test file layout mirrors story-map layout. No walk-through is unimplemented; no test is un-walk-throughed.

Four ties enforced:

1. **One test per scenario / row** — a scenario becomes one `it` / `test` case; an outline row becomes one row in `it.each`
2. **Test name = scenario name** — the `it` / `test` string is the scenario title, verbatim
3. **Describe = story** — the enclosing `describe` names the story, matching the story-map folder / section
4. **Steps match** — the test's Given / When / Then structure mirrors the scenario's steps in order

This is what makes the test file readable to someone who has only ever read the scenarios — and vice versa.

## DO

- Put one `it` / `test` block per scenario in the corresponding `scenarios/` folder
- Use the scenario title *verbatim* as the `it` string
- Group tests in `describe(<story-name>)` blocks that match the story map exactly (see `artifacts-mirror-story-hierarchy.md`)
- Use Given/When/Then helpers or comment markers so the test's shape is visible

## DON'T

- Rename the scenario when translating it into a test — the two must match word-for-word
- Combine two scenarios into one test — one test per scenario
- Add tests for behaviour that has no walk-through — add the walk-through first (see `bug-fix-test-first.md` for the bug case)
- Organise tests by class or by internal module — organise by story (see `artifacts-mirror-story-hierarchy.md`)

## One test per scenario / row

For each scenario, exactly one `it` block. For each row of a scenario outline, exactly one entry in `it.each`.

```gherkin
Scenario Outline: Payment within balance is accepted
  Examples:
    | balance | amount |
    | 500     | 100    |
    | 500     | 500    |
    | 500     | 499.99 |
```

```typescript
describe('Customer submits payment from web', () => {
  it.each([
    { balance: 500, amount: 100 },
    { balance: 500, amount: 500 },
    { balance: 500, amount: 499.99 },
  ])('Payment within balance is accepted (balance=$balance, amount=$amount)', ({ balance, amount }) => {
    // Given
    const account = anAccount({ balance });
    // When
    const outcome = account.submitPayment(amount);
    // Then
    expect(outcome.status).toBe('accepted');
  });
});
```

## Test name = scenario name

The `it` / `test` string is the scenario title. Not a paraphrase, not a translation, not a "cleaned-up" version.

Wrong:
```typescript
it('accepts a payment when the balance is enough', ...)
```

Correct (scenario is titled `Payment within balance is accepted`):
```typescript
it('Payment within balance is accepted', ...)
```

Where a scenario outline has parameterised rows, append the parameter values to the title:

```typescript
it('Payment within balance is accepted (balance=500, amount=100)', ...)
```

## Describe = story

The `describe` name matches the story name in the map. When stories nest (sub-story under a story), nest `describe` blocks:

```typescript
describe('Customer submits payment from web', () => {
  describe('with valid inputs', () => {
    it('Payment within balance is accepted', ...);
    it('Payment at daily Limit is accepted', ...);
  });
  describe('with invalid inputs', () => {
    it('Payment over balance is rejected', ...);
    it('Payment over daily Limit is rejected', ...);
  });
});
```

`describe` blocks that don't correspond to map nodes (e.g. `describe('edge cases')`) are a smell — the map probably needs a sub-story.

## Steps match

The test's structure mirrors the scenario's Given / When / Then structure, in order. Use one of:

- Explicit Given/When/Then helpers (see abd-bdd-development for helper patterns)
- `// Given` / `// When` / `// Then` comment markers with the same phrasing as the scenario
- Named blocks / arrange-act-assert with domain-language names

```typescript
it('Payment over daily Limit is rejected', () => {
  // Given a Customer with daily Limit 1000
  const customer = aCustomer({ dailyLimit: 1000 });
  // And previous Payments totalling 950 today
  customer.recordPayment(950, today());
  // When the Customer submits a Payment of 100
  const outcome = customer.submitPayment(100, today());
  // Then the Payment is rejected
  expect(outcome.status).toBe('rejected');
  // And the rejection reason names the daily Limit
  expect(outcome.reason).toContain('daily Limit');
});
```

## Coverage completeness

A story has full engineering coverage when:

- Every scenario in `stories/…/<story>/scenarios/` has one `it` in the story's test file
- Every row of every scenario outline has one row in the corresponding `it.each`
- No `it` block exists that doesn't correspond to a scenario (missing walk-through → add walk-through)

Missing tests are a gap (see `document-observed-quirks.md`). Missing scenarios for existing tests are also a gap — walk-through comes first.

## Cross-references

- `artifacts-mirror-story-hierarchy.md` — the folder / describe layout this rule sits inside
- `scenario-coverage.md` — the specification-side rule that says every walk-through must exist
- `scenario-outline-structure.md` — how outlines map to `it.each`
- `assertions-against-real-behavior.md` — how each `it` body's assertions must be shaped
- `bug-fix-test-first.md` — how newly-discovered bugs enter this system (walk-through first, test next)
