"""The receipt works out the cost again, with the invoice's six lines copied: a change to the discount made in one
is missing from the other."""


class Receipt:
    def amount_due(self, lines: list, discount: int, tax_rate: int, minimum_charge: int) -> int:
        subtotal = sum(line.price * line.quantity for line in lines)
        if subtotal > 100:
            subtotal = subtotal - subtotal * discount // 100
        taxed = subtotal + subtotal * tax_rate // 100
        rounded = round(taxed / 5) * 5
        return max(rounded, minimum_charge)
