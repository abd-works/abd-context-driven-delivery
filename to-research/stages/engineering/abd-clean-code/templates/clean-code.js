/**
 * ## Instructions (remove this block before committing to production)
 *
 * This template shows the canonical layout for a clean production ES module.
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
// <domainArea>.js
//
// Domain area   : <e.g. cart, order, inventory>
// Responsibilities: <list the domain behaviours this module covers>
// ============================================================================

// third-party  (add as needed)
// import { something } from 'some-package';

// local
// import { Symbol } from '../path/to/module.js';

// ============================================================================
// DOMAIN CONSTANTS
// ============================================================================

const TAX_RATE = 0.13;              // GST/HST applied to all orders
const MAX_LOYALTY_DISCOUNT = 0.40;  // loyalty programme cap
const LOYALTY_THRESHOLD = 1000;     // cumulative spend that unlocks loyalty pricing

// ============================================================================
// DOMAIN ENTITY: Product
//
// A Product owns its own price. No other class stores a copy of it.
// ============================================================================

export class Product {
  constructor(sku, name, price) {
    this.sku = sku;
    this.name = name;
    this.price = price;
  }
}

// ============================================================================
// DOMAIN ENTITY: LineItem
//
// A LineItem is a chosen quantity of a Product.
// It gets its price from the Product -- it does not store a duplicate.
// ============================================================================

export class LineItem {
  /** @type {Product} */ #product;
  /** @type {number}  */ #qty;

  /** @param {Product} product  @param {number} qty */
  constructor(product, qty) {
    if (qty < 1) throw new InvalidQuantityError(product.sku, qty);
    this.#product = product;
    this.#qty = qty;
  }

  get product() { return this.#product; }

  get qty() { return this.#qty; }

  /** Price comes from the Product -- not a stored copy. */
  get extendedPrice() {
    return this.#round(this.#product.price * this.#qty);
  }

  #round(value) { return Math.round(value * 100) / 100; }
}

export class CartError extends Error {
  constructor(message) {
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
  constructor(sku, qty) {
    super(`Quantity for '${sku}' must be at least 1, got ${qty}.`);
    this.name = 'InvalidQuantityError';
  }
}

export class OrderError extends Error {
  constructor(message) {
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
// DOMAIN ENTITY: Cart
//
// A Cart owns its items and all pricing logic for those items.
// It knows whether it is empty, what it costs, and how to become an Order.
// No infrastructure dependencies -- Cart is a pure domain object.
// ============================================================================

export class Cart {
  /** @type {object} */ #owner;
  /** @type {Array}  */ #items;

  /** @param {object} owner */
  constructor(owner) {
    this.#owner = owner;
    this.#items = [];
  }

  // ------------------------------------------------------------------
  // Getters -- what this Cart IS
  // ------------------------------------------------------------------

  get owner() { return this.#owner; }

  get items() { return [...this.#items]; }

  get isEmpty() { return this.#items.length === 0; }

  get subtotal() {
    return this.#round(this.#items.reduce((sum, i) => sum + i.extendedPrice, 0));
  }

  // ------------------------------------------------------------------
  // Domain responsibilities -- what this Cart CAN DO
  // ------------------------------------------------------------------

  /** Add a quantity of a product to the cart. Throws InvalidQuantityError if qty < 1. */
  add(product, qty) {
    this.#items.push(new LineItem(product, qty));
  }

  /** Remove all line items whose product matches sku. */
  remove(sku) {
    this.#items = this.#items.filter(i => i.product.sku !== sku);
  }

  /** Convert this cart into an Order, or throw EmptyCartError. */
  placeOrder() {
    if (this.isEmpty) throw new EmptyCartError();
    return new Order(this.#owner, this.items);
  }

  // ------------------------------------------------------------------
  // Private helpers
  // ------------------------------------------------------------------

  #round(value) {
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
  /** @type {object}        */ #owner;
  /** @type {Array}         */ #items;
  /** @type {boolean}       */ #confirmed;

  /**
   * @param {object} owner
   * @param {Array}  items  -- snapshot of cart items at placement time
   */
  constructor(owner, items) {
    this.#owner = owner;
    this.#items = items;
    this.#confirmed = false;
  }

  // ------------------------------------------------------------------
  // Getters -- what this Order IS
  // ------------------------------------------------------------------

  get owner() { return this.#owner; }

  get items() { return [...this.#items]; }

  get subtotal() {
    return this.#round(this.#items.reduce((sum, i) => sum + i.extendedPrice, 0));
  }

  get tax() {
    return this.#round(this.subtotal * TAX_RATE);
  }

  get total() {
    return this.#round(this.#applyLoyaltyDiscount(this.subtotal + this.tax));
  }

  get isConfirmed() { return this.#confirmed; }

  // ------------------------------------------------------------------
  // Domain responsibilities -- what this Order CAN DO
  // ------------------------------------------------------------------

  /** Mark this order as confirmed. */
  confirm() {
    if (this.#confirmed) throw new OrderAlreadyConfirmedError();
    this.#confirmed = true;
  }

  // ------------------------------------------------------------------
  // Private helpers
  // ------------------------------------------------------------------

  #applyLoyaltyDiscount(amount) {
    if (this.#owner.lifetimeSpend < LOYALTY_THRESHOLD) return amount;
    const rate = Math.min(this.#owner.loyaltyRate, MAX_LOYALTY_DISCOUNT);
    return amount * (1 - rate);
  }

  #round(value) {
    return Math.round(value * 100) / 100;
  }
}
