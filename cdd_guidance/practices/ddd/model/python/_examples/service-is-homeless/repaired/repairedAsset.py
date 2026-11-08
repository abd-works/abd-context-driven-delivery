# <<Entity>>
class Cart:
    def add(self):
        return None

    def place_order(self):
        return self.add()


# <<Domain Service>>
class PricingService:
    def quote(self, cart: Cart, rate: int) -> int:
        total = rate * 2
        return total
