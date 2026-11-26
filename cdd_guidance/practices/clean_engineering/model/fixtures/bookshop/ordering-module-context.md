# src/ordering
*Cart* is what a customer fills while browsing: it holds one *CartLine* for each book chosen and checks itself out into an *Order*.

*Order* is the cart's lines as bought, with the *Payment* that paid for them.

- **Purpose:** let a customer fill a cart with books and check it out into a paid order
- **Seam (terms):** Cart, CartLine, Order, Payment
- **Dependencies (one-way):** src/catalogue

## Constraint

Make an *Order* only through `Cart.check_out`; an order built by hand has no authorised payment.
