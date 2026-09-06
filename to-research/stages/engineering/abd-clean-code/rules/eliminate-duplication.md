---
scanner: duplication_scanner.py
---

### Rule: Eliminate Duplication

Extract repeated logic into reusable functions. Do not repeat yourself.

#### DO

- One canonical function for each repeated calculation or operation.

```python
def calculate_subtotal(items):
    return sum(i.price * i.qty for i in items)

subtotal_a = calculate_subtotal(items_a)
subtotal_b = calculate_subtotal(items_b)
```

```javascript
function calculateSubtotal(items) {
  return items.reduce((sum, i) => sum + i.price * i.qty, 0);
}

const subtotalA = calculateSubtotal(itemsA);
const subtotalB = calculateSubtotal(itemsB);
```

#### DON'T

- Copy-paste the same logic in multiple places.

```python
subtotal_a = 0                    # WRONG: duplicated logic
for i in items_a:
    subtotal_a += i.price * i.qty

subtotal_b = 0                    # WRONG: same logic repeated
for i in items_b:
    subtotal_b += i.price * i.qty
```

```javascript
let subtotalA = 0;                // WRONG: duplicated logic
for (const i of itemsA) subtotalA += i.price * i.qty;

let subtotalB = 0;                // WRONG: same logic repeated
for (const i of itemsB) subtotalB += i.price * i.qty;
```
