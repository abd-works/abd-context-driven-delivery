/**
 * ## Instructions (remove this block before committing to production)
 *
 * This template shows the canonical layout for a clean production TypeScript module.
 * Steps:
 *   1. Replace <domainArea> with the sub-epic or bounded context name (camelCase file).
 *   2. Replace each domain class with entities from your story's domain model.
 *   3. Replace placeholder method names with domain responsibility verbs.
 *   4. Delete this Instructions block.
 *   5. Run peer-review against abd-clean-code rules before opening a PR.
 *
 * Layout:
 *   Module comment      (domain area + responsibilities)
 *   Imports             (stdlib -> third-party -> local)
 *   DOMAIN TYPES        (interfaces for collaborators and value shapes)
 *   DOMAIN CONSTANTS    (named constants, no magic numbers)
 *   DOMAIN EXCEPTIONS   (extend Error with domain names)
 *   DOMAIN ENTITIES     (classes that own both state AND behaviour)
 *     constructor       (injection only, private #fields)
 *     getters           (what the object IS / CONTAINS)
 *     public methods    (what the object CAN DO -- domain verbs)
 *     #private helpers  (implementation details, under 20 lines each)
 *
 * KEY RULE: domain logic belongs on domain objects, not in services.
 * A Cart knows its own subtotal. An Order knows whether it is confirmed.
 * A service that accepts a pile of plain objects and does all the work is the
 * Anemic Domain Model anti-pattern -- avoid it.
 */

// ============================================================================
// <domainArea>.ts
//
// Domain area   : <e.g. cart, order, inventory>
// Responsibilities: <list the domain behaviours this module covers>
// ============================================================================

// third-party  (add as needed)
// import { something } from 'some-package';

// local
// import { Symbol } from '../path/to/module.js';

// ============================================================================
// DOMAIN TYPES
// ============================================================================

export interface Customer {
  lifetimeSpend: number;
  loyaltyRate: number;
}

// ============================================================================
// DOMAIN CONSTANTS
// ============================================================================

const TAX_RATE = 0.13;              // GST/HST applied to all orders
const MAX_LOYALTY_DISCOUNT = 0.40;  // loyalty programme cap
const LOYALTY_THRESHOLD = 1000;     // cumulative spend that unlocks loyalty pricing

// ============================================================================
// DOMAIN EXCEPTIONS
// ============================================================================

export class CartError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CartError';
  }
}

export class EmptyCartError extends CartError {
  constructor() {
    super('Cannot place an order from an empty cart.');
    this.name = 'EmptyCartError';
  }
}

export class InvalidQuantityError extends CartError {
  constructor(sku: string, qty: number) {
    super(`Quantity for '${sku}' must be at least 1, got ${qty}.`);
    this.name = 'InvalidQuantityError';
  }
}

export class OrderError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OrderError';
  }
}

export class OrderAlreadyConfirmedError extends OrderError {
  constructor() {
    super('Order is already confirmed.');
    this.name = 'OrderAlreadyConfirmedError';
  }
}

// ============================================================================
// DOMAIN ENTITY: Product
//
// A Product owns its own price. No other class stores a copy of it.
// ============================================================================

export class Product {
  constructor(
    readonly sku: string,
    readonly name: string,
    readonly price: number,
  ) {}
}

// ============================================================================
// DOMAIN ENTITY: LineItem
//
// A LineItem is a chosen quantity of a Product.
// It gets its price from the Product -- it does not store a duplicate.
// ============================================================================

export class LineItem {
  readonly #product: Product;
  readonly #qty: number;

  constructor(product: Product, qty: number) {
    if (qty < 1) throw new InvalidQuantityError(product.sku, qty);
    this.#product = product;
    this.#qty = qty;
  }

  get product(): Product {
    return this.#product;
  }

  get qty(): number {
    return this.#qty;
  }

  /** Price comes from the Product -- not a stored copy. */
  get extendedPrice(): number {
    return this.#round(this.#product.price * this.#qty);
  }

  #round(value: number): number {
    return Math.round(value * 100) / 100;
  }
}

// ============================================================================
// DOMAIN ENTITY: Cart
//
// A Cart owns its items and all pricing logic for those items.
// It knows whether it is empty, what it costs, and how to become an Order.
// No infrastructure dependencies -- Cart is a pure domain object.
// ============================================================================

export class Cart {
  readonly #owner: Customer;
  #items: LineItem[];

  constructor(owner: Customer) {
    this.#owner = owner;
    this.#items = [];
  }

  // ------------------------------------------------------------------
  // Getters -- what this Cart IS
  // ------------------------------------------------------------------

  get owner(): Customer {
    return this.#owner;
  }

  get items(): readonly LineItem[] {
    return [...this.#items];
  }

  get isEmpty(): boolean {
    return this.#items.length === 0;
  }

  get subtotal(): number {
    return this.#round(this.#items.reduce((sum, item) => sum + item.extendedPrice, 0));
  }

  // ------------------------------------------------------------------
  // Domain responsibilities -- what this Cart CAN DO
  // ------------------------------------------------------------------

  /** Add a quantity of a product to the cart. Throws InvalidQuantityError if qty < 1. */
  add(product: Product, qty: number): void {
    this.#items.push(new LineItem(product, qty));
  }

  /** Remove all line items whose product matches sku. */
  remove(sku: string): void {
    this.#items = this.#items.filter((item) => item.product.sku !== sku);
  }

  /** Convert this cart into an Order, or throw EmptyCartError. */
  placeOrder(): Order {
    if (this.isEmpty) throw new EmptyCartError();
    return new Order(this.#owner, this.items);
  }

  // ------------------------------------------------------------------
  // Private helpers
  // ------------------------------------------------------------------

  #round(value: number): number {
    return Math.round(value * 100) / 100;
  }
}

// ============================================================================
// DOMAIN ENTITY: Order
//
// An Order owns its pricing, tax, and confirmation lifecycle.
// It knows its own total; no service calculates this on its behalf.
// No infrastructure dependencies -- Order is a pure domain object.
// ============================================================================

export class Order {
  readonly #owner: Customer;
  readonly #items: readonly LineItem[];
  #confirmed: boolean;

  /** @param items snapshot of cart items at placement time */
  constructor(owner: Customer, items: readonly LineItem[]) {
    this.#owner = owner;
    this.#items = items;
    this.#confirmed = false;
  }

  // ------------------------------------------------------------------
  // Getters -- what this Order IS
  // ------------------------------------------------------------------

  get owner(): Customer {
    return this.#owner;
  }

  get items(): readonly LineItem[] {
    return [...this.#items];
  }

  get subtotal(): number {
    return this.#round(this.#items.reduce((sum, item) => sum + item.extendedPrice, 0));
  }

  get tax(): number {
    return this.#round(this.subtotal * TAX_RATE);
  }

  get total(): number {
    return this.#round(this.#applyLoyaltyDiscount(this.subtotal + this.tax));
  }

  get isConfirmed(): boolean {
    return this.#confirmed;
  }

  // ------------------------------------------------------------------
  // Domain responsibilities -- what this Order CAN DO
  // ------------------------------------------------------------------

  /** Mark this order as confirmed. */
  confirm(): void {
    if (this.#confirmed) throw new OrderAlreadyConfirmedError();
    this.#confirmed = true;
  }

  // ------------------------------------------------------------------
  // Private helpers
  // ------------------------------------------------------------------

  #applyLoyaltyDiscount(amount: number): number {
    if (this.#owner.lifetimeSpend < LOYALTY_THRESHOLD) return amount;
    const rate = Math.min(this.#owner.loyaltyRate, MAX_LOYALTY_DISCOUNT);
    return amount * (1 - rate);
  }

  #round(value: number): number {
    return Math.round(value * 100) / 100;
  }
}
