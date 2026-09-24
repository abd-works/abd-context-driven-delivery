class Cart:
    def __init__(self):
        self._items = []

    def size(self):
        return len(self._items)


class Checkout:
    def total(self, cart):
        return len(cart._items)
