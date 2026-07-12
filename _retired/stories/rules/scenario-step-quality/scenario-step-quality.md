---
fidelity: [exploration, specification, engineering]
artifact: [ac, scenario, test]
scanner: scenario-step-quality
kind: quality

---

# Rule: Scenario Step Quality

Steps describe observable behavior in domain language regardless of fidelity.
Each keyword has a specific role — use them correctly at every level.

## Keywords

| Keyword | Role |
|---|---|
| **Given** | Pre-existing state — domain concepts and their values before the action |
| **When** | The action or trigger under test — one per beat |
| **Then** | The primary observable outcome — what becomes true or visible |
| **And** | Additional outcomes in the same beat, or additional state in Given |
| **But** | What does NOT happen — errors, prevention, no persistence |

## DO

- One distinct trigger per When — start a new When only when the actor or trigger genuinely changes
- Chain multiple system reactions with And, not a new When
- Use But for negative conditions explicitly (`But no Order is created`)
- Keep steps readable aloud — a product owner and tester should both understand them

## DON'T

- Use Given in AC steps (exploration) — Given is for specification scenarios
- Use When for micro-steps that are part of the same action — chain with And
- Omit But when an error path has a negative condition worth stating
- Write steps that require code knowledge to understand

## At each fidelity

**Exploration — AC (no Given):**
```
When the Customer submits the Order with valid Payment
Then the Order is confirmed
And the Cart is cleared
But no Order is created if Payment Authorization fails
```

**Specification — scenarios (Given adds state):**
```
Given a **Customer** *Jane Doe* with a valid **DDA Account** *DDA-001*
When the **Customer** applies for a **Payment Product Agreement**
Then the **Payment Product Agreement** status is *Submitted*
And the **Owner** is notified at *john@acme.com*
But no **Payment Product Agreement** is created if the **DDA Account** is *Invalid*
```

**Engineering — test helpers:**
```python
given_customer_with_valid_dda_account(customer="Jane Doe", account="DDA-001")
when_customer_applies_for_agreement(customer="Jane Doe")
then_agreement_status_is(expected="Submitted")
but_no_agreement_created_when_account_invalid()
```
