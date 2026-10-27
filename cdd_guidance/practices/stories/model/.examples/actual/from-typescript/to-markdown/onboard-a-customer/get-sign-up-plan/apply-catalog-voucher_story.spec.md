## Story: Apply Catalog Voucher

### Scenario: Apply Catalog Voucher via deep link

*Given* the plan catalog contains purchasable plans
*And* Vouchera has valid catalog voucher
*When* the Customer applies valid catalog voucher from a promotional voucher link
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent

### Scenario: Apply Catalog Voucher manually

*Given* the Customer is selecting a plan
*And* Vouchera has valid catalog voucher
*When* the Customer applies valid catalog voucher
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent

### Scenario: Short catalog voucher code is rejected

*Given* the Customer is selecting a plan
*Then* the catalog voucher is rejected
*And* Vouchera is not asked for the voucher

### Scenario: Remove Catalog Voucher

*Given* the Customer is selecting a plan with valid catalog voucher applied
*When* the Customer removes valid catalog voucher
*Then* the catalog has no catalog voucher
