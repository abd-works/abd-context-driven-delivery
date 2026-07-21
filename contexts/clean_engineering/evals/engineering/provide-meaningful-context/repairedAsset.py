"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
TAX_RATE = 0.13

def apply_tax(subtotal):
    return subtotal * TAX_RATE
