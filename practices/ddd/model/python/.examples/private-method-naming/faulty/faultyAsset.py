class Cart:
    def add(self):
        return self._hide()

    def _hide(self):
        return None


class Other:
    def poke(self, cart: Cart):
        return cart._hide()
