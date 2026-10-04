class Cart:
    def __init__(self):
        self._items = []


class Checkout:
    def total(self, cart):
        return len(cart._items)
