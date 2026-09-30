# Bounded Context Map

## Sales | custom

### ShoppingCart

ShoppingCart
  CartItem
  Discount

Integrations:
  - Product
    pattern: Customer/Supplier
    direction: downstream
    crosses: unit price
    integration: synchronous call to Catalog.Product.unit_price at add_item

emits:
  - CartCheckedOut

## Catalog | bespoke

### Product

Product

## event map

- CartCheckedOut: emitted by ShoppingCart; consumed by Product
