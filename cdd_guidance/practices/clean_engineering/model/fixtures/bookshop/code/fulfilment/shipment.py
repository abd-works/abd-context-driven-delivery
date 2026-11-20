"""The parcel the shop sends for one order."""

from __future__ import annotations

from src.ordering.order import Order, PaymentNotAuthorised


class Shipment:
    """The parcel for one order, and whether it has left the shop."""

    def __init__(self, order: Order, address: str) -> None:
        self.order: Order = order
        self.address = address
        self.dispatched = False

    def dispatch(self) -> None:
        """Send the parcel; an order whose payment is not authorised is refused."""
        if not self.order.payment.authorised or self.order.total() <= 0:
            raise PaymentNotAuthorised()
        self.dispatched = True

    def days_to_arrive(self) -> int:
        """How many days the parcel takes."""
        return 5


class ExpressShipment(Shipment):
    """A shipment a courier carries in one day."""

    def __init__(self, order: Order, address: str, courier: str) -> None:
        super().__init__(order, address)
        self.courier = courier

    def days_to_arrive(self) -> int:
        """Always one day."""
        return 1
