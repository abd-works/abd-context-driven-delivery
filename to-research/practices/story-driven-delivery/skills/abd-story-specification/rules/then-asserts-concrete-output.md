---
scanner: then-asserts-concrete-output
---

# Rule: Then steps state the behavior AND assert concrete expected values

**Scanner:** `scanners/then-asserts-concrete-output-scanner.py` — **`ThenAssertsConcreteOutputScanner`**

Every **Then** or **And** step after Then that references a computation, aggregation, transformation, or display of domain data MUST do two things:

1. **State the behavior** — what the system does (groups, sums, filters, transitions, formats)
2. **Assert concrete values** — via `{tokens}` resolved from an example table that prove the behavior is correct

The specification IS the test. If a Then step only describes logic without assertable values, there is nothing to verify. If it only states values without describing what the system did, there is no behavior under test.

## Why

- "Then the system displays amounts grouped by Currency" describes logic but gives no way to verify it. **Violation: no values.**
- "Then the group row shows {account_count} and {total_available}" states values but not what the system did with them. **Better but incomplete.**
- "Then operating Accounts are grouped by AccountType {accountType} and Currency {currency}, showing account count {account_count} and total AvailableBalance {total_available}" describes the behavior AND asserts on the values that prove it. **Correct.**

## DO

- Write Then steps that say WHAT the system does (the verb: groups, calculates, transitions, filters) followed by the expected output values as `{tokens}`.
- Back every `{token}` in a Then step with a concrete value in an example table row.
- When the output is derived from inputs (sum, count, grouping, status transition, formatted display), add an **(expected output)** table that shows the concrete result.
- Name output tables with the domain concept followed by `(expected output)` when the same concept also appears as an input table.

```text
# RIGHT — describes behavior AND asserts concrete values

Scenario Outline: Account type summary displays grouped totals
  When the FinanceUser {user_name} views the DailyCashPosition home screen
  Then operating Account records are grouped by AccountType {accountType} and Currency {currency}
  And the group row displays account count {account_count} and total AvailableBalance {total_available}

### DailyCashPosition (expected output):
| scenario | accountType | currency | account_count | total_available |
| type summary | Operating | USD | 2 | 1,700,000.00 |
| type summary | Operating | CAD | 1 | 875,000.00 |
```

## DON'T

- Write a Then step that only describes behavior without any `{token}` or concrete `*value*` to assert on — that is a requirement statement, not a specification.
- Write a Then step that only has values without stating what the system did — that is data without context.
- Use abstract verbs ("reflects", "shows the total", "displays grouped") as the entire assertion without any assertable tokens or values.
- List field names without their expected values — "Then the detail shows: PaymentStatus, amount, date" is a field inventory, not a test.

```text
# WRONG — only logic, no values to assert
Scenario Outline: Multiple currencies display grouped
  Then the DailyCashPosition displays amounts grouped by Currency {currency} for each Account {name}

# WRONG — field inventory, no values
Scenario: Status detail
  Then the detail view shows: PaymentStatus, payment type, amount, EffectiveDate

# WRONG — abstract assertion
Scenario: Badge reflects count
  Then the badge reflects the total count including that submission
```

## Scanner heuristic

The scanner flags **Scenario Outline** Then/And steps that contain NONE of: a `{token}`, a concrete `*italic*` value, or a quoted literal string — because such steps cannot be asserting on anything testable.
