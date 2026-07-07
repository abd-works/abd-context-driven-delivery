---
fidelity: [engineering]
artifact: [test]
scanner: real-assertions
kind: quality

---

# Rule: Assertions against real behavior

Every test's assertions must be:

1. **Full-result** — assert on the whole observable outcome, not a fragment that happens to be convenient
2. **Real-implementation** — call production code directly and assert on what production code actually returns, not a mock's return value
3. **Public-surface only** — assert on domain-observable state, never on internal / private fields

If any of the three fails, the test is testing itself, or the mock, or an accident of implementation — not the behaviour the story specifies.

## DO

- Assert on the full domain object that the operation produces, not one field of it
- Call the production code path the scenario describes — the same entry point a real caller uses
- Assert against public / documented state (`status`, `confirmationNumber`, `notification.sentTo`)
- Include the *reason* / *message* the domain produces on failure paths, not just the status

## DON'T

- Assert only that the operation "didn't throw" — non-throw is not an outcome
- Assert on mock invocations (`mock.calledWith(...)`) as the primary assertion — mocks verify interactions, not outcomes
- Reach into private fields (`._status`, `__internal`) — if the outcome isn't public, either the outcome is wrong or the surface needs to expose it
- Split the outcome across many one-field assertions when a single full-object assertion says it clearer

## Full-result assertions

Compare the whole observable result, not a fragment.

Wrong — one field:
```typescript
expect(outcome.status).toBe('accepted');
```

Better — whole outcome:
```typescript
expect(outcome).toEqual({
  status: 'accepted',
  confirmationNumber: expect.stringMatching(/^cn_/),
  amount: 250.00,
  currency: 'USD',
});
```

The full-object assertion:

- Fails loudly if a new field is added and not asserted
- Documents *all* the observable outcomes in one place
- Reads as the domain contract, not a debugging snippet

For fields whose exact value is unpredictable (IDs, timestamps), use matchers (`expect.stringMatching`, `expect.any(Date)`) — but keep them *in* the full-object assertion.

## Real-implementation

The test calls the production code path the scenario describes:

Wrong — asserting on a mock:
```typescript
it('Payment is rejected when over daily Limit', () => {
  const paymentServiceMock = jest.fn().mockReturnValue({ status: 'rejected' });
  const outcome = paymentServiceMock({ amount: 2000 });
  expect(outcome.status).toBe('rejected');  // testing the mock
});
```

Correct — real production call:
```typescript
it('Payment is rejected when over daily Limit', () => {
  const customer = aCustomer({ dailyLimit: 1000 });
  customer.recordPayment(950, today());
  const outcome = customer.submitPayment(100, today());  // real code
  expect(outcome).toEqual({
    status: 'rejected',
    reason: 'daily Limit exceeded',
    dailyLimit: 1000,
    attempted: 100,
    alreadyUsedToday: 950,
  });
});
```

Mocks are legitimate only at genuine external boundaries (network / third-party service / clock / random). See `abd-clean-code` mocking rules for the boundary discussion — this rule only cares that the *assertion* is on real output, not mock output.

## Public-surface only

Assert only on state the domain exposes as public. Never on private / underscore-prefixed / internal fields.

Wrong — internal state:
```typescript
expect(agreement._status).toBe('SUBMITTED');
expect(agreement.__internal.dbRow.status_code).toBe(1);
```

Correct — public observable state:
```typescript
expect(agreement.status).toBe('Submitted');
expect(owner.notificationSentTo).toBe(owner.contactEmail);
```

If the outcome the scenario describes isn't reachable through the public surface, that's a *surface* problem, not a test problem — the domain object needs to expose it. Fix the surface, then the test.

## Failure paths — assert the reason, not just the status

Failure outcomes must include *why*, using domain wording:

Wrong:
```typescript
expect(outcome.status).toBe('rejected');
```

Correct:
```typescript
expect(outcome).toEqual({
  status: 'rejected',
  reason: 'daily Limit exceeded',
  dailyLimit: 1000,
  attempted: 100,
});
```

The reason text uses domain terms (`daily Limit`, not `LIMIT_EXCEEDED_CODE_42`). It matches the scenario's Then step:

```gherkin
Then the payment is rejected
And the rejection reason names the daily Limit
```

## Assertion shape summary

| Aspect | Wrong | Correct |
|---|---|---|
| Scope | one field | full result object |
| Source | mock return value | real production call |
| Surface | private / internal | public / documented |
| Failure info | status only | status + reason + relevant context |

## Cross-references

- `behavioral-observable-outcomes.md` — the underlying principle that "observable" outcomes are what get asserted
- `tests-implement-specification.md` — the wider rule about how each test relates to its scenario
- `real-data-over-invented-values.md` — the values compared in assertions come from real domain examples, not `foo` / `bar`
- `scenarios-tied-to-runtime.md` — asserting on schema-matching shapes rather than invented shapes
