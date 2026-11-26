"""One book chosen in a cart."""

from __future__ import annotations

from src.catalogue.book import Book


class CartLine:
    """A book and how many copies of it the customer chose."""

    def __init__(self, book: Book, quantity: int) -> None:
        self.book: Book = book
        self.quantity = quantity

    def subtotal(self) -> int:
        """The book's price times the quantity."""
        return self.book.price * self.quantity
