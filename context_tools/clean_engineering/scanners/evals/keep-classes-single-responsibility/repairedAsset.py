"""
"""
class CartTotal:
    def subtotal(self, line_items):
        return sum(item.extended_price for item in line_items)
