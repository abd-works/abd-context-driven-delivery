---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Domain Model — Bookshop

**Sources / context:** [bounded-context-map.md](bounded-context-map.md) (read in full); [story-map.md](story-map.md) epics Browse Books, Fill Cart, Check Out, Fulfil Order.

---

## Ordering | custom

### Cart

A cart holds one line per book and its total is the sum of its lines.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
+ customerId: CustomerId
+ << composition >> lines: CartLine[]
+ << association >> bookId: BookId
	// held by identity — Book lives in Catalogue · Book
----
+ addBook(bookId: BookId, quantity: Quantity): CartLine
	-> BookRepository.load(bookId)
	// the title and price cross at the moment the book is added
+ removeBook(bookId: BookId): void
+ total(): Money
	-> CartLine.subtotal
+ checkOut(): Order
	-> OrderRepository.create(cart)

**Invariants**

- a cart holds at most one line for each book
- the total is the sum of the lines' subtotals

#### CartRepository <<Repository>>

------
+ << aggregation >> carts: Collection<Cart>
----
+ create(customerId: CustomerId): Cart
+ load(cartId: CartId): Cart
+ update(cart: Cart): void

#### CartLine <<Value Object>>

------
+ bookId: BookId
+ title: Title
+ unitPrice: Money
+ quantity: Quantity
----
+ subtotal(): Money

Integrations:
  - → Catalogue · Book · Book (by BookId)
    pattern: Customer/Supplier
    crosses: the book's title and price at the moment it is added
    integration: Cart.addBook
    sync: Catalogue owns the price · copied when the book is added · stale until checkout

### Order

An order is paid once, in full, before it can be fulfilled.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
+ customerId: CustomerId
+ deliveryAddress: Address
+ << composition >> payment: Payment
+ << association >> cartId: CartId
	// held by identity — the Cart it was checked out from
----
+ pay(amount: Money): Payment
	-> Payment.settle
	// a paid order is handed to Fulfilment
+ cancel(reason: Reason): void
	// an order already shipped is refused

**Invariants**

- an order is paid exactly once and for its whole total
- a cancelled order is never shipped

#### OrderRepository <<Repository>>

------
+ << aggregation >> orders: Collection<Order>
----
+ create(cart: Cart): Order
+ load(orderId: OrderId): Order
+ update(order: Order): void
+ search(customerId: CustomerId): Order[]
	// the Customer looks up their own orders

#### Payment <<Entity>>

------
+ paymentId: PaymentId
+ amount: Money
+ settled: boolean
----
+ settle(): void

Integrations:
  - → Fulfilment · Shipment · Shipment (by OrderId)
    pattern: Open Host / Published Language
    crosses: the paid order's lines and delivery address
    integration: Order.pay
    sync: Ordering owns the order · on payment · within a minute

---

## Catalogue | custom

### Book

A book on sale has exactly one price.

#### Book <<Aggregate Root>> <<Entity>>

------
+ bookId: BookId
+ title: Title
+ << composition >> price: Price
----
+ reprice(amount: Money): void
	-> Price.withAmount
+ withdraw(): void

**Invariants**

- a book on sale has exactly one price, greater than zero

#### BookRepository <<Repository>>

------
+ << aggregation >> books: Collection<Book>
----
+ create(title: Title, amount: Money): Book
+ load(bookId: BookId): Book
+ search(title: Title): Book[]
	// the Customer browses by title

#### Price <<Value Object>>

------
+ amount: Money
+ currency: Currency
----
+ withAmount(amount: Money): Price

---

## Fulfilment | ShipFast

### Shipment

A shipment is dispatched once, for one paid order.

#### Shipment <<Aggregate Root>> <<Entity>>

------
+ shipmentId: ShipmentId
+ << composition >> parcel: Parcel
+ << association >> orderId: OrderId
	// held by identity — Order lives in Ordering · Order
----
+ pack(parcel: Parcel): void
+ dispatch(): TrackingCode
	-> OrderRepository.load(orderId)
	// the Shop Clerk ships only a paid order

**Invariants**

- a shipment is dispatched at most once

#### ShipmentRepository <<Repository>>

------
+ << aggregation >> shipments: Collection<Shipment>
----
+ create(orderId: OrderId): Shipment
+ load(shipmentId: ShipmentId): Shipment
+ update(shipment: Shipment): void

#### Parcel <<Value Object>>

------
+ weight: Weight
+ trackingCode: TrackingCode

Integrations:
  - → Ordering · Order · Order (by OrderId)
    pattern: Conformist
    crosses: the order's identity and delivery address
    integration: Shipment.dispatch
    sync: Ordering owns the order · read at dispatch · none
