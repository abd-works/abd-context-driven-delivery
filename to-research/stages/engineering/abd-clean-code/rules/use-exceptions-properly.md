---
scanner: exception_handling_scanner.py
---

### Rule: Use Exceptions Properly

Use domain-specific exceptions with informative messages. Never return None to signal an error condition.

#### DO

- Define domain exceptions that extend built-in error types.
- Include the original cause when re-raising to preserve the stack.

```python
class ParseError(ValueError):
    pass

def parse_json(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as e:
        raise ParseError("Invalid JSON") from e   # preserves cause
```

```javascript
class ParseError extends Error { }

function parseJson(payload) {
  try {
    return JSON.parse(payload);
  } catch (e) {
    throw new ParseError('Invalid JSON');         // informative, domain-named
  }
}
```

#### DON'T

- Return None to signal failure.
- Use bare except or silent catch-all blocks.

```python
def load(payload):
    try:
        return json.loads(payload)
    except:                     # WRONG: bare except catches everything
        return None             # WRONG: silent failure, caller gets None with no context
```

```javascript
function load(payload) {
  try {
    return JSON.parse(payload);
  } catch (e) {
    /* ignore */                // WRONG: silent failure, caller has no idea what happened
  }
}
```
