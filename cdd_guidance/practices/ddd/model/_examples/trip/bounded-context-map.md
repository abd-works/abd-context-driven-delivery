# Bounded Context Map — Bookshop

The bookshop sells books and keeps a catalogue.

## Ordering | custom

Where a Customer's orders are taken.

### Order

Order - what a Customer asked for
  OrderLine

Integrations:
  - Catalog (by BookId)
    pattern: Customer/Supplier
    direction: downstream
    crosses: the book's title and price
    integration: Order.total reads Book.price

## Catalog | custom

The books the shop sells.

### Book

Book - a title on sale
