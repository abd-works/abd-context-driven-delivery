"""This project holds a module to 2 importers, so the example stays small. The refund policy moved to refunds, the
one module that uses it, so two modules import money."""


class Amount:
    def __init__(self, cents: int) -> None:
        self._cents = cents

    def plus(self, other: "Amount") -> "Amount":
        return Amount(self._cents + other._cents)
