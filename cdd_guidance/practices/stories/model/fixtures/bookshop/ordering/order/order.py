from __future__ import annotations

# === Ordering | custom · Order ===

@aggregate_root
@entity
class Order:
    """Module: Ordering | custom · Order
---<<Open Host / Published Language>>--> Shipment
context: Fulfilment
aggregate: Shipment
entity: Shipment
held_by: OrderId
crosses: the paid order's lines and delivery address
integration: Order.pay"""

    orderId: OrderId
    customerId: CustomerId
    deliveryAddress: Address
    # << composition >>
    payment: Payment
    # << association >>
    # held by identity — the Cart it was checked out from
    cartId: CartId

    def __init__(self, orderId: OrderId, customerId: CustomerId, deliveryAddress: Address, payment: Payment, cartId: CartId) -> None:
        self.orderId = orderId
        self.customerId = customerId
        self.deliveryAddress = deliveryAddress
        self.payment = payment
        self.cartId = cartId

    def pay(self, amount: Money) -> Payment:
        """a paid order is handed to Fulfilment"""
        Payment.settle()
        raise NotImplementedError

    def cancel(self, reason: Reason) -> void:
        """an order already shipped is refused"""
        raise NotImplementedError


@repository
class OrderRepository:
    """Module: Ordering | custom · Order"""

    # << aggregation >>
    orders: Collection[Order]

    def __init__(self, orders: Collection[Order]) -> None:
        self.orders = orders

    def create(self, cart: Cart) -> Order:
        raise NotImplementedError

    def load(self, orderId: OrderId) -> Order:
        raise NotImplementedError

    def update(self, order: Order) -> void:
        raise NotImplementedError

    def search(self, customerId: CustomerId) -> list[Order]:
        """the Customer looks up their own orders"""
        raise NotImplementedError


@entity
class Payment:
    """Module: Ordering | custom · Order"""

    paymentId: PaymentId
    amount: Money
    settled: boolean

    def __init__(self, paymentId: PaymentId, amount: Money, settled: boolean) -> None:
        self.paymentId = paymentId
        self.amount = amount
        self.settled = settled

    def settle(self) -> void:
        raise NotImplementedError
