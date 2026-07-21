"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
def checkout_total(line_items):
    return sum(line_item.extended_price for line_item in line_items)
