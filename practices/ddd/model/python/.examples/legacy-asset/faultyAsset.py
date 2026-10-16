class ProductData:
    sku: str
    price: int


class CheckoutScreen:
    def open(self):
        return True

    def isShowing(self):
        return True


class Cart:
    def add(self):
        return self._hide()

    def _hide(self):
        return None


class Other:
    def poke(self, cart: Cart):
        return cart._hide()


class LonelyType:
    def remember(self):
        return None


class CartManager:
    def run(self):
        return None


class CheckoutService:
    def place_order(self, cart: Cart):
        return cart.add()


class NoteRepository:
    def persist(self):
        return None


class CustomerRepository:
    def load(self):
        return None
