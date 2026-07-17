"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def checkout_total(line_items):
    return sum(line_item.extended_price for line_item in line_items)
