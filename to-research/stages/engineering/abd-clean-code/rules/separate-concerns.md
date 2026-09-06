---
scanner: separate_concerns_scanner.py
---

### Rule: Separate Concerns

Keep pure calculations separate from side effects. Logging, I/O, and mutations belong in dedicated functions.

#### DO

- Pure functions return values without touching external state.
- Side effects are isolated in dedicated orchestration functions.

```python
def full_name(user) -> str:
    return f"{user.first} {user.last}"          # pure: no side effects

def greet(user, logger) -> str:
    logger.debug("Greeting", extra={"user_id": user.id})
    return f"Hello, {full_name(user)}!"
```

```javascript
function fullName(user) {
  return `${user.first} ${user.last}`;          // pure: no side effects
}

function greet(user, { logger }) {
  logger.debug({ userId: user.id });
  return `Hello, ${fullName(user)}!`;
}
```

#### DON'T

- Log, mutate, or perform I/O inside a calculation function.

```python
def discount(total):
    d = total * 0.1 if total > 100 else 0
    logging.info("discount=%s", d)              # WRONG: side effect in calculation
    return d
```

```javascript
function discount(total) {
  const d = total > 100 ? total * 0.1 : 0;
  console.log('discount:', d);                  // WRONG: side effect in calculation
  return d;
}
```
