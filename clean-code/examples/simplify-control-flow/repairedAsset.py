"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def checkout(cart):
    if cart.is_empty():
        return None
    return cart.subtotal()
