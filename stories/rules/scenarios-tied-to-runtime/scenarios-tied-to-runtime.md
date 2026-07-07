---
fidelity: [specification, engineering]
artifact: [scenario, test]
scanner: scenarios-tied-to-runtime
kind: quality

---

# Rule: Scenarios tied to runtime

By specification fidelity, scenarios must reference **real runtime shapes** — the schemas, service interactions, and stub structures that will actually run. Scenarios written in vacuum drift from the system and quietly become fiction.

Three ties enforced:

1. **Schema tie** — every value that maps to a typed field references that type; scenario values validate against the schema
2. **Service-interaction tie** — every `When` that calls a service and every `Then` that observes a service response uses the service's actual shape (endpoint, method, response envelope)
3. **Stub-data tie** — stubs used by scenarios and tests share one source of truth for shape and identity, so scenarios and stubs cannot drift apart

## DO

- Reference the schema (`schemas/payment.json`, `PaymentRequest` type, DB DDL) beside any scenario that uses a typed value
- Use the real endpoint / method / event name in `When` and `Then` steps that cross a service boundary
- Store stub data in one place; both scenarios and tests read from it — see the stub-data-sync section below
- When a scenario uses a value that must validate, run it through the schema and cite the result

## DON'T

- Invent field names or shapes in a scenario that don't exist in the actual schema
- Describe a service call using a name the code doesn't use (`the payment API` when the endpoint is `POST /v2/transactions`)
- Duplicate stub data — scenarios saying `amount: 100` and tests using `amount: 250` for the "same" case is drift
- Wait until engineering fidelity to check the tie — by then, scenarios have drifted and rewriting them is expensive

## Schema tie

Every typed value in a scenario references a real schema. The scenario cites the schema location once at the top:

```gherkin
Feature: Payment submission
  Schema: schemas/payment_request.json → PaymentRequest

Scenario: Customer submits valid payment
  Given a Customer with an active Account
  When the Customer POSTs to /v2/payments with:
    | field       | value              |
    | amount      | 250.00             |
    | currency    | USD                |
    | recipient   | acc_xyz            |
    | idempotency | key-2026-07-02-001 |
  Then the response body matches PaymentResponse with status "accepted"
```

Rules:

- Field names in the table match the schema field names exactly
- Types match — `250.00` is a decimal, not the string `"250.00"`, if the schema says decimal
- Enums use the exact string values the schema allows

When a schema-validated value fails validation, that's a **specification-fidelity failure** — either the schema is wrong or the scenario invented a value.

## Service-interaction tie

Steps that cross a service boundary must use the real interaction shape.

| Boundary | Scenario step includes |
|---|---|
| HTTP endpoint | Method + path (`POSTs to /v2/payments`) |
| Event | Event name (`emits event PaymentSubmitted`) |
| Message queue | Queue + message shape (`enqueues to payments-in with body matching PaymentEnvelope`) |
| DB call | Table + operation (`inserts into payments`) — only when persistence is the observed outcome |

Wrong — vague:
```
When the Customer submits the payment
Then the payment service accepts it
```

Correct — tied to runtime shape:
```
When the Customer POSTs to /v2/payments with a valid PaymentRequest
Then the response is 201 Created with a PaymentResponse body containing a confirmation_number
And an event PaymentAccepted is emitted with the confirmation_number
```

## Stub-data tie

Stubs (fake data used to satisfy dependencies during a walk-through or test) live in **one place per bounded context**. Both scenarios and tests read from the same source:

```
stories/
  payments/
    stubs/
      customers.yaml     # aliceCustomer, bobCustomer, frozenCustomer
      accounts.yaml      # aliceCheckingAccount, aliceSavingsAccount
      payments.yaml      # small, atLimit, overLimit
    scenarios/
      submit-payment.feature
    tests/
      submit-payment.test.ts
```

The scenario cites the stub by name; the test loads the same file:

```gherkin
Scenario: Payment at daily Limit is accepted
  Given customer aliceCustomer with account aliceCheckingAccount
  When aliceCustomer submits payment atLimit
  Then the payment is accepted
```

```typescript
import { customers, accounts, payments } from './stubs';

it('at daily Limit is accepted', () => {
  const outcome = payments.submit(customers.aliceCustomer, accounts.aliceCheckingAccount, payments.atLimit);
  expect(outcome.status).toBe('accepted');
});
```

When the stub file changes, both the scenario and the test see the new value — drift is impossible.

## Where the tie is checked

- **Specification fidelity:** the scenario cites the schema / endpoint / event; a mechanical schema-validation pass verifies every table value validates
- **Engineering fidelity:** tests import stubs by name (not literal values); a scanner verifies scenario stub references match stub file identifiers (see `scanners/scenarios-tied-to-runtime-scanner.py`)

## Cross-references

- `real-data-over-invented-values.md` — the values in the schema table must be real domain values
- `scenario-outline-structure.md` — outline example rows follow the same schema tie as inline scenarios
- `artifacts-mirror-story-hierarchy.md` — stub files live in the folder that mirrors the story map
