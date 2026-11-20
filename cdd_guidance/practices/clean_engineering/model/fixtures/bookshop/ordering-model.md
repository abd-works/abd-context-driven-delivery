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
