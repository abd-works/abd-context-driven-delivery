def place_order(cart, payment_gateway, data):
    return payment_gateway.charge(cart.subtotal())
