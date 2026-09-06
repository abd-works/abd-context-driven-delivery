# Rule: Validate Scenario Values Against Schema

When specifying an **existing system**, every concrete value chosen for a scenario must satisfy the constraints the system already enforces. Invalid values produce tests that fail silently — forms don't submit, APIs return cryptic 4xx errors, dialogs "stay open" with no visible cause.

## DO

- **Read the contract schema** before choosing input values. Check regex patterns, min/max, required fields, and enum constraints:

```
# Before writing: "When operator submits batch with prefix E2E-BATCH"
# Read: packages/contracts/src/vouchers/create-voucher-batch.ts
#   → BATCH_PREFIX_PATTERN = /^[A-Za-z0-9]+$/   ← no hyphens allowed!
# Fix: "When operator submits batch with prefix E2EBATCH"
```

- **Check date constraints** against the domain validators. If campaigns have start/end windows, scenario dates must fall within them:

```gherkin
# DO — date within the seeded campaign range
Given a campaign "Summer 2026" running from 2026-06-01 to 2099-12-31
When the operator creates a voucher with startAt 2026-07-01

# DON'T — date after campaign end; API returns 409 and test fails mysteriously
Given a campaign "Summer 2026" running from 2026-06-01 to 2026-08-31
When the operator creates a voucher with startAt 2027-01-01
```

- **Verify required fields** — if a form requires a discount value but the scenario doesn't mention it, the implementation will reject the submission silently.

## DON'T

- **Don't choose values based on what "looks right" without checking the schema:**

```gherkin
# WRONG — chose prefix with hyphens because it looks like a code format
When operator generates a batch with prefix "E2E-BATCH-" and quantity 5

# The regex /^[A-Za-z0-9]+$/ rejects it. Form never submits. Dialog stays open.
# No error message. No stack trace. 30 minutes of debugging.
```

- **Don't assume "any valid-looking date" works** — service validators may check against campaign boundaries, subscription periods, or business rules.

- **Don't assume defaults are safe** — `NaN`, empty string, or `undefined` may fail validation when a numeric field has `.min(1)`.

## Where to look

| Stack layer | What defines the constraints |
|---|---|
| Form validation | Zod schema passed to `useForm({ resolver })` — check the form schema, not the API schema |
| API validation | DTO schema or Zod schema used by the controller pipe |
| Service rules | Domain validators called by the service (e.g. `validateVoucherRules`) |
| Database | Prisma schema `@unique`, `@default`, field types |

## When this rule doesn't apply

In a **new system** (spec-first mode), the schema doesn't exist yet. You are free to choose any values — the schema will be built to accept them. This rule only applies when the system already exists and the constraints are already defined.
