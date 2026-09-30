// Epic: Get Voucher Credit
// Orders: 0.0.8

/** Story: Redeem Voucher and Apply Credit
 * SCENARIO: Redeem an any-plan voucher
 * EXAMPLES: anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials
 * GIVEN: the Customer is in Order Creation with any-plan voucher applied
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00
 * WHEN: Vouchera records the voucher redemption
 * THEN: My Paradise stores the zero redemption
 * AND: My Paradise skips the apply credit request to Mavenir
 * SCENARIO: Skip redeem when the cart bundle is not in the voucher plan list
 * EXAMPLES: ace, amountOffVoucher, cartWithBilling
 * GIVEN: the Customer is in Order Creation with amount-off voucher applied and Ace in the cart
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise skips the redeem request to Vouchera
 * AND: My Paradise skips the apply credit request to Mavenir
 * SCENARIO: Failed voucher redemption
 * EXAMPLES: amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines, cartWithBilling, essentials
 * GIVEN: the Customer is in Order Creation with amount-off voucher applied
 * WHEN: the Customer redeems the voucher
 * THEN: My Paradise sends the redeem request to Vouchera
 * WHEN: Vouchera returns an error
 * THEN: the voucher redemption is unsuccessful
 * WHEN: the Customer applies the voucher credit
 * THEN: My Paradise skips the apply credit request to Mavenir
 */
