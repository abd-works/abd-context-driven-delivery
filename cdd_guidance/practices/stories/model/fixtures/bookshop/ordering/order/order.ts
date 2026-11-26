// === Ordering | custom · Order ===

/**
 * Module: Ordering | custom · Order
 * ---<<Open Host / Published Language>>--> Shipment
 * context: Fulfilment
 * aggregate: Shipment
 * entity: Shipment
 * held_by: OrderId
 * crosses: the paid order's lines and delivery address
 * integration: Order.pay
 */
@AggregateRoot()
@Entity()
class Order {
  orderId: OrderId;
  customerId: CustomerId;
  deliveryAddress: Address;
  // << composition >>
  payment: Payment;
  // << association >>
  // held by identity — the Cart it was checked out from
  cartId: CartId;

  constructor(orderId: OrderId, customerId: CustomerId, deliveryAddress: Address, payment: Payment, cartId: CartId) {
    this.orderId = orderId;
    this.customerId = customerId;
    this.deliveryAddress = deliveryAddress;
    this.payment = payment;
    this.cartId = cartId;
  }

  /** a paid order is handed to Fulfilment */
  pay(amount: Money): Payment {
    Payment.settle();
    throw new Error("not implemented");
  }

  /** an order already shipped is refused */
  cancel(reason: Reason): void {
    throw new Error("not implemented");
  }
}

/**
 * Module: Ordering | custom · Order
 */
@Repository()
class OrderRepository {
  // << aggregation >>
  orders: Collection<Order>;

  constructor(orders: Collection<Order>) {
    this.orders = orders;
  }

  create(cart: Cart): Order {
    throw new Error("not implemented");
  }

  load(orderId: OrderId): Order {
    throw new Error("not implemented");
  }

  update(order: Order): void {
    throw new Error("not implemented");
  }

  /** the Customer looks up their own orders */
  search(customerId: CustomerId): Order[] {
    throw new Error("not implemented");
  }
}

/**
 * Module: Ordering | custom · Order
 */
@Entity()
class Payment {
  paymentId: PaymentId;
  amount: Money;
  settled: boolean;

  constructor(paymentId: PaymentId, amount: Money, settled: boolean) {
    this.paymentId = paymentId;
    this.amount = amount;
    this.settled = settled;
  }

  settle(): void {
    throw new Error("not implemented");
  }
}
