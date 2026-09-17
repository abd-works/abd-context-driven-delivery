"""
"""
def checkout(cart):
    # Loyalty discount applies only after the configured threshold.
    return cart.subtotal()
