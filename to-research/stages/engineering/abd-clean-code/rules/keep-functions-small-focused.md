---
scanner: function_size_scanner.py
---

### Rule: Keep Functions Small and Focused

Keep functions under 20 lines. Extract complex logic into named helpers.

#### DO

- Functions fit in one screen.
- Extract calculation, validation, and persistence into named helpers.

```python
TAX_RATE = 0.13

def total_with_tax(subtotal: float, tax_rate: float = TAX_RATE) -> float:
    return round(subtotal * (1 + tax_rate), 2)

def checkout(user, cart, services):
    sub = subtotal(cart.items)
    total = total_with_tax(sub)
    invoice = save_invoice(user, total, cart.items)
    return invoice, total
```

```javascript
const TAX_RATE = 0.13;

export function totalWithTax(subtotal, tax = TAX_RATE) {
  return Math.round(subtotal * (1 + tax) * 100) / 100;
}

export async function checkout({ user, cart, services }) {
  const sub = subtotal(cart.items);
  const total = totalWithTax(sub);
  const invoice = await saveInvoice(user, total, cart);
  return { invoice, total };
}
```

#### DON'T

- Write functions that inline calculation, persistence, email, and logging together.

```python
def checkout(user, cart):
    subtotal = sum(i.price * i.qty for i in cart.items)  # WRONG: mixed abstraction levels
    total = round(subtotal * 1.13, 2)
    db.invoices.insert({'user_id': user.id, 'total': total})
    for it in cart.items:
        db.products.decrement(it.sku, it.qty)
    email.send(user.email, f"Thanks for ${total}")
    print('checkout complete')
    return total
```

```javascript
async function checkout(user, cart) {
  let subtotal = 0;
  for (const i of cart.items) subtotal += i.price * i.qty;  // WRONG: mixed levels
  const total = subtotal * 1.13;
  await db.invoices.insert({ userId: user.id, total });
  for (const it of cart.items) await db.products.decrement(it.sku, it.qty);
  await email.send(user.email, `Thanks for $${total}`);
  return total;
}
```
