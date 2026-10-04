def place_order(cart, payment, address):
    return payment.charge(cart.subtotal())
