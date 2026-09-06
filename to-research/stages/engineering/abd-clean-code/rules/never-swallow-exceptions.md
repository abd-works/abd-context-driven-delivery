---
scanner: swallowed_exceptions_scanner.py
---

### Rule: Never Swallow Exceptions

Never silently swallow exceptions. Always log and re-raise, re-raise, or convert to a domain exception.

#### DO

- Log and re-raise when you cannot fully handle the error.
- Convert to a domain exception with context to help the caller.

```python
def parse_request(raw_data):
    try:
        return _parse_json(raw_data)
    except ParseError as e:
        logger.error("Parse failed", exc_info=e)
        raise
```

```javascript
async function parseRequest(rawData) {
  try {
    return await _parseJson(rawData);
  } catch (err) {
    logger.error('Parse failed', err);
    throw err;
  }
}
```

#### DON'T

- Use bare `except: pass` or an empty catch block.
- Catch exceptions and return None.

```python
try:
    result = risky_operation()
except:                         # WRONG: swallows everything including SystemExit
    pass                        # WRONG: silent failure, caller has no signal
```

```javascript
try {
  result = riskyOperation();
} catch (e) {
  // WRONG: swallowed, caller never knows
}
```
