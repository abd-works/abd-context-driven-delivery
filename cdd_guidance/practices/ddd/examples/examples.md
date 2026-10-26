# Examples — DDD

---

# Bounded Context Map — Shop

## Catalog | custom

Product identity and pricing — slower-changing than checkout.

### Product

- Product
→ Sales · ShoppingCart · CartItem

## Sales | custom

Shopping carts, checkout, discounts.

### ShoppingCart

- CartItem
- Discount
- unit_price snapshot → Catalog · Product
→ Catalog · Product

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
