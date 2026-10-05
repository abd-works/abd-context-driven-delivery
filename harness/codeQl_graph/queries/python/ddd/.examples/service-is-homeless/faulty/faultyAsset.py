class CheckoutService:
    def place_order(self, cart):
        return cart.add()
