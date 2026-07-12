// ============================================================================
// Instructions (remove this block before committing to production)
//
// This template shows the canonical layout for a clean production Java module.
// Steps:
//   1. Replace <domain_area> with the sub-epic or bounded context name.
//   2. Replace each domain class with entities from your story's domain model.
//   3. Replace placeholder method names with domain responsibility verbs.
//   4. Delete this Instructions block.
//   5. Run peer-review against abd-clean-code rules before opening a PR.
//
// Layout (one file per domain entity for larger modules; grouped by area otherwise):
//   Package declaration
//   Imports              (java.* -> third-party -> local)
//   DOMAIN CONSTANTS     (public static final, no magic numbers)
//   DOMAIN EXCEPTIONS    (named for what went wrong in the domain)
//   DOMAIN ENTITIES      (classes that own both state AND behaviour)
//     constructor        (accept infrastructure deps via injection; no construction inside)
//     getters / property-like accessors  (what the object IS / CONTAINS)
//     public methods     (what the object CAN DO -- domain verbs)
//     private helpers    (implementation details, under 20 lines each)
//
// KEY RULE: domain logic belongs on domain objects, not in services.
// A Cart knows its own subtotal. An Order knows whether it is confirmed.
// A service that accepts a pile of DTOs and does all the work is the
// Anemic Domain Model anti-pattern -- avoid it.
// ============================================================================

package com.example.<domainarea>;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

// ============================================================================
// DOMAIN CONSTANTS
// ============================================================================

public final class CartConstants {
    public static final double TAX_RATE = 0.13;              // GST/HST applied to all orders
    public static final double MAX_LOYALTY_DISCOUNT = 0.40;  // loyalty programme cap
    public static final int LOYALTY_THRESHOLD = 1000;        // cumulative spend that unlocks loyalty pricing

    private CartConstants() { }
}


// ============================================================================
// DOMAIN EXCEPTIONS
// ============================================================================

class CartError extends RuntimeException {
    CartError(String message) { super(message); }
}

class EmptyCartError extends CartError {
    EmptyCartError(String message) { super(message); }
}

class InvalidQuantityError extends CartError {
    InvalidQuantityError(String sku, int qty) {
        super(String.format("Invalid quantity %d for product %s", qty, sku));
    }
}

class OrderError extends RuntimeException {
    OrderError(String message) { super(message); }
}

class OrderAlreadyConfirmedError extends OrderError {
    OrderAlreadyConfirmedError(String message) { super(message); }
}


// ============================================================================
// DOMAIN ENTITY: Product
//
// A Product owns its own price. No other class stores a copy of it.
// ============================================================================

final class Product {

    private final String sku;
    private final String name;
    private final double price;

    Product(String sku, String name, double price) {
        this.sku = Objects.requireNonNull(sku);
        this.name = Objects.requireNonNull(name);
        this.price = price;
    }

    public String getSku()   { return sku; }
    public String getName()  { return name; }
    public double getPrice() { return price; }
}


// ============================================================================
// DOMAIN ENTITY: LineItem
//
// A LineItem is a chosen quantity of a Product.
// It gets its price from the Product -- it does not store a duplicate.
// ============================================================================

final class LineItem {

    private final Product product;
    private final int qty;

    LineItem(Product product, int qty) {
        if (qty < 1) {
            throw new InvalidQuantityError(product.getSku(), qty);
        }
        this.product = product;
        this.qty = qty;
    }

    public Product getProduct() { return product; }
    public int getQty()         { return qty; }

    // Price comes from the Product -- not a stored copy.
    public double getExtendedPrice() {
        return round(product.getPrice() * qty);
    }

    private static double round(double v) {
        return Math.round(v * 100.0) / 100.0;
    }
}


// ============================================================================
// DOMAIN ENTITY: Cart
//
// A Cart owns its items and all pricing logic for those items.
// It knows whether it is empty, what it costs, and how to become an Order.
// Collaborators injected via constructor: none -- Cart is a pure domain object.
// ============================================================================

final class Cart {

    private final User owner;
    private final List<LineItem> items = new ArrayList<>();

    Cart(User owner) {
        this.owner = Objects.requireNonNull(owner);
    }

    // --- Properties -- what this Cart IS -----------------------------------

    public User getOwner()               { return owner; }
    public List<LineItem> getItems()     { return Collections.unmodifiableList(items); }
    public boolean isEmpty()             { return items.isEmpty(); }

    public double getSubtotal() {
        double sum = 0.0;
        for (LineItem item : items) {
            sum += item.getExtendedPrice();
        }
        return round(sum);
    }

    // --- Domain responsibilities -- what this Cart CAN DO ------------------

    public void add(Product product, int qty) {
        items.add(new LineItem(product, qty));
    }

    public void remove(String sku) {
        items.removeIf(item -> item.getProduct().getSku().equals(sku));
    }

    public Order placeOrder() {
        if (isEmpty()) {
            throw new EmptyCartError("Cannot place an order from an empty cart.");
        }
        return new Order(owner, List.copyOf(items));
    }

    private static double round(double v) {
        return Math.round(v * 100.0) / 100.0;
    }
}


// ============================================================================
// DOMAIN ENTITY: Order
//
// An Order owns its pricing, tax, and confirmation lifecycle.
// It knows its own total; no service calculates this on its behalf.
// Collaborators injected via constructor: none -- Order is a pure domain object.
// ============================================================================

final class Order {

    private final User owner;
    private final List<LineItem> items;
    private boolean confirmed = false;

    Order(User owner, List<LineItem> items) {
        this.owner = Objects.requireNonNull(owner);
        this.items = List.copyOf(items);
    }

    // --- Properties -- what this Order IS ----------------------------------

    public User getOwner()            { return owner; }
    public List<LineItem> getItems()  { return items; }
    public boolean isConfirmed()      { return confirmed; }

    public double getSubtotal() {
        double sum = 0.0;
        for (LineItem item : items) {
            sum += item.getExtendedPrice();
        }
        return round(sum);
    }

    public double getTax() {
        return round(getSubtotal() * CartConstants.TAX_RATE);
    }

    public double getTotal() {
        return round(applyLoyaltyDiscount(getSubtotal() + getTax()));
    }

    // --- Domain responsibilities -- what this Order CAN DO -----------------

    public void confirm() {
        if (confirmed) {
            throw new OrderAlreadyConfirmedError("Order is already confirmed.");
        }
        confirmed = true;
    }

    // --- Private helpers ---------------------------------------------------

    private double applyLoyaltyDiscount(double amount) {
        if (owner.getLifetimeSpend() < CartConstants.LOYALTY_THRESHOLD) {
            return amount;
        }
        double discount = Math.min(owner.getLoyaltyRate(), CartConstants.MAX_LOYALTY_DISCOUNT);
        return amount * (1 - discount);
    }

    private static double round(double v) {
        return Math.round(v * 100.0) / 100.0;
    }
}


// ============================================================================
// DOMAIN ENTITY: User  (stub -- replace with your real User)
// ============================================================================

final class User {

    private final String id;
    private final String email;
    private final double lifetimeSpend;
    private final double loyaltyRate;

    User(String id, String email, double lifetimeSpend, double loyaltyRate) {
        this.id = id;
        this.email = email;
        this.lifetimeSpend = lifetimeSpend;
        this.loyaltyRate = loyaltyRate;
    }

    public String getId()             { return id; }
    public String getEmail()          { return email; }
    public double getLifetimeSpend()  { return lifetimeSpend; }
    public double getLoyaltyRate()    { return loyaltyRate; }
}
