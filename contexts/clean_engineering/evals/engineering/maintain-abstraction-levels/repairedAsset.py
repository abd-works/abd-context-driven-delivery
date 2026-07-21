"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
def orchestrate_checkout(cart, payment_gateway):
    total = cart.subtotal()
    return payment_gateway.charge(total)
