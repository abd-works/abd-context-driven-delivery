def checkout(cart):
    if cart:
        if not cart.is_empty():
            if cart.has_items():
                if cart.subtotal() > 0:
                    if cart.owner:
                        return cart.subtotal()
    return None
