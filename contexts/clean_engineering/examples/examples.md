<!-- @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only. -->
<!-- invoke-edit: action satisfy | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->

<!--
  clean_engineering markdown examples — ShoppingCart domain — unified across all fidelities.
  Fidelity tags:
    L = language      (prose only)
    M = model         (typed compact block)
    S = specification (relationship kinds, invariant sentences, interactions)
-->

# ShoppingCart                                                    <!-- L -->

---

## Language fidelity                                              <!-- L -->

*ShoppingCart* is a running tally of what a customer intends to buy in a single shopping session. <!-- L -->

### shopping_cart                                                  <!-- L -->

- Belongs to exactly one *Customer* whose identity anchors the cart. <!-- L -->
- Collects *CartItems* as the customer browses and keeps the running total current. <!-- L -->
- Accepts an optional *Discount* applied before the total is computed. <!-- L -->
- **Invariant:** Once checked out, the cart may not be modified.  <!-- L -->

### discount                                                       <!-- L -->

- **Invariant:** A discount may not reduce the total below zero.  <!-- L -->

---

## Model fidelity                                                 <!-- M -->

### **ShoppingCart**                                              <!-- M -->

ShoppingCart(customer: Customer)                                   <!-- M -->
------
customer: Customer                                                 <!-- M -->
items: list[CartItem]                                              <!-- M -->
discount: Discount | None                                         <!-- M -->
checked_out: bool                                                  <!-- M -->
	Invariant: Once true, never reverts to false.                  <!-- M -->
----
add_item(product: str, quantity: int, unit_price: Decimal): None  <!-- M -->
	Invariant: Cart may not be modified after checkout.           <!-- M -->
	Invariant: Quantity must be at least 1.                       <!-- M -->
remove_item(product: str): None                                    <!-- M -->
	Invariant: Cart may not be modified after checkout.           <!-- M -->
apply_discount(discount: Discount): None                           <!-- M -->
	Invariant: Cart may not be modified after checkout.           <!-- M -->
compute_total(): Decimal                                           <!-- M -->
checkout(inventory: Inventory): None                               <!-- M -->
	Invariant: May not be called when already checked out.        <!-- M -->
- _find_item(product: str): CartItem | None                       <!-- M -->

### **CartItem**                                                  <!-- M -->

CartItem(product: str, quantity: int, unit_price: Decimal)        <!-- M -->
------
product: str                                                       <!-- M -->
quantity: int                                                      <!-- M -->
	Invariant: quantity >= 1.                                      <!-- M -->
unit_price: Decimal                                                <!-- M -->
	Invariant: unit_price >= 0.                                   <!-- M -->
----
line_total(): Decimal                                              <!-- M -->
update_quantity(quantity: int): None                               <!-- M -->

### **Discount**                                                  <!-- M -->

Discount(code: str, reduction: Decimal)                            <!-- M -->
------
code: str                                                          <!-- M -->
reduction: Decimal                                                 <!-- M -->
	Invariant: reduction > 0.                                      <!-- M -->
----
is_valid(cart: ShoppingCart): bool                                 <!-- M -->
compute_reduction(subtotal: Decimal): Decimal                      <!-- M -->
	Invariant: Total may not be reduced below zero.               <!-- M -->

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
