---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Domain Model — Bookshop

---

## Ordering | custom

### Cart

A cart holds one line per book and its total is the sum of its lines.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
+ << composition >> lines: CartLine[]
----
+ total(): Money
	-> CartLine.subtotal

**Invariants**

- the total is the sum of the lines' subtotals

#### CartLine <<Value Object>>

------
+ quantity: Quantity
+ unitPrice: Money
----
+ subtotal(): Money
