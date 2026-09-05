## Story: `Update Cart Quantity`

### Scenario Outline 1: `Quantity change recalculates line price and subtotal`

Given the **Shopping Cart** contains a **Cart Item** with **product in cart** *{sku}*, **quantity** *{initial_qty}*, **unit price at time of adding** *{unit_price}*
And the **Shopping Cart** has **cart subtotal** *{initial_subtotal}*
When the customer changes **quantity** on **Cart Item** *{sku}* to *{new_qty}*
Then **Cart Item** *{sku}* has **quantity** *{new_qty}* and **line price** *{expected_line_price}*
And the **Shopping Cart** has **cart subtotal** *{expected_subtotal}*
And the visible item count indicator shows *{expected_badge_count}*

#### Examples:


| scenario | sku         | unit_price | initial_qty | initial_subtotal | new_qty | expected_line_price | expected_subtotal | expected_badge_count |
| -------- | ----------- | ---------- | ----------- | ---------------- | ------- | ------------------- | ----------------- | -------------------- |
| 1        | PET-HAR-001 | Â£34.99     | 2           | Â£69.98           | 3       | Â£104.97             | Â£104.97           | 3                    |
| 2        | PET-HAR-001 | Â£34.99     | 2           | Â£69.98           | 1       | Â£34.99              | Â£34.99            | 1                    |


### Scenario 2: `Quantity set to zero removes item from cart`

Given the **Shopping Cart** contains a **Cart Item** with **product in cart** *PET-TRT-042*, **quantity** *1*, **unit price at time of adding** *Â£4.99*
And the **Shopping Cart** has **cart subtotal** *Â£4.99*
When the customer sets **quantity** on **Cart Item** *PET-TRT-042* to *0*
Then **Cart Item** *PET-TRT-042* is removed from the **Shopping Cart**
And the **Shopping Cart** has **cart subtotal** *Â£0.00*
And the visible item count indicator shows *0*
