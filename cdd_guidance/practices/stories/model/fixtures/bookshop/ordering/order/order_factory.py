from __future__ import annotations


@factory
class OrderFactory:
    """Module: Ordering | custom · Order
    Builds an Order from a checked-out Cart: prices each line again from the Catalogue and refuses an empty cart."""

    books: BookRepository

    def __init__(self, books: BookRepository) -> None:
        self.books = books

    def create(self, cart: Cart, deliveryAddress: Address) -> Order:
        self.books.load(cart.bookId)
        raise NotImplementedError
