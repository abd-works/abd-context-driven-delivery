---
rule: every-describe-has-behavior
severity: warning
---
# Every Describe Has Behavior

No describe block should be a dead end. Every grouping must have at least one `should` leaf beneath it. An empty grouping usually means the domain concept is unclear, misplaced, or that discovery is incomplete.

**DO:** Ensure every describe block has at least one behavior leaf.

```
Payment
  Card processing
    should authorise a payment with valid card details
    should decline a card with insufficient funds
```

**DO NOT:** Leave describe blocks empty or with only nested describes and no leaf behaviors.

```
Payment
  Card processing          ← no leaves under this
    Authorisation          ← no leaves under this either
```

- Example (wrong): `Payment > Card processing` with no `should` lines
- Example (correct): `Payment > Card processing > should authorise a payment with valid card details`
