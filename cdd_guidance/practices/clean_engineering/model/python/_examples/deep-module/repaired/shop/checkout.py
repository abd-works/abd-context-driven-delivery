from cart.cart import Cart


class Checkout:
    def total(self, cart: Cart) -> int:
        return cart.total()
