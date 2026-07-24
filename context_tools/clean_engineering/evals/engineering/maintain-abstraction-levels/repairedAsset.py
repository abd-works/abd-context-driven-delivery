"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
"""
def orchestrate_checkout(cart, payment_gateway):
    total = cart.subtotal()
    return payment_gateway.charge(total)
