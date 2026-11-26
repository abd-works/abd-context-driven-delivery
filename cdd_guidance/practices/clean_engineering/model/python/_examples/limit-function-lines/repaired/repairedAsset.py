class Receipt:
    """Adds up an order."""

    def total(self, order) -> int:
        return sum(order.lines)
