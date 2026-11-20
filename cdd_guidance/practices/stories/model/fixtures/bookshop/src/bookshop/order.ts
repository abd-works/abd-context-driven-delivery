/** Order. The books a Customer bought, and what the Customer sees once it is submitted. */

export class OrderNotFound extends Error {
  constructor(public readonly orderNumber: string) {
    super(`order ${orderNumber} is not found`);
  }
}

export class OrderConfirmation {
  constructor(
    public readonly orderNumber: string,
    public readonly total: number,
    public readonly status: string,
  ) {}
}

export class Order {
  public status = "submitted";

  constructor(
    public readonly orderNumber: string,
    public readonly total: number,
  ) {}

  confirmation(): OrderConfirmation {
    return new OrderConfirmation(this.orderNumber, this.total, this.status);
  }

  cancel(): void {
    this.status = "cancelled";
  }
}

export class OrderRepository {
  private readonly orders = new Map<string, Order>();

  create(order: Order): Order {
    this.orders.set(order.orderNumber, order);
    return order;
  }

  load(orderNumber: string): Order {
    const order = this.orders.get(orderNumber);
    if (!order) throw new OrderNotFound(orderNumber);
    return order;
  }
}
