"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
def checkout(cart):
    if cart.is_empty():
        return None
    return cart.subtotal()
