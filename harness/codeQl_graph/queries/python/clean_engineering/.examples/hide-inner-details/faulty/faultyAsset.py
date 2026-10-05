class Cart:
    def __init__(self):
        self._items = []

    def size(self):
        return len(self._items)

    def cached_size(self):
        return type(self)._items

    def class_size(self):
        return self.__class__._items

    class _Tally:
        def __init__(self, host: "Cart"):
            self._host = host

        def tally(self):
            return len(self._host._items)


class Checkout:
    def total(self, cart):
        return len(cart._items)
