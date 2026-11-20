/**
 * Module: Ordering | custom · Order
 * Builds an Order from a checked-out Cart.
 */
@Factory()
class OrderFactory {
  books: BookRepository;

  constructor(books: BookRepository) {
    this.books = books;
  }

  create(cart: Cart, deliveryAddress: Address): Order {
    this.books.load(cart.bookId);
    throw new Error("not implemented");
  }
}
