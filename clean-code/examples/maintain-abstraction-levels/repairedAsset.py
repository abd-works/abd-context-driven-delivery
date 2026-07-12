"""
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
"""
def orchestrate_checkout(cart, payment_gateway):
    total = cart.subtotal()
    return payment_gateway.charge(total)
