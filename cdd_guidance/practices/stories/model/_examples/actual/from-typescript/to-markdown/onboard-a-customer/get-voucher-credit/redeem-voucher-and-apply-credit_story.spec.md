## Story: Redeem Voucher and Apply Credit

### Scenario: Redeem a plan-restricted voucher that matches the cart bundle: ${example}

*Given* the Customer is in Order Creation with ${example} applied
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ${example} orderAmount ${orderAmount}
*When* Vouchera records the voucher redemption
*Then* My Paradise stores the ${example} redemption
*When* the Customer applies the voucher credit
*Then* My Paradise sends the ${creditExample} to Mavenir
*When* Mavenir records the credit adjustment on the billing account
*Then* My Paradise stores the credit on the Customer billing account

### Examples

| example |
| --- |
| reloadCart |
| billingAccountId |
| cartWithBilling |
| essentials |

### Scenario: Redeem an any-plan voucher

*Given* the Customer is in Order Creation with any-plan voucher applied
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00
*When* Vouchera records the voucher redemption
*Then* My Paradise stores the zero redemption
*And* My Paradise skips the apply credit request to Mavenir

### Examples

| example |
| --- |
| anyPlanVoucher |
| anyPlanVoucherCode |
| anyPlanVoucheraSeed |
| zeroRedemption |
| cartWithBilling |
| essentials |

### Scenario: Skip redeem when the cart bundle is not in the voucher plan list

*Given* the Customer is in Order Creation with amount-off voucher applied and Ace in the cart
*When* the Customer redeems the voucher
*Then* My Paradise skips the redeem request to Vouchera
*And* My Paradise skips the apply credit request to Mavenir

### Examples

| example |
| --- |
| ace |
| amountOffVoucher |
| cartWithBilling |

### Scenario: Failed voucher redemption

*Given* the Customer is in Order Creation with amount-off voucher applied
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera
*When* Vouchera returns an error
*Then* the voucher redemption is unsuccessful
*When* the Customer applies the voucher credit
*Then* My Paradise skips the apply credit request to Mavenir

### Examples

| example |
| --- |
| amountOffVoucher |
| amountOffVoucherCode |
| amountOffVoucheraSeed |
| redeemMatchOutlines |
| cartWithBilling |
| essentials |
