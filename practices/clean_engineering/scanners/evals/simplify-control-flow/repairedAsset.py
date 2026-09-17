"""
"""
def checkout(cart):
    if cart.is_empty():
        return None
    return cart.subtotal()
