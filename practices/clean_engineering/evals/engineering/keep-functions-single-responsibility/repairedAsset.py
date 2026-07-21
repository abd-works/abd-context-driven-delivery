"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def subtotal(line_items):
    return sum(item.extended_price for item in line_items)
