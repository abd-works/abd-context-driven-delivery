class Cart:
    def add(self) -> None:
        return None


# <<Domain Service>>
class CheckoutService:
    def place_order(self, cart: Cart) -> None:
        return cart.add()
