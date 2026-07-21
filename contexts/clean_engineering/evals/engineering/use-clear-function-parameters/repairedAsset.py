"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
def place_order(cart, payment_gateway):
    return payment_gateway.charge(cart.subtotal())
