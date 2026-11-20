# Bounded Context Map — Bookshop

The Bookshop lets a Customer browse books, fill a cart, check out, and has the Shop Clerk fulfil the order. Stories are in [story-map.md](story-map.md); the classes are in [domain-model.md](domain-model.md).

## Ordering | custom

Where a Customer fills a Cart and checks out an Order. Epics: Fill Cart, Check Out.

### Cart

Cart - the books a Customer means to buy
  Cart Line

Integrations:
  - → Catalogue · Book · Book (by BookId)
    pattern: Customer/Supplier
    direction: downstream
    crosses: the book's title and price at the moment it is added
    integration: Cart.addBook reads Book.price

emits events:
  - CartCheckedOut

### Order

Order - what a Customer bought and paid for
  Payment

Integrations:
  - → Fulfilment · Shipment · Shipment (by OrderId)
    pattern: Open Host / Published Language
    direction: upstream
    crosses: the paid order's lines and delivery address
    integration: Order.pay publishes OrderPaid

emits events:
  - OrderPaid
consumes events:
  - CartCheckedOut

## Catalogue | custom

The books the shop sells and what each costs. Epic: Browse Books.

### Book

Book - a title on sale with one price
  Price

## Fulfilment | ShipFast

Where the Shop Clerk packs and ships a paid order. Epic: Fulfil Order.

### Shipment

Shipment - the parcel sent for one Order
  Parcel

Integrations:
  - → Ordering · Order · Order (by OrderId)
    pattern: Conformist
    direction: downstream
    crosses: the order's identity and delivery address
    integration: Shipment.dispatch reads Order.deliveryAddress

consumes events:
  - OrderPaid

## event map

- CartCheckedOut: emitted by Cart; consumed by Order
- OrderPaid: emitted by Order; consumed by Shipment
