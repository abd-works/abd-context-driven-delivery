"""
"""
def orchestrate_checkout(cart, payment_gateway):
    total = cart.subtotal()
    return payment_gateway.charge(total)
