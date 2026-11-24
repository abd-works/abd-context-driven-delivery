from money.money import Amount


class Bill:
    def __init__(self, held: Amount) -> None:
        self._held = held

    def due(self) -> Amount:
        return self._held
