---
fidelity: [specification, engineering]
artifact: [scenario, test]
scanner: scenario-outline
kind: shape

---

# Rule: Scenario outline structure

When a story has several walk-throughs that share the same shape and differ only in **data values**, they become a single **scenario outline** with an example table — not several near-identical scenarios.

Three things this rule governs:

1. **When to switch to an outline** — the trigger for compression
2. **How the table maps to the parameters** — column headers are placeholders, one row per key example
3. **How the outline becomes a parameterised test** — the engineering-fidelity translation

Background steps that repeat across scenarios have their own place — see the Background section below.

## DO

- Use a scenario outline when **three or more** scenarios share the same Given/When/Then shape and differ only in values
- Name every parameter with a `<placeholder>` and give each `<placeholder>` a column in the example table
- List **key examples**, not every combination — one per equivalence class, one per boundary, one per named domain case
- Put steps that are the same for *every* scenario in a `Background:` block above the scenarios

## DON'T

- Copy-paste three near-identical scenarios when their shape is the same and only the values differ — that's the trigger to outline
- Explode the example table with every combinatoric permutation of inputs — pick the meaningful cases
- Put a step in `Background:` unless *every* scenario in the file uses it — otherwise it's setup for a subset of scenarios and belongs inline
- Use a scenario outline when the shape is not actually shared — different Then means different scenario

## When to switch to an outline

Look at your scenarios for a story. If you see:

```gherkin
Scenario: Payment of 100 is accepted
  Given account balance is 500
  When Customer submits payment of 100
  Then payment is accepted

Scenario: Payment of 500 is accepted
  Given account balance is 500
  When Customer submits payment of 500
  Then payment is accepted

Scenario: Payment of 501 is rejected
  Given account balance is 500
  When Customer submits payment of 501
  Then payment is rejected with reason "insufficient funds"
```

The first two share shape (accept), the third has a different Then (reject). Two shapes → two outlines (or one outline plus one scenario):

```gherkin
Scenario Outline: Payment within balance is accepted
  Given account balance is <balance>
  When Customer submits payment of <amount>
  Then payment is accepted

  Examples:
    | balance | amount |
    | 500     | 100    |  # well within
    | 500     | 500    |  # at the boundary
    | 500     | 499.99 |  # just below the boundary

Scenario Outline: Payment over balance is rejected
  Given account balance is <balance>
  When Customer submits payment of <amount>
  Then payment is rejected with reason "insufficient funds"

  Examples:
    | balance | amount |
    | 500     | 500.01 |  # just above the boundary
    | 500     | 1000   |  # well over
    | 0       | 1      |  # empty balance
```

## Placeholder ↔ column mapping

Every `<placeholder>` in the outline must appear as a column header in the example table. Every column header must appear as a `<placeholder>` in the outline. Names match exactly.

Wrong — placeholder without column:
```
Scenario Outline: …
  When Customer submits payment of <amount> to <recipient>
  …
  Examples:
    | amount |
    | 100    |
```

Wrong — column without placeholder:
```
Scenario Outline: …
  When Customer submits payment of <amount>
  …
  Examples:
    | amount | recipient |
    | 100    | Alice     |
```

Correct:
```
Scenario Outline: …
  When Customer submits payment of <amount> to <recipient>
  …
  Examples:
    | amount | recipient |
    | 100    | Alice     |
```

## Key examples, not exhaustive enumeration

Pick examples that reveal *different behaviours*. Skip examples that only re-prove the same behaviour with different labels.

For a numeric range, pick one **inside**, one **at**, one **just outside** (see `scenario-coverage.md` for the boundary axis). For a categorical field, pick one per named domain case (Gold / Silver / Bronze customer, not "amount = 100, 200, 300").

## Background

When *every* scenario in a file shares the same Given step, factor it into a `Background:` block:

```gherkin
Feature: Payment submission

Background:
  Given the Customer is signed in
  And the Customer has a Verified account

Scenario: … 
```

Rules for `Background:`:

- Only include steps that apply to **every** scenario in the file — if a step applies to some scenarios and not others, it belongs inline in those scenarios
- Background steps are Given only — no When or Then in a Background
- Keep it short (typically 2–4 steps) — a long Background usually signals the scenarios should be split into multiple files

## Engineering translation

A scenario outline compiles to a **parameterised test** (`it.each`, `@pytest.mark.parametrize`, `test.each`). The table becomes the parameter array, the shape stays intact.

```typescript
describe('Payment within balance is accepted', () => {
  it.each([
    { balance: 500, amount: 100 },     // well within
    { balance: 500, amount: 500 },     // at the boundary
    { balance: 500, amount: 499.99 },  // just below the boundary
  ])('balance=$balance, amount=$amount', ({ balance, amount }) => {
    const account = anAccount({ balance });
    const outcome = account.submitPayment(amount);
    expect(outcome).toBe('accepted');
  });
});
```

Rules:

- One `it.each` per scenario outline — not one per row
- The rows in the test array match the rows in the example table, in order
- The parameter names in the test match the column headers exactly

## Cross-references

- `scenario-coverage.md` — the "which examples to pick" logic (boundaries, error paths, channels)
- `real-data-over-invented-values.md` — the values in the table must be real domain values, not placeholders like `foo`, `bar`, `123`
- `tests-implement-specification.md` — the engineering-fidelity version of the outline-to-test mapping
