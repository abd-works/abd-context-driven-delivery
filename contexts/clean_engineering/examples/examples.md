<!-- @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only. -->
<!-- invoke-edit: action satisfy | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->

<!--
  clean_engineering markdown examples — ShoppingCart domain — unified across all fidelities.
  Fidelity tags:
    L  = language companion (prose only; refined every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order)
    Md = model          (typed compact block / I{Class})
    S  = specification (relationship kinds, invariant sentences, interactions)
-->

# ShoppingCart                                                    <!-- L -->

---

## Language companion                                             <!-- L -->

*ShoppingCart* is a running tally of what a customer intends to buy in a single shopping session. <!-- L -->

### shopping_cart                                                  <!-- L -->

- Belongs to exactly one *Customer* whose identity anchors the cart. <!-- L -->
- Collects *CartItems* as the customer browses and keeps the running total current. <!-- L -->
- Accepts an optional *Discount* applied before the total is computed. <!-- L -->
- **Invariant:** Once checked out, the cart may not be modified.  <!-- L -->

### discount                                                       <!-- L -->

- **Invariant:** A discount may not reduce the total below zero.  <!-- L -->

---

## Modules fidelity                                               <!-- Mu -->

### Module `cart`                                                  <!-- Mu -->

- **Purpose:** Owns the shopping-session tally and checkout gate. <!-- Mu -->
- **Seam (terms):** ShoppingCart, CartItem, Discount              <!-- Mu -->
- **Dependencies (one-way):** inventory                           <!-- Mu -->

### Module `inventory`                                             <!-- Mu -->

- **Purpose:** Asserts stock availability at checkout.            <!-- Mu -->
- **Seam (terms):** Inventory                                     <!-- Mu -->
- **Dependencies (one-way):** *(none)*                            <!-- Mu -->

### Build order                                                    <!-- Mu -->

1. `inventory`                                                     <!-- Mu -->
2. `cart`                                                          <!-- Mu -->

---

## Model fidelity                                                 <!-- Md -->

### **IShoppingCart**                                              <!-- Md -->

IShoppingCart(customer: Customer)                                  <!-- Md -->
------
customer: Customer                                                 <!-- Md -->
items: list[CartItem]                                              <!-- Md -->
discount: Discount | None                                         <!-- Md -->
checked_out: bool                                                  <!-- Md -->
	Invariant: Once true, never reverts to false.                  <!-- Md -->
----
add_item(product: str, quantity: int, unit_price: Decimal): None  <!-- Md -->
	Invariant: Cart may not be modified after checkout.           <!-- Md -->
	Invariant: Quantity must be at least 1.                       <!-- Md -->
remove_item(product: str): None                                    <!-- Md -->
	Invariant: Cart may not be modified after checkout.           <!-- Md -->
apply_discount(discount: Discount): None                           <!-- Md -->
	Invariant: Cart may not be modified after checkout.           <!-- Md -->
compute_total(): Decimal                                           <!-- Md -->
checkout(inventory: Inventory): None                               <!-- Md -->
	Invariant: May not be called when already checked out.        <!-- Md -->
- _find_item(product: str): CartItem | None                       <!-- Md -->

### **CartItem**                                                  <!-- Md -->

CartItem(product: str, quantity: int, unit_price: Decimal)        <!-- Md -->
------
product: str                                                       <!-- Md -->
quantity: int                                                      <!-- Md -->
	Invariant: quantity >= 1.                                      <!-- Md -->
unit_price: Decimal                                                <!-- Md -->
	Invariant: unit_price >= 0.                                   <!-- Md -->
----
line_total(): Decimal                                              <!-- Md -->
update_quantity(quantity: int): None                               <!-- Md -->

### **Discount**                                                  <!-- Md -->

Discount(code: str, reduction: Decimal)                            <!-- Md -->
------
code: str                                                          <!-- Md -->
reduction: Decimal                                                 <!-- Md -->
	Invariant: reduction > 0.                                      <!-- Md -->
----
is_valid(cart: ShoppingCart): bool                                 <!-- Md -->
compute_reduction(subtotal: Decimal): Decimal                      <!-- Md -->
	Invariant: Total may not be reduced below zero.               <!-- Md -->

---

## Specification fidelity                                         <!-- S -->

### **ShoppingCart**                                              <!-- S -->

+ ShoppingCart(customer: Customer)                                 <!-- S -->
------
+ << association >> customer: Customer                             <!-- S -->
+ << composition >> items: list[CartItem]                          <!-- S -->
+ << association >> discount: Discount | None                      <!-- S -->
+ checked_out: bool                                                <!-- S -->
	Invariant: Once true, never reverts to false.                  <!-- S -->
----
+ add_item(product: str, quantity: int, unit_price: Decimal): None <!-- S -->
	Invariant: Cart may not be modified after checkout.           <!-- S -->
	Invariant: Quantity must be at least 1.                       <!-- S -->
	Interaction:                                                   <!-- S -->
		existing: CartItem | None = _find_item(product)           <!-- S -->
		if existing: existing.update_quantity(quantity)           <!-- S -->
		else: items.append(CartItem(product, quantity, unit_price)) <!-- S -->
+ remove_item(product: str): None                                  <!-- S -->
	Invariant: Cart may not be modified after checkout.           <!-- S -->
+ apply_discount(discount: Discount): None                         <!-- S -->
	Invariant: Cart may not be modified after checkout.           <!-- S -->
+ compute_total(): Decimal                                         <!-- S -->
	Interaction:                                                   <!-- S -->
		subtotal: Decimal = sum(item.line_total() for item in items) <!-- S -->
		return discount.compute_reduction(subtotal) if discount else subtotal <!-- S -->
+ checkout(inventory: Inventory): None                             <!-- S -->
	Invariant: May not be called when already checked out.        <!-- S -->
	Interaction:                                                   <!-- S -->
		inventory.assert_available(items)                         <!-- S -->
		checked_out = True                                        <!-- S -->
- _find_item(product: str): CartItem | None                       <!-- S -->

---

### **CartItem**                                                  <!-- S -->

+ CartItem(product: str, quantity: int, unit_price: Decimal)      <!-- S -->
------
+ product: str                                                     <!-- S -->
+ quantity: int                                                    <!-- S -->
	Invariant: quantity >= 1.                                      <!-- S -->
+ unit_price: Decimal                                              <!-- S -->
	Invariant: unit_price >= 0.                                   <!-- S -->
----
+ line_total(): Decimal                                            <!-- S -->
	Interaction:                                                   <!-- S -->
		return quantity * unit_price                              <!-- S -->
+ update_quantity(quantity: int): None                             <!-- S -->

---

### **Discount**                                                  <!-- S -->

+ Discount(code: str, reduction: Decimal)                         <!-- S -->
------
+ code: str                                                        <!-- S -->
+ reduction: Decimal                                               <!-- S -->
	Invariant: reduction > 0.                                      <!-- S -->
----
+ is_valid(cart: ShoppingCart): bool                               <!-- S -->
+ compute_reduction(subtotal: Decimal): Decimal                    <!-- S -->
	Invariant: Total may not be reduced below zero.               <!-- S -->
	Interaction:                                                   <!-- S -->
		reduced: Decimal = subtotal - reduction                   <!-- S -->
		return max(reduced, Decimal("0"))                         <!-- S -->
