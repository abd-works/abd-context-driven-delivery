/**
 * Module: Ordering | custom · Order
 * Checking out belongs to neither the Cart nor the Order alone.
 */
@DomainService()
class Checkout {
  carts: CartRepository;
  orders: OrderRepository;

  constructor(carts: CartRepository, orders: OrderRepository) {
    this.carts = carts;
    this.orders = orders;
  }

  checkOut(cartId: CartId, deliveryAddress: Address): Order {
    const cart = this.carts.load(cartId);
    return this.orders.create(cart);
  }
}
