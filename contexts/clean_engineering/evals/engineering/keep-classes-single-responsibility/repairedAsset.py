"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
class CartTotal:
    def subtotal(self, line_items):
        return sum(item.extended_price for item in line_items)
