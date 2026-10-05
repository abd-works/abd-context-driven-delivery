class Cart:
    def subtotal(self):
        return 0


class CartFacade:
    def subtotal(self, cart):
        return cart.subtotal()
