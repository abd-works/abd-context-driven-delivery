class Order:
    """An order and its lines."""

    def __init__(self, lines: list[int]) -> None:
        self._lines = lines

    def line(self, index: int) -> int:
        return self._lines[index]

    def total(self) -> int:
        return sum(self._lines)
