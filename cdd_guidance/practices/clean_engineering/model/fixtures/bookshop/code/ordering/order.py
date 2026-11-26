"""A cart's lines as bought."""

from __future__ import annotations

from src.ordering.cart_line import CartLine
from src.ordering.payment import Payment


class PaymentNotAuthorised(ValueError):
    """An order placed before its payment was authorised."""


class Order:
    """The lines a customer bought and the payment that paid for them."""

    def __init__(self, lines: list[CartLine], payment: Payment) -> None:
        self.lines: list[CartLine] = lines
        self.payment: Payment = payment
        self.status = "new"

    def place(self) -> None:
        """Reserve each line's copies; an unauthorised payment is refused."""
        if not self.payment.authorised:
            raise PaymentNotAuthorised()
        for line in self.lines:
            line.book.reserve(line.quantity)
        self.status = "placed"

    def total(self) -> int:
        """The sum of the lines' subtotals."""
        return sum(line.subtotal() for line in self.lines)
