"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
"""
def checkout_total(line_items):
    return sum(item.extended_price for item in line_items)

def apply_discount(total):
    return total * 0.9
