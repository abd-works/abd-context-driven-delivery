class Checkout:
    """Takes payment for a cart, and also formats shipping labels."""

    def __init__(self, cart: list[int], address: str) -> None:
        self._cart = cart
        self._address = address

    def total(self) -> int:
        return sum(self._cart)

    def is_empty(self) -> bool:
        return not self._cart

    def label(self) -> str:
        return self._address.upper()

    def label_lines(self) -> list[str]:
        return self._address.split(",")
