"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
def checkout(cart):
    # Loyalty discount applies only after the configured threshold.
    return cart.subtotal()
