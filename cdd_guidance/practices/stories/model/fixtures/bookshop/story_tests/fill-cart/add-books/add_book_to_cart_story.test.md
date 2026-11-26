---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Add Book To Cart

**Story type:** website

See the [story map](../../../.context/story-map.md#s-customer----add-book-to-cart) for where this story sits.

### Domain terms

- ++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++ — a title the Bookshop sells at a price
- ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ — the Books a Customer means to buy
- ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++ — one Book in the Cart with its quantity

### Examples

#### book

| book | example | isbn | title | price | stock |
| --- | --- | --- | --- | --- | --- |
| book | Tiny Tales | 978-1 | Tiny Tales | 5 | 10 |
| book | Grand Atlas | 978-2 | Grand Atlas | 80 | 0 |

#### cart

| cart | example | lines | total |
| --- | --- | --- | --- |
| cart | empty cart | none | 0 |
| cart | cart with Tiny Tales | 1 x Tiny Tales | 5 |

### Background

*Given* the Bookshop sells ++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++ ++Tiny Tales++  
  *And* the Customer has ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ ++empty cart++

### Behaviors

#### Scenario: Add a book in stock

*When* the Customer adds ++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++ ++Tiny Tales++ to the ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++

```realization
Cart.addBook(book, 1)
  -> Book.reserve(1)
  <- CartLine
```

*Then* the ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ holds a ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++ of 1 x Tiny Tales  
  *And* the Cart total is *5*

#### Scenario: Refuse a book out of stock

*Given* the Bookshop sells ++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++ ++Grand Atlas++ with no stock  
*When* the Customer adds ++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++ ++Grand Atlas++ to the ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++  
*Then* the Bookshop refuses with "Grand Atlas is out of stock"  
  *But* no ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++ is added
