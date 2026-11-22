class Shipments:
    """Counts the lines of the orders that can ship."""

    def shippable_lines(self, orders: list) -> int:
        return sum(self._shippable_in(order) for order in orders if order.paid)

    def _shippable_in(self, order) -> int:
        return sum(self._packed(line) for line in order.lines if line.in_stock)

    def _packed(self, line) -> int:
        return len([parcel for parcel in line.parcels if parcel.packed and parcel.weight > 0])
