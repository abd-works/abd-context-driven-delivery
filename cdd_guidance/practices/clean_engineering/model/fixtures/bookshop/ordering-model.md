---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

# Ordering

**Module:** `src/ordering`

A customer's cart and the order it becomes at checkout.

---

## Cart

A cart and its lines change together.

### **Cart** <<Aggregate Root>>

The *Cart* is the books a customer means to buy, while they are still choosing them. The Cart is created for one customer and starts empty; it ends when the customer checks it out and it becomes an *Order*.

- **Lines.** The Cart adds a *CartLine* for each book the customer picks, after asking the *Book* whether it is in stock, and refuses a book that is not.
- **Total.** The Cart adds up the subtotal each CartLine calculates for itself.
- **Checking out.** The Cart refuses to check out while it is empty. Otherwise it asks the *Payment* to authorise itself, and asks the new Order to place itself with the Cart's lines and that Payment.

+ Cart(customer_id: str)
------
+ customer_id: str
	// who is filling the cart
+ << composition >> lines: list[CartLine]
----
+ add(book: Book, quantity: int): CartLine
	-> Book.is_in_stock
	// a book out of stock is refused
+ total(): int
	-> CartLine.subtotal
+ check_out(payment: Payment): Order
	-> Payment.authorise
	-> Order.place
	// an empty cart is refused

### **CartLine** <<Value Object>>

+ CartLine(book: Book, quantity: int)
------
+ quantity: int
+ << association >> book: Book
----
+ subtotal(): int
	// the book's price times the quantity

## Order

An order and the payment that paid for it.

### **Order** <<Aggregate Root>>

The *Order* is what a customer bought: the lines their Cart held and the Payment that paid for them. The Order is created from a checked-out Cart; it starts placed and ends shipped.

- **Placing.** The Order refuses to place itself unless its Payment is authorised, then asks each line's *Book* to reserve a copy.
- **Total.** The Order adds up the subtotal each *CartLine* calculates for itself.

+ Order(lines: list[CartLine], payment: Payment)
------
+ status: str
	// placed, then shipped
+ << aggregation >> lines: list[CartLine]
+ << association >> payment: Payment
----
+ place(): None
	-> Book.reserve
	// an order whose payment is not authorised is refused
+ total(): int
	-> CartLine.subtotal

### **Payment** <<Entity>>

+ Payment(amount: int)
------
+ amount: int
+ authorised: bool
----
+ authorise(): bool
	// an amount of zero is refused
