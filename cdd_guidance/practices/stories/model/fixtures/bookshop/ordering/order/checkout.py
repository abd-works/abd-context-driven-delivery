from __future__ import annotations


@domain_service
class Checkout:
    """Module: Ordering | custom · Order
    Checking out belongs to neither the Cart nor the Order alone: it closes the one and opens the other."""

    carts: CartRepository
    orders: OrderRepository
    factory: OrderFactory

    def __init__(self, carts: CartRepository, orders: OrderRepository, factory: OrderFactory) -> None:
        self.carts = carts
        self.orders = orders
        self.factory = factory

    def checkOut(self, cartId: CartId, deliveryAddress: Address) -> Order:
        cart = self.carts.load(cartId)
        order = self.factory.create(cart, deliveryAddress)
        self.orders.update(order)
        return order
