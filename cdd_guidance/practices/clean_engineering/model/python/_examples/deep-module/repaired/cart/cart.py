class Cart:
    def __init__(self) -> None:
        self._lines: list[Line] = []

    def add(self, amount: int, quantity: int) -> None:
        self._lines.append(Line(Price(amount), quantity))

    def total(self) -> int:
        return self._taxed(self._discounted(sum(line.subtotal() for line in self._lines)))

    def _discounted(self, amount: int) -> int:
        return amount - Discount().off(amount)

    def _taxed(self, amount: int) -> int:
        return amount + Tax().on(amount)


class Line:
    def __init__(self, price: "Price", quantity: int) -> None:
        self.price = price
        self.quantity = quantity

    def subtotal(self) -> int:
        return self.price.amount * self.quantity


class Price:
    def __init__(self, amount: int) -> None:
        self.amount = amount


class Discount:
    def off(self, amount: int) -> int:
        return 0


class Tax:
    def on(self, amount: int) -> int:
        return 0
