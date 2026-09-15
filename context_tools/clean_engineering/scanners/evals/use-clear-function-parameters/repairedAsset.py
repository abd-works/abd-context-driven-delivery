"""
"""
def place_order(cart, payment_gateway):
    return payment_gateway.charge(cart.subtotal())
