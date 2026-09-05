---
scanner: abstraction_levels_scanner.py
---

### Rule: Maintain Abstraction Levels

Step down one abstraction level at a time. High-level functions call medium-level helpers; never mix raw SQL or HTTP with business logic.

#### DO

- High-level orchestration calls named helpers at the next level down.

```python
def checkout(user, cart, services):
    sub = subtotal(cart.items)            # medium-level calculation
    total = total_with_tax(sub)           # medium-level calculation
    invoice = save_invoice(user, total, cart.items)  # medium-level persistence
    return invoice, total
```

```javascript
export async function checkout({ user, cart, taxRate, services }) {
  const sub = subtotal(cart.items);           // medium-level calculation
  const total = totalWithTax(sub, taxRate);   // medium-level calculation
  const invoice = await saveInvoice(user, total, cart);  // medium-level persistence
  return { invoice, total };
}
```

#### DON'T

- Mix raw SQL or low-level I/O detail directly in high-level orchestration.

```python
def checkout(user, cart):
    sub = sum(i.price * i.qty for i in cart.items)   # WRONG: low-level detail
    db.execute("INSERT INTO invoices (user_id, total) VALUES (?, ?)", user.id, sub)
```

```javascript
async function checkout(user, cart) {
  const sub = cart.items.reduce((s, i) => s + i.price * i.qty, 0);  // WRONG: low-level
  await db.execute("INSERT INTO invoices...");       // WRONG: SQL in orchestration
}
```
