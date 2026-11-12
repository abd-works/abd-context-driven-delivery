---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Orders Model

Known issues: `place` takes five parameters, over the limit; `Basket` is described here and in no code.

## Orders

**Module:** `orders`

> // seam: the orders a shopper places
> // constraint: place an order only through its operations

#### **Order** <<Aggregate Root>> <<Entity>>

+ Order(shopper: string)
------
+ shopper: string
+ lines: string[]
+ total: number
----
+ place(a: string, b: string, c: string, d: string, e: string): void
	-> confirm()
+ confirm(): boolean

#### **Basket** <<Entity>>

+ Basket(order: Order)
------
+ pets: number
----
+ empty(): void
