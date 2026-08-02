"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
"""
TAX_RATE = 0.13

def apply_tax(subtotal):
    return subtotal * TAX_RATE
