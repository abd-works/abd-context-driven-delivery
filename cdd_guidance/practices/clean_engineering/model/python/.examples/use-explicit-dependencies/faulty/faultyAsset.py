class CartRepository:
    pass


class Cart:
    def __init__(self):
        self._repository = CartRepository()
