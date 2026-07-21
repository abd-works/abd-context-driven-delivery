"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
class CartTotal:
    def subtotal(self, line_items):
        return sum(item.extended_price for item in line_items)
