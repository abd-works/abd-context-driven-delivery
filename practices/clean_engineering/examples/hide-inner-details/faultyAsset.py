class Cart:
    def __init__(self):
        self._items = []

    def size(self):
        return len(self._items)

    class _Tally:
        def __init__(self, host: "Cart"):
            self._host = host

        def tally(self):
            return len(self._host._items)


class Checkout:
    def total(self, cart):
        return len(cart._items)
