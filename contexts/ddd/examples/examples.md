# Examples — DDD

---

# Bounded Context Map — Shop

## Catalog

- **Owning team:** Merchandising
- **Scope:** Product identity and pricing.
- **Implementation:** monolith module

### Product

- **Root:** Product
- **Boundary members:** none beyond Product
- **Protected invariants:** price always non-negative
- **Cross-aggregate refs:** ShoppingCart (by ID) — consistency: snapshot; unit price locked at add_item

## Sales

- **Owning team:** Checkout
- **Scope:** Shopping carts, checkout, discounts.
- **Implementation:** monolith module

### ShoppingCart

- **Root:** ShoppingCart
- **Boundary members:** CartItem, Discount — total and checkout invariants span the cart
- **Protected invariants:** once checked out, cart may not be modified; discount may not reduce total below zero
- **Cross-aggregate refs:** Customer (by ID), Inventory (by ID) — consistency: eventual on stock

#### **ShoppingCart** <<Aggregate Root>> <<Entity>>

+ ShoppingCart(customer: CustomerId)
------
+ << identifier >> customer: CustomerId                 # by ID — cross-aggregate
+ << composition >> items: list[CartItem]
+ << association >> discount: Discount | None
+ checked_out: bool
	Invariant: Once true, never reverts to false.
----
+ add_item(product: ProductId, quantity: int, unit_price: Decimal): None
	Invariant: Cart may not be modified after checkout.
	Invariant: Quantity must be at least 1.
+ remove_item(product: ProductId): None
	Invariant: Cart may not be modified after checkout.
+ apply_discount(discount: Discount): None
	Invariant: Cart may not be modified after checkout.
+ compute_total(): Decimal
+ checkout(inventory: Inventory): None
	Invariant: May not be called when already checked out.
- _find_item(product: ProductId): CartItem | None

#### **CartItem** <<Value Object>>

+ CartItem(product: ProductId, quantity: int, unit_price: Decimal)
------
+ product: ProductId                                    # by ID — snapshot at add time
+ quantity: int
	Invariant: quantity >= 1.
+ unit_price: Decimal
	Invariant: unit_price >= 0. Immutable — replace, do not update in place.
----
+ line_total(): Decimal
+ update_quantity(quantity: int): None

#### **Discount** <<Value Object>> <<Specification>>

+ Discount(code: str, reduction: Decimal)
------
+ code: str
+ reduction: Decimal
	Invariant: reduction > 0.
----
+ is_valid(cart: ShoppingCart): bool
+ compute_reduction(subtotal: Decimal): Decimal
	Invariant: Total may not be reduced below zero.

#### **ShoppingCartRepository** <<Repository>>

+ ShoppingCartRepository()
------
----
+ add(cart: ShoppingCart): None
+ remove(cart: ShoppingCart): None
+ update(cart: ShoppingCart): None
+ find_by_customer(customer: CustomerId): ShoppingCart | None

#### **CartCheckedOut** <<Domain Event>>

+ CartCheckedOut(cart_id: CartId, customer: CustomerId, total: Decimal, checked_out_at: DateTime)
------
+ cart_id: CartId
+ customer: CustomerId
+ total: Decimal
+ checked_out_at: DateTime
	Invariant: Raised when ShoppingCart.checkout succeeds.
	Invariant: Consumers are Inventory (assert/reserve) and Notifications (receipt).
----

## Dependencies

### Catalog → Sales

- **Direction:** Catalog is upstream; Sales is downstream
- **What crosses:** product identity and unit price into cart lines
- **How they integrate:** Synchronous call — at `add_item`, Sales reads `Catalog.Product.unit_price` and stores a snapshot on the line
- **Relationship pattern:** Customer/Supplier
- **Rationale:** Later Catalog price changes do not rewrite open carts
