---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Bookshop

**Sources / context:** `README.md` (a customer browses books, fills a cart, checks out, and the shop fulfils the order); the domain model `.context/domain-model.md`.

---

The map reads in the order a sale happens: browse, fill the cart, check out, fulfil.

# (E) Browse Books

A Customer finds a Book to buy.

## (S) Customer --> Search Books
## (S) Customer --> View Book
## (S) Customer --> Filter Books
## (S) Shop Clerk --> Add Book

# (E) Fill Cart

## (E) Add Books

The Cart gains a Cart Line for each Book the Customer wants.

### (S) Customer --> [Add Book To Cart](../story_tests/fill-cart/add-books/add_book_to_cart_story.test.md)
### (S) Customer --> [Change Cart Line Quantity](../story_tests/fill-cart/add-books/change_cart_line_quantity_story.test.md)

## (E) Review Cart

### (S) Customer --> View Cart
### (S) Customer --> Remove Cart Line

# (E) Check Out

## (E) Place Order

### (S) Customer --> Submit Order

The Cart becomes an Order the moment the Customer submits it.

### (S:system) Payment Provider --> Authorize Payment

## (E) Confirm Order

### (S) Customer --> View Order Confirmation
### (S) Customer --> Cancel Order

# (E) Fulfil Order

## (S) Shop Clerk --> Pack Order
## (S) Shop Clerk --> Create Shipment
## (S) Shop Clerk --> Mark Order Shipped
## (S) Customer --> Track Shipment

---

## Scope boundary

**In scope:** browsing, the cart, checkout with one payment provider, and fulfilment by the Shop Clerk.
**Out of scope:** returns, gift cards, and reviews.
