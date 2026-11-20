from __future__ import annotations


@domain_event
class OrderPaid:
    """Module: Ordering | custom · Order
    Published by Order.pay; consumed by Shipment in Fulfilment. Carries the order's identity and delivery address."""

    orderId: OrderId
    deliveryAddress: Address

    def __init__(self, orderId: OrderId, deliveryAddress: Address) -> None:
        self.orderId = orderId
        self.deliveryAddress = deliveryAddress
