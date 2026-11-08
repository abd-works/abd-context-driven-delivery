class Cart:
    def __init__(self) -> None:
        self._lines: list[Line] = []

    def add(self, amount: int) -> None:
        self._lines.append(Line(Price(amount)))

    def total(self) -> int:
        return sum(line.price.amount for line in self._lines)


class Line:
    def __init__(self, price: "Price") -> None:
        self.price = price


class Price:
    def __init__(self, amount: int) -> None:
        self.amount = amount


class Discount:
    def rate(self) -> int:
        return 0


class Tax:
    def rate(self) -> int:
        return 0
