<!-- @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source. -->
<!-- invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->

<!--
  clean_engineering markdown examples — ShoppingCart domain — unified across all fidelities.
  Structure: H1 = module, H2 = class.
  Interface (I{Type}) and implementation ({Type}) sit together under the same module H1.
  Language companion and modules overview go as prose before the first H1.
-->

## Language companion                                             <!-- L -->

*ShoppingCart* is a running tally of what a customer intends to buy in a single shopping session.

### shopping_cart                                                  <!-- L -->

- Belongs to exactly one *Customer* whose identity anchors the cart. <!-- L -->
- Collects *CartItems* as the customer browses and keeps the running total current. <!-- L -->
- Accepts an optional *Discount* applied before the total is computed. <!-- L -->
- **Invariant:** Once checked out, the cart may not be modified.  <!-- L -->

### discount                                                       <!-- L -->

- **Invariant:** A discount may not reduce the total below zero.  <!-- L -->

## Modules                                                        <!-- Mu -->

Build order: `inventory` → `cart`

---

# cart                                                            <!-- Mu -->

- **Purpose:** Owns the shopping-session tally and checkout gate. <!-- Mu -->
- **Seam (terms):** ShoppingCart, CartItem, Discount              <!-- Mu -->
- **Dependencies (one-way):** inventory                           <!-- Mu -->

## IShoppingCart                                                  <!-- Md -->

IShoppingCart(customer: Customer)
------
customer: Customer
items: list[CartItem]
discount: Discount | None
checked_out: bool
	Invariant: Once true, never reverts to false.
----
add_item(product: str, quantity: int, unit_price: Decimal): None
	Invariant: Cart may not be modified after checkout.
	Invariant: Quantity must be at least 1.
remove_item(product: str): None
	Invariant: Cart may not be modified after checkout.
apply_discount(discount: Discount): None
	Invariant: Cart may not be modified after checkout.
compute_total(): Decimal
checkout(inventory: Inventory): None
	Invariant: May not be called when already checked out.
- _find_item(product: str): CartItem | None

## ShoppingCart                                                   <!-- S -->

+ ShoppingCart(customer: Customer)
------
+ << association >> customer: Customer
+ << composition >> items: list[CartItem]
+ << association >> discount: Discount | None
+ checked_out: bool
	Invariant: Once true, never reverts to false.
----
+ add_item(product: str, quantity: int, unit_price: Decimal): None
	Invariant: Cart may not be modified after checkout.
	Invariant: Quantity must be at least 1.
	Interaction:
		existing: CartItem | None = _find_item(product)
		if existing: existing.update_quantity(quantity)
		else: items.append(CartItem(product, quantity, unit_price))
+ remove_item(product: str): None
	Invariant: Cart may not be modified after checkout.
+ apply_discount(discount: Discount): None
	Invariant: Cart may not be modified after checkout.
+ compute_total(): Decimal
	Interaction:
		subtotal: Decimal = sum(item.line_total() for item in items)
		return discount.compute_reduction(subtotal) if discount else subtotal
+ checkout(inventory: Inventory): None
	Invariant: May not be called when already checked out.
	Interaction:
		inventory.assert_available(items)
		checked_out = True
- _find_item(product: str): CartItem | None

## ICartItem                                                      <!-- Md -->

CartItem(product: str, quantity: int, unit_price: Decimal)
------
product: str
quantity: int
	Invariant: quantity >= 1.
unit_price: Decimal
	Invariant: unit_price >= 0.
----
line_total(): Decimal
update_quantity(quantity: int): None

## CartItem                                                       <!-- S -->

+ CartItem(product: str, quantity: int, unit_price: Decimal)
------
+ product: str
+ quantity: int
	Invariant: quantity >= 1.
+ unit_price: Decimal
	Invariant: unit_price >= 0.
----
+ line_total(): Decimal
	Interaction:
		return quantity * unit_price
+ update_quantity(quantity: int): None

## IDiscount                                                      <!-- Md -->

Discount(code: str, reduction: Decimal)
------
code: str
reduction: Decimal
	Invariant: reduction > 0.
----
is_valid(cart: ShoppingCart): bool
compute_reduction(subtotal: Decimal): Decimal
	Invariant: Total may not be reduced below zero.

## Discount                                                       <!-- S -->

+ Discount(code: str, reduction: Decimal)
------
+ code: str
+ reduction: Decimal
	Invariant: reduction > 0.
----
+ is_valid(cart: ShoppingCart): bool
+ compute_reduction(subtotal: Decimal): Decimal
	Invariant: Total may not be reduced below zero.
	Interaction:
		reduced: Decimal = subtotal - reduction
		return max(reduced, Decimal("0"))

---

# inventory                                                       <!-- Mu -->

- **Purpose:** Asserts stock availability at checkout.            <!-- Mu -->
- **Seam (terms):** Inventory                                     <!-- Mu -->
- **Dependencies (one-way):** *(none)*                            <!-- Mu -->

## IInventory                                                     <!-- Md -->

IInventory()
------
----
assert_available(items: list[CartItem]): None

## Inventory                                                      <!-- S -->

+ Inventory()
------
----
+ assert_available(items: list[CartItem]): None
