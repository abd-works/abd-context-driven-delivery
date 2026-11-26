class Shipments:
    """Counts the lines of the orders that can ship."""

    def shippable_lines(self, orders: list) -> int:
        count = 0
        for order in orders:
            if order.paid:
                for line in order.lines:
                    if line.in_stock:
                        for parcel in line.parcels:
                            if parcel.packed:
                                if parcel.weight > 0:
                                    count += 1
        return count
