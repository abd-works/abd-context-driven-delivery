# <<Aggregate Root>> <<Entity>>
class Cart:
    def __init__(self):
        self._lines = []

    def add_book(self, book, quantity):
        self._lines.append((book.book_id, book.price, quantity))


# <<Aggregate Root>> <<Entity>>
class Book:
    def __init__(self, book_id, price):
        self.book_id = book_id
        self.price = price

    def reprice(self, price):
        self.price = price


# <<Repository>>
class BookRepository:
    def __init__(self):
        self._books = {}

    def load(self, book_id):
        return self._books[book_id]
