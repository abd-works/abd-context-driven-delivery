---
scanner: meaningful_context_scanner.py
---

### Rule: Provide Meaningful Context

Replace magic numbers and inline literals with named constants that explain their purpose and unit.

#### DO

- Declare a named constant for every value with business meaning.

```python
ADULT_AGE = 18
TAX_RATE = 0.13

def is_adult(age: int) -> bool:
    return age >= ADULT_AGE
```

```javascript
const ADULT_AGE = 18;
const TAX_RATE = 0.13;

function isAdult(age) {
  return age >= ADULT_AGE;
}
```

#### DON'T

- Inline unexplained numbers or business constants.

```python
def is_adult(age):
    return age >= 18          # WRONG: magic number with no context

import time
time.sleep(86400000)          # WRONG: what unit? what meaning?
```

```javascript
function isAdult(age) {
  return age >= 18;           // WRONG: magic number with no context
}

const total = subtotal * 1.13;  // WRONG: unexplained magic number
```
