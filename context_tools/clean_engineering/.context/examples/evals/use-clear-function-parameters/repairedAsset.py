"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
"""
def place_order(cart, payment_gateway):
    return payment_gateway.charge(cart.subtotal())
