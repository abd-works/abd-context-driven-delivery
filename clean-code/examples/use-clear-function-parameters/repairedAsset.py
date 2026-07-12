"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def place_order(cart, payment_gateway):
    return payment_gateway.charge(cart.subtotal())
