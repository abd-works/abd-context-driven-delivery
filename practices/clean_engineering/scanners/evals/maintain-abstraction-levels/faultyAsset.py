def orchestrate_checkout(cart, payment_gateway):
    with open("audit.log", "w") as audit:
        audit.write(str(cart.subtotal()))
    return payment_gateway.charge(cart.subtotal())
