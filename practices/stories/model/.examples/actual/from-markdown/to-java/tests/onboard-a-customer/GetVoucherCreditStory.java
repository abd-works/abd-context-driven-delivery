// Epic: Get Voucher Credit
// Orders: 0.0.9

/** Story: Redeem Voucher and Apply Credit
 * Actor: My Paradise
 * SCENARIO: Redeem a plan-restricted voucher that matches the cart bundle
 * GIVEN: the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied
 * AND: the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
 * AND: Vouchera has ++voucher++ ++{voucher}++
 * AND: the Customer has a billing account
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount `70.00`)
 * WHEN: Vouchera records the ++voucher redemption++
 * THEN: My Paradise stores ++voucher redemption++ ++{redemption}++
 * WHEN: the Customer applies the voucher credit
 * THEN: My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (`transactionType` creditAdjustment, glCode `100004`, unit BMD, channel `@type`)
 * WHEN: Mavenir records the ++credit adjustment++ on the billing account
 * THEN: My Paradise stores the credit on the Customer billing account
 * AND: continues to Create Product Order
 * SCENARIO: Redeem an any-plan voucher
 * GIVEN: the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied
 * AND: the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
 * AND: Vouchera has ++voucher++ ++any-plan voucher++
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount `0.00`)
 * WHEN: Vouchera records the ++voucher redemption++
 * THEN: My Paradise stores ++voucher redemption++ ++zero redemption++
 * AND: My Paradise skips the apply credit request to Mavenir
 * AND: continues to Create Product Order
 * SCENARIO: Skip redeem when the cart bundle is not in the voucher plan list
 * GIVEN: the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
 * BUT: the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id `100000000042`) which is not in ++voucher++ ++amount-off voucher++ planIds
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise skips the redeem request to Vouchera
 * AND: My Paradise skips the apply credit request to Mavenir
 * AND: continues to Create Product Order
 * SCENARIO: Failed voucher redemption
 * GIVEN: the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
 * AND: the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++
 * AND: Vouchera returns an error for the redeem request
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise sends the redeem request to Vouchera
 * WHEN: Vouchera returns an error
 * THEN: the voucher redemption is unsuccessful
 * WHEN: the Customer applies the voucher credit
 * THEN: My Paradise skips the apply credit request to Mavenir
 * AND: continues to Create Product Order
 */
