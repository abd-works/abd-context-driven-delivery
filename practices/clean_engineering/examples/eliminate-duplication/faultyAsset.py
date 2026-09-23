class Totals:
    def subtotal(self, items):
        total = 0
        for item in items:
            total += item.price
        return total

    def backup_subtotal(self, items):
        total = 0
        for item in items:
            total += item.price
        return total
