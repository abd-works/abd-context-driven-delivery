---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Domain Model — Bookshop

**Sources / context:** `bounded-context-map.md` (read in full).

---

## Ordering | custom

### Order

An order keeps its lines and its total in step.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
+ << composition >> lines: OrderLine
+ << association >> bookId: BookId
	// held by identity — Book lives in Catalog
----
+ total(): Money
	-> OrderLine.price
+ cancel(reason: Reason): void
	// an order already shipped is refused

**Invariants**

- the total is the sum of the lines' prices

#### OrderRepository <<Repository>>

------
+ << aggregation >> orders: Collection<Order>
----
+ load(orderId: OrderId): Order

#### OrderLine <<Value Object>>

------
+ title: Title
+ price: Money

## Catalog | custom

### Book

A book has one price.

#### Book <<Aggregate Root>> <<Entity>>

------
+ bookId: BookId
+ price: Money
----
+ reprice(price: Money): void
