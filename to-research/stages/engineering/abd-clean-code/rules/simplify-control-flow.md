---
scanner: simplify_control_flow_scanner.py
---

### Rule: Simplify Control Flow

Use guard clauses to reduce nesting. Return early for invalid or boundary conditions.

#### DO

- Guard clauses at the top of the function.
- Flat structure, maximum 2 levels of nesting.

```python
def price_for(user, plan):
    if not user or not plan: return 0       # guard clause
    if user.is_student: return plan.base * 0.5
    return plan.base
```

```javascript
function priceFor(user, plan) {
  if (!user || !plan) return 0;             // guard clause
  if (user.isStudent) return plan.base * 0.5;
  return plan.base;
}
```

#### DON'T

- Nest if statements 3 or more levels deep.
- Use else when an early return makes it unnecessary.

```python
def price_for(user, plan):
    if user is not None:          # WRONG: deep nesting
        if plan is not None:
            if user.is_student:
                return plan.base * 0.5
            else:
                return plan.base
    return 0
```

```javascript
function priceFor(user, plan) {
  if (user) {                     // WRONG: deep nesting
    if (plan) {
      if (user.isStudent) return plan.base * 0.5;
      return plan.base;
    }
  }
  return 0;
}
```
