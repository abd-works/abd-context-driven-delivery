---
scanner: intention_revealing_names_scanner.py
---

### Rule: Use Intention-Revealing Names

Names answer "why does this exist?". Avoid abbreviations, single letters, and undescriptive identifiers.

#### DO

- Named constants for every magic number.
- Variable names that reveal purpose, unit, and domain context.

```python
MILLISECONDS_PER_DAY = 86_400_000

elapsed_time_in_days = timer.elapsed_ms() / MILLISECONDS_PER_DAY
```

```javascript
const MILLISECONDS_PER_DAY = 86_400_000;

const elapsedTimeInDays = timer.elapsedMs / MILLISECONDS_PER_DAY;
```

#### DON'T

- Use single-letter variable names outside of trivial loop indices.
- Abbreviate names that carry domain meaning.

```python
d = 86400000                                  # WRONG: meaningless name, magic number
elapsed = timer.elapsed_ms() / 86400000       # WRONG: no context on unit
```

```javascript
const d = 86400000;                           // WRONG: meaningless name, magic number
const elapsed = timer.elapsedMs / 86400000;   // WRONG: no context
```
