---
scanner: ascii_only_scanner.py
---

# Rule: Use ASCII Only

All test code must use **ASCII-only characters**. No Unicode symbols, emoji, special punctuation, or curly quotes. Windows environments and CI pipelines can mishandle non-ASCII bytes in source files. Use plain ASCII alternatives.

## DO

- Use bracket labels for status indicators: `[PASS]`, `[FAIL]`, `[ERROR]`, `[SKIP]`.
- Use `->` for arrows, `!=` for not-equal, standard ASCII quotes.

```python
print('[PASS] Agent initialized')
print('[ERROR] Config not found')
result = {'status': 'ok', 'name': 'story_bot'}
```

## DON'T

- Use Unicode symbols, emojis, or curly quotes anywhere in test code.

```python
# WRONG
print('\u2713 Done')           # Unicode checkmark
print('\U0001f7e2 OK')         # emoji
message = '\u201chello\u201d'  # curly quotes
```
