from cart.cart import Cart, Line, Price


class Checkout:
    def total(self, cart: Cart, line: Line) -> Price:
        cart.add(line)
        return line.price()
