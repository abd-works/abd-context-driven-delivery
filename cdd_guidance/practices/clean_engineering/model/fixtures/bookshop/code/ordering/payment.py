"""The payment for an order."""

from __future__ import annotations


class NothingToPay(ValueError):
    """A payment of zero."""


class Payment:
    """An amount in cents and whether the customer's bank authorised it."""

    def __init__(self, amount: int) -> None:
        self.amount = amount
        self.authorised = False

    def authorise(self) -> bool:
        """Authorise the amount; zero is refused."""
        if self.amount <= 0:
            raise NothingToPay()
        self.authorised = True
        return self.authorised
