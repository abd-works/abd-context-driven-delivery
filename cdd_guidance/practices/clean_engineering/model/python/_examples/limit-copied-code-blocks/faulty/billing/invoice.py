"""The invoice works out what an order costs."""


class Invoice:
    def total(self, lines: list, discount: int, tax_rate: int, minimum_charge: int) -> int:
        subtotal = sum(line.price * line.quantity for line in lines)
        if subtotal > 100:
            subtotal = subtotal - subtotal * discount // 100
        taxed = subtotal + subtotal * tax_rate // 100
        rounded = round(taxed / 5) * 5
        return max(rounded, minimum_charge)
