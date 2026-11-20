"""The shelf a customer browses."""

from __future__ import annotations

from src.catalogue.book import Book


class BookNotSold(LookupError):
    """An ISBN the shop does not sell."""


class Catalogue:
    """The books the shop sells, found by a search word or by ISBN."""

    def __init__(self, books: list[Book]) -> None:
        self.books: list[Book] = books

    def search(self, word: str) -> list[Book]:
        """The books whose title holds the word."""
        return [book for book in self.books if book.matches(word)]

    def book_with(self, isbn: str) -> Book:
        """The book with this ISBN."""
        for book in self.books:
            if book.isbn == isbn:
                return book
        raise BookNotSold(isbn)
