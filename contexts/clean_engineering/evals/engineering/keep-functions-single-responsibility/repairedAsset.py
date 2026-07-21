"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
def subtotal(line_items):
    return sum(item.extended_price for item in line_items)
