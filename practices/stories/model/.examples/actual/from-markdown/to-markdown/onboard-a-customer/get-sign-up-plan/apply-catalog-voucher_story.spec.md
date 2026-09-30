## Story: Apply Catalog Voucher

### Scenario: Apply Catalog Voucher via deep link

### Background

*Given* the plan catalog contains purchasable plans

*Given* Vouchera has ++catalog voucher++ ++valid catalog voucher++
*When* the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent

### Scenario: Apply Catalog Voucher manually

### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan
*And* Vouchera has ++catalog voucher++ ++valid catalog voucher++
*When* the Customer applies ++catalog voucher++ ++valid catalog voucher++
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent

### Scenario: Short catalog voucher code is rejected

### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan
*When* the Customer applies a catalog voucher shorter than 4 characters
*Then* the catalog voucher is rejected
*And* Vouchera is not asked for the voucher

### Scenario: Remove Catalog Voucher

### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied
*When* the Customer removes ++catalog voucher++ ++valid catalog voucher++
*Then* the catalog has no catalog voucher

### Scenario Outline: Apply unusable catalog voucher

### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan
*And* Vouchera has ++catalog voucher++ ++{scenario}++
*When* the Customer applies ++{scenario}++
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns
*Then* the catalog voucher is rejected
