# Acceptance criteria (exploration) — example

Filled example for the **Manage Customer Orders** story map (`abd-story-mapping` reference). Use as the quality bar when authoring `acceptance-criteria.md` from `templates/acceptance-criteria.md`.

---

## Story: Browse Product Catalog

**Story type:** user

**Sources / context:** *Order Management Workshop* whiteboard, 2026-03-15

### Domain terms

- *Product Catalog* — browsable list of products available to order
- *Category* — grouping used to narrow what the customer sees
- *Product Detail* — name, description, price, and image for one product
- *Out Of Stock* — product not available to add to an order right now

### Behaviors

1. *When* the customer opens the **Product Catalog**
   *Then* the system displays available products grouped by **Category**
   *And* each row shows at least product name and price

2. *When* the customer selects a **Category**
   *Then* the **Product Catalog** lists only products in that **Category**

3. *When* the customer selects a product from the **Product Catalog**
   *Then* the system shows **Product Detail** for that product

4. *When* a product is **Out Of Stock**
   *Then* the **Product Catalog** and **Product Detail** show that the product cannot be added to an order
   *But* the customer can still browse other products

### Evidence

| # | Source | Location |
| --- | --- | --- |
| 1 | *Order Management Workshop* | Whiteboard "Place order" flow, sticky "browse by category" |
| 2 | *Order Management Workshop* | Same session, "filter catalog by category" |
| 3 | *Order Management Workshop* | "click through to product detail" |
| 4 | *Order Management Workshop* | "don't block browsing when one SKU is gone" |

---

## Story: Add Item To Cart

**Story type:** user

**Sources / context:** *Order Management Workshop* whiteboard, 2026-03-15

### Domain terms

- *Cart* — holding area for products the customer intends to order
- *Cart Line* — one product and quantity in the **Cart**
- *Product Detail* — surface where the customer chooses quantity
- *Quantity* — number of units of one product
- *Out Of Stock* — cannot add or increase quantity beyond available supply

### Behaviors

1. *When* the customer adds a product from **Product Detail**
   *Then* the system creates or updates a **Cart Line** with the chosen **Quantity**
   *And* the **Cart** shows the updated line total

2. *When* the customer changes **Quantity** on an existing **Cart Line**
   *Then* the **Cart** updates the line total immediately

3. *When* the customer adds the same product again
   *Then* the system increases **Quantity** on the existing **Cart Line**
   *But* does not create a duplicate **Cart Line** for the same product

4. *When* the product is **Out Of Stock** for the requested **Quantity**
   *Then* the system rejects the add or increase
   *And* the customer sees which **Quantity** is available
   *But* other **Cart Line** items are unchanged

### Evidence

| # | Source | Location |
| --- | --- | --- |
| 1 | *Order Management Workshop* | "add to cart from detail page" |
| 2 | *Order Management Workshop* | "edit qty in cart" |
| 3 | *Order Management Workshop* | "one line per SKU" |
| 4 | *Order Management Workshop* | "cap qty to stock" |

---

## Story: Submit Order

**Story type:** user

**Sources / context:** *Order Management Workshop* whiteboard, 2026-03-15

### Domain terms

- *Cart* — must contain at least one **Cart Line** before submit
- *Shipping Address* — delivery destination captured earlier in the flow
- *Delivery Option* — shipping speed or method the customer selected
- *Order* — confirmed request to fulfill and ship
- *Order Confirmation* — reference and summary shown after successful submit
- *Payment Authorization* — funds check with the payment provider before the **Order** is accepted

### Behaviors

1. *When* the customer submits with a non-empty **Cart**, a valid **Shipping Address**, and a selected **Delivery Option**
   *Then* the system requests **Payment Authorization**
   *And* on success creates an **Order** from the **Cart**

2. *When* **Payment Authorization** succeeds
   *Then* the customer sees **Order Confirmation** with order reference and line summary
   *And* the **Cart** is cleared

3. *When* **Payment Authorization** fails
   *Then* the customer sees that payment failed and can retry or change payment method
   *But* no **Order** is created and the **Cart** is unchanged

4. *When* the customer submits with an empty **Cart**
   *Then* the system blocks submit
   *And* prompts the customer to add products first

5. *When* the customer submits without a **Shipping Address** or **Delivery Option**
   *Then* the system blocks submit
   *And* directs the customer to complete the missing step

### Evidence

| # | Source | Location |
| --- | --- | --- |
| 1 | *Order Management Workshop* | "submit only when cart + address + delivery ready" |
| 2 | *Order Management Workshop* | "confirmation screen + empty cart" |
| 3 | *Order Management Workshop* | "failed pay ≠ order placed" |
| 4 | *Order Management Workshop* | "no empty submit" |
| 5 | *Order Management Workshop* | "gate on address and delivery" |
