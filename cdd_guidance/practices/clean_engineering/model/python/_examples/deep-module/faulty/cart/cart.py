class Cart:
    def add(self, line: "Line") -> None:
        return None

    def remove(self, line: "Line") -> None:
        return None

    def lines(self) -> list:
        return []

    def total(self) -> int:
        return 0


class Line:
    def price(self) -> "Price":
        return Price()

    def quantity(self) -> int:
        return 1

    def subtotal(self) -> int:
        return self.price().amount() * self.quantity()


class Price:
    def amount(self) -> int:
        return 1

    def currency(self) -> str:
        return "CAD"


class Discount:
    def rate(self) -> int:
        return 0

    def applies_to(self, line: Line) -> bool:
        return line.quantity() > 1


class Tax:
    def rate(self) -> int:
        return 0
