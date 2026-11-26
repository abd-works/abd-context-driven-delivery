"""This project holds a module to 2 importers, so the example stays small. money holds the refund policy too, so
refunds imports it as well: three modules import money."""


class Amount:
    def __init__(self, cents: int) -> None:
        self._cents = cents

    def plus(self, other: "Amount") -> "Amount":
        return Amount(self._cents + other._cents)


class RefundPolicy:
    def allows(self, days_since_sale: int) -> bool:
        return days_since_sale <= 30
