"""What a customer fills while browsing."""

from __future__ import annotations

from src.catalogue.book import Book, OutOfStock
from src.ordering.cart_line import CartLine
from src.ordering.order import Order
from src.ordering.payment import Payment


class EmptyCart(ValueError):
    """A cart checked out with no lines."""


class Cart:
    """The books a customer has chosen, one line for each."""

    def __init__(self, customer_id: str) -> None:
        self.customer_id = customer_id
        self.lines: list[CartLine] = []

    def add(self, book: Book, quantity: int) -> CartLine:
        """Add a line for the book; a book out of stock is refused."""
        if not book.is_in_stock(quantity):
            raise OutOfStock(book.title)
        line = CartLine(book, quantity)
        self.lines.append(line)
        return line

    def total(self) -> int:
        """The sum of the lines' subtotals."""
        return sum(line.subtotal() for line in self.lines)

    def check_out(self, payment: Payment) -> Order:
        """Authorise the payment and place the order; an empty cart is refused."""
        if not self.lines:
            raise EmptyCart()
        payment.authorise()
        order = Order(self.lines, payment)
        order.place()
        return order
