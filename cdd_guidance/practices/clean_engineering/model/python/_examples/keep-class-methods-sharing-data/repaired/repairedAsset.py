class Checkout:
    """Takes payment for a cart."""

    def __init__(self, cart: list[int]) -> None:
        self._cart = cart

    def total(self) -> int:
        return sum(self._cart)

    def is_empty(self) -> bool:
        return not self._cart
