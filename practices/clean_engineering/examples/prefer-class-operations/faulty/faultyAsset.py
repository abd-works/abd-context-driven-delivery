def _extended_price(item):
    return item.price * item.quantity


class Cart:
    def subtotal(self, item):
        return _extended_price(item)
