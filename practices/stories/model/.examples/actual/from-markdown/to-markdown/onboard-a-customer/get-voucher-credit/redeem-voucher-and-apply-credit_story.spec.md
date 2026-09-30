## Story: Redeem Voucher and Apply Credit

### Scenario Outline: Redeem a plan-restricted voucher that matches the cart bundle

*Given* the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied
*And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
*And* Vouchera has ++voucher++ ++{voucher}++
*And* the Customer has a billing account
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount `70.00`)
*When* Vouchera records the ++voucher redemption++
*Then* My Paradise stores ++voucher redemption++ ++{redemption}++
*When* the Customer applies the voucher credit
*Then* My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (`transactionType` creditAdjustment, glCode `100004`, unit BMD, channel `@type`)
*When* Mavenir records the ++credit adjustment++ on the billing account
*Then* My Paradise stores the credit on the Customer billing account
*And* continues to Create Product Order

### Scenario: Redeem an any-plan voucher

*Given* the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied
*And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
*And* Vouchera has ++voucher++ ++any-plan voucher++
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount `0.00`)
*When* Vouchera records the ++voucher redemption++
*Then* My Paradise stores ++voucher redemption++ ++zero redemption++
*And* My Paradise skips the apply credit request to Mavenir
*And* continues to Create Product Order

### Scenario: Skip redeem when the cart bundle is not in the voucher plan list

*Given* the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
*But* the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id `100000000042`) which is not in ++voucher++ ++amount-off voucher++ planIds
*When* the Customer redeems the voucher
*Then* My Paradise skips the redeem request to Vouchera
*And* My Paradise skips the apply credit request to Mavenir
*And* continues to Create Product Order

### Scenario: Failed voucher redemption

*Given* the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
*And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++
*And* Vouchera returns an error for the redeem request
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera
*When* Vouchera returns an error
*Then* the voucher redemption is unsuccessful
*When* the Customer applies the voucher credit
*Then* My Paradise skips the apply credit request to Mavenir
*And* continues to Create Product Order
