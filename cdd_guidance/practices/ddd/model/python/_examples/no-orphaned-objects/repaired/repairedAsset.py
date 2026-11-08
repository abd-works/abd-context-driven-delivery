# <<Entity>>
class Cart:
    def add(self):
        return Order()


# <<Entity>>
class Order:
    def hold(self):
        return Cart()
