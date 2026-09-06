# Specification by Example — Examples

## Plain Scenario (distinct flow)

```gherkin
Scenario: Customer places and tracks a new order
  Given a Customer with an active account
  When the Customer adds items to the cart and submits the order
  Then the order is confirmed with a tracking number
  When the Customer views the active orders for their account
  Then that order is displayed along with any other active orders
  And the status for that order is displayed as Processing
  When the order is dispatched
  Then the Customer receives a shipment notification
  And the order status changes to Shipped
```

**Bold** for domain concept names, *italics* for their actual values — e.g. **User** *Jane Doe*, **Enterprise** *Acme Corp*.

## Scenario Outline (parameterized — same steps, varying data)

```gherkin
Scenario Outline: Applying a discount code reduces the order total
  Given a **Customer** *{customer_name}* with an active account
  And a **Cart** containing items totalling *{original_total}*
  When the **Customer** applies **Discount Code** *{code}*
  Then the **Order Total** is *{discounted_total}*
  And the **Discount** line shows *{discount_description}*

  Examples: DiscountCode

  | scenario         | code       | discount_description |
  | ---------------- | ---------- | -------------------- |
  | Percentage off   | SAVE20     | 20% off              |
  | Fixed amount off | FLAT10     | $10.00 off           |

  Examples: CartAndResult

  | scenario         | customer_name | original_total | discounted_total |
  | ---------------- | ------------- | -------------- | ---------------- |
  | Percentage off   | Jane Doe      | $50.00         | $40.00           |
  | Fixed amount off | Jane Doe      | $50.00         | $40.00           |
```

The `scenario` column joins `DiscountCode` to `CartAndResult`. Each table holds one concept; FK columns express the relationship.

## Background (shared state across 3+ scenarios)

```gherkin
Background:
  Given a **Warehouse** *"Central Hub"* with **Inventory** for all standard products
  And a **Customer** *"Jane Doe"* with an active account
```

Background is Given/And only — no When or Then. Use when three or more scenarios share identical starting state.
