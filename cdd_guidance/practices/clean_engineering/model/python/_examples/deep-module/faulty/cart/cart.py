class Cart:
    def add(self, line: "Line") -> None:
        return None


class Line:
    def price(self) -> "Price":
        return Price()


class Price:
    def amount(self) -> int:
        return 1


class Discount:
    def rate(self) -> int:
        return 0


class Tax:
    def rate(self) -> int:
        return 0
