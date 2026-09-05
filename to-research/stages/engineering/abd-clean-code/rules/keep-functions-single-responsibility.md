---
scanner: function_single_responsibility_scanner.py
---

### Rule: Keep Functions Single Responsibility

Functions do one thing. No hidden side effects, no mixing business logic with I/O or mutations.

#### DO

- Separate pure calculations from orchestration.
- Each function has one reason to change.
- Side effects live in dedicated orchestration functions.

```python
def subtotal(items: list) -> float:
    return sum(i.price * i.qty for i in items)  # pure calculation

def checkout(user, cart, services):
    sub = subtotal(cart.items)                  # calls pure helper
    services.logger.info('checkout', extra={'user_id': user.id})
    return sub
```

```javascript
export function subtotal(items) {
  return items.reduce((s, i) => s + i.price * i.qty, 0);  // pure calculation
}

export async function checkout({ user, cart, services }) {
  const sub = subtotal(cart.items);             // calls pure helper
  services.logger.info('checkout', { userId: user.id });
  return sub;
}
```

#### DON'T

- Mix business logic with logging, I/O, or mutations in the same function.

```python
def full_name(user):
    print("User:", user.id)       # WRONG: hidden side effect in calculation
    metrics.append(user.id)       # WRONG: state mutation in pure function
    return f"{user.first} {user.last}"
```

```javascript
function fullName(user) {
  console.log('User:', user.id);  // WRONG: hidden side effect
  return `${user.first} ${user.last}`;
}
```
