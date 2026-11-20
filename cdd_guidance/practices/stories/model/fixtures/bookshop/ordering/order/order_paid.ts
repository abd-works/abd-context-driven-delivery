/**
 * Module: Ordering | custom · Order
 * Published by Order.pay; consumed by Shipment in Fulfilment.
 */
@DomainEvent()
class OrderPaid {
  orderId: OrderId;
  deliveryAddress: Address;

  constructor(orderId: OrderId, deliveryAddress: Address) {
    this.orderId = orderId;
    this.deliveryAddress = deliveryAddress;
  }
}
