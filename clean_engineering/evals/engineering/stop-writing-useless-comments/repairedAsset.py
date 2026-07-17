"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def checkout(cart):
    # Loyalty discount applies only after the configured threshold.
    return cart.subtotal()
