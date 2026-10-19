# Bounded Context Map — Shop

## Sales | custom

### ShoppingCart

ShoppingCart - the cart
  CartItem
  Discount

Integrations:
  - Product (by ProductId)
    pattern: Customer/Supplier
    direction: downstream
    crosses: unit price
    integration: synchronous call to Catalog.Product.unit_price at add_item

emits events:
  - CartCheckedOut

## Catalog | bespoke

### Product

Product - identity and price

## event map

- CartCheckedOut: emitted by ShoppingCart; consumed by Product
