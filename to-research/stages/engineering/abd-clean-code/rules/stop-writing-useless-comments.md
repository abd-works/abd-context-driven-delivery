---
scanner: useless_comments_scanner.py
---

### Rule: Stop Writing Useless Comments

Comments should explain WHY, not WHAT. The code already shows what it does. Delete noise comments and commented-out code.

#### DO

- Legal notices.
- Explanations for non-obvious algorithms.
- Actionable TODOs with context.

```python
# Copyright 2025 Company Name

# Newton-Raphson approximation for 1/sqrt(x); see Quake III Arena source
def fast_inverse_sqrt(x):
    ...

# TODO: Replace with paginated query when dataset exceeds 10k rows
def load_all_orders():
    ...
```

```javascript
// Copyright 2025 Company Name

// Newton-Raphson approximation for 1/sqrt(x); see Quake III Arena source
function fastInverseSqrt(x) {
  // ...
}

// TODO: Replace with paginated query when dataset exceeds 10k rows
function loadAllOrders() { }
```

#### DON'T

- Write comments that restate what the code already says.
- Leave commented-out code in the codebase.
- Add attribution comments.

```python
# i = 0  # initialize counter
i = 0

# def old_process(data):  # WRONG: commented-out code as backup
#     return legacy(data)
def process(data):
    return transform(data)
```

```javascript
let i = 0;  // initialize counter      // WRONG: noise comment

// const oldResult = legacyTransform(data);  // WRONG: commented-out code
// const newResult = transform(data);
function process(data) {
  return transform(data);
}
```
