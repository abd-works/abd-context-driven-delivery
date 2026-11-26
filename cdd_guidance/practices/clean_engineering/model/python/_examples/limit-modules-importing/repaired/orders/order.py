from money.money import Amount


class Order:
    def __init__(self, held: Amount) -> None:
        self._held = held

    def paid(self) -> Amount:
        return self._held
