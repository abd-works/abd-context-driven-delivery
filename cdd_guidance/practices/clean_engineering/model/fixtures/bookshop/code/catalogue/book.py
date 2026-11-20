"""A title the bookshop sells."""

from __future__ import annotations


class OutOfStock(ValueError):
    """More copies were asked for than the shop holds."""


class Book:
    """A title the shop sells, with its price in cents and the copies in stock."""

    def __init__(self, isbn: str, title: str, price: int, copies: int) -> None:
        self.isbn = isbn
        self.title = title
        self.price = price
        self.copies = copies

    def matches(self, word: str) -> bool:
        """Whether the title holds the search word; an empty word matches every book."""
        return word.lower() in self.title.lower()

    def is_in_stock(self, quantity: int) -> bool:
        """Whether the shop holds at least quantity copies."""
        return 0 < quantity <= self.copies

    def reserve(self, quantity: int) -> None:
        """Take quantity copies out of stock, never more than are held."""
        if not self.is_in_stock(quantity):
            raise OutOfStock(self.title)
        self.copies -= quantity
