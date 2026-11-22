from __future__ import annotations

# === Ordering | custom · Order ===


@aggregate_root
@entity
class Order:
    """Module: Ordering | custom · Order"""

    orderId: OrderId
    # << composition >>
    lines: OrderLine
    # << association >>
    # held by identity — Book lives in Catalog
    bookId: BookId

    def __init__(self, orderId: OrderId, lines: OrderLine, bookId: BookId) -> None:
        self.orderId = orderId
        self.lines = lines
        self.bookId = bookId

    def total(self) -> Money:
        OrderLine.price()
        raise NotImplementedError

    def cancel(self, reason: Reason) -> None:
        # an order already shipped is refused
        raise NotImplementedError


@repository
class OrderRepository:
    """Module: Ordering | custom · Order"""

    # << aggregation >>
    orders: Collection[Order]

    def __init__(self, orders: Collection[Order]) -> None:
        self.orders = orders

    def load(self, orderId: OrderId) -> Order:
        raise NotImplementedError


@value_object
class OrderLine:
    """Module: Ordering | custom · Order"""

    title: Title
    price: Money

    def __init__(self, title: Title, price: Money) -> None:
        self.title = title
        self.price = price

# === Catalog | custom · Book ===


@aggregate_root
@entity
class Book:
    """Module: Catalog | custom · Book"""

    bookId: BookId
    price: Money

    def __init__(self, bookId: BookId, price: Money) -> None:
        self.bookId = bookId
        self.price = price

    def reprice(self, price: Money) -> None:
        raise NotImplementedError
