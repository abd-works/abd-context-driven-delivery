"""Order. The books a Customer bought, which the Shop Clerk packs and ships."""

from __future__ import annotations


class OrderNotPaid(Exception):
    """Raised when a Shop Clerk packs an Order whose Payment is not authorized."""

    def __init__(self, number: str) -> None:
        super().__init__(f"order {number} is not paid")
        self.number = number


class Order:
    def __init__(self, number: str, total: int, payment_status: str = "unpaid") -> None:
        self.number = number
        self.total = total
        self.payment_status = payment_status
        self.status = "submitted"

    def pack(self) -> None:
        # An Order is packed only after its Payment is authorized.
        if self.payment_status != "authorized":
            raise OrderNotPaid(self.number)
        self.status = "packed"


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def create(self, order: Order) -> Order:
        self._orders[order.number] = order
        return order

    def load(self, number: str) -> Order:
        return self._orders[number]
