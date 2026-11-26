---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Add Book To Cart

**Story type:** website

### Domain terms

- ++Book++ — a title the Bookshop sells at a price
- ++Cart++ — the Books a Customer means to buy

### Background

*Given* the Bookshop sells ++Book++ ++Tiny Tales++  
  *And* the Customer has an empty ++Cart++

```realization
// the Bookshop sells Book Tiny Tales
book = new Book(TinyTales.title, TinyTales.price)
BookRepository.create(book)
// the Customer has an empty Cart
cart = new Cart(Me.customerId)
CartRepository.create(cart)
```

### Behaviors

#### Scenario: Add a book in stock

*When* the Customer adds ++Book++ ++Tiny Tales++ to the ++Cart++

```realization
cart = CartRepository.load(cart.cartId)
book = BookRepository.load(book.bookId)
cart.addBook(book, 1)
CartRepository.update(cart)
```

*Then* the ++Cart++ holds one line of 1 x Tiny Tales
