---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

# Catalogue

**Module:** `src/catalogue`

The books the shop sells, with each one's price and stock.

---

## Catalogue

The shelf and the books on it.

### **Catalogue** <<Aggregate Root>>

+ Catalogue(books: list[Book])
------
+ << aggregation >> books: list[Book]
----
+ search(word: str): list[Book]
	-> Book.matches
	// an empty word finds every book
+ book_with(isbn: str): Book
	// an ISBN the shop does not sell is refused

### **Book** <<Entity>>

+ Book(isbn: str, title: str, price: int, copies: int)
------
+ isbn: str
	// the book's identity
+ title: str
+ price: int
	// in cents
+ copies: int
----
+ matches(word: str): bool
+ is_in_stock(quantity: int): bool
+ reserve(quantity: int): None
	// never takes more copies than are in stock
