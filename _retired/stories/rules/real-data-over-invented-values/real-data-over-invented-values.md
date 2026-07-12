---
fidelity: [specification, engineering]
artifact: [scenario, test]
scanner: real-data
kind: quality

---

# Rule: Real Data Over Invented Values

Example values in scenario tables and test fixtures must be realistic — drawn
from source material, domain model, or real system data. Not `$1.00`, `John`,
`foo`, `test123`, or `example`.

## DO

- Use values that could appear in production: real amounts, real statuses, real identifiers
- Draw values from source material when available (workshop data, API samples, requirements)
- Use canonical named data sets — reuse the same fixtures across tests for consistency
- Format values as the domain formats them: `$10,000.00 USD`, not `10000`
- **For existing systems: read the contract schemas before choosing values** — check regex, min/max, allowed characters, required fields, enum values, and date/range constraints. A value that violates the schema produces a test that fails for the wrong reason (silent form rejection, cryptic 4xx, invalid enum).

## DON'T

- Invent placeholder values that would fail real validation
- Use generic names (`User1`, `Account123`) when domain names are available
- Use values that violate system constraints (wrong format, out of range, invalid enum)
- Denormalize tables by repeating values instead of linking via FK columns

## At each fidelity

**Specification — example tables:**
```
# Wrong — invented values
| customer_name | amount  |
| John          | 1.00    |

# Correct — realistic domain values
| customer_id | customer_name | payment_amount | currency |
| USR-001     | Jane Doe      | 10000.00       | USD      |
| USR-002     | Bob Smith     | 500000.01      | USD      |
```

**Engineering — fixtures:**
```python
# Wrong
customer = Customer(name="test")
payment = Payment(amount=1)

# Correct — matches spec example table
JANE_DOE = Customer(id="USR-001", name="Jane Doe")
WIRE_PAYMENT_VALID = WirePayment(amount=Decimal("10000.00"), currency="USD")
WIRE_PAYMENT_OVER_LIMIT = WirePayment(amount=Decimal("500000.01"), currency="USD")
```
