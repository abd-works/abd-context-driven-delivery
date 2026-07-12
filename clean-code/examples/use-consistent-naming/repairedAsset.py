"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def checkout_total(line_items):
    return sum(item.extended_price for item in line_items)

def apply_discount(total):
    return total * 0.9
