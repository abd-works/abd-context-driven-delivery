// Epic: Get Sign Up Plan
// Orders: 0.0.5

/** Story: Open Plan Deep Link
 * SCENARIO: Open plan deep link: ${plan.name}
 * EXAMPLES: seedPurchasableCatalog
 * GIVEN: the plan catalog contains purchasable plans and the Customer arrived at sign-up from the Paradise Mobile website
 * WHEN: the Customer opens a plan deep link for ${plan.name}
 * THEN: ${plan.name} is selected
 * AND: the Customer continues to Enter Account Credentials
 * SCENARIO: Unknown plan deep link
 * EXAMPLES: seedPurchasableCatalog, unknownPlanDeepLinkId
 * GIVEN: the plan catalog contains purchasable plans
 * BUT: the deep-link plan id is not in the catalog
 * WHEN: the Customer opens a plan deep link
 * THEN: the plan is not found
 */

/** Story: Apply Catalog Voucher
 * SCENARIO: Apply Catalog Voucher via deep link
 * EXAMPLES: seedPurchasableCatalog, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode, expectedValidCatalogVoucherCode
 * GIVEN: the plan catalog contains purchasable plans
 * AND: Vouchera has valid catalog voucher
 * WHEN: the Customer applies valid catalog voucher from a promotional voucher link
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns the voucher view
 * THEN: the catalog voucher is applied
 * AND: the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent
 * SCENARIO: Apply Catalog Voucher manually
 * EXAMPLES: seedPurchasableCatalog, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode
 * GIVEN: the Customer is selecting a plan
 * AND: Vouchera has valid catalog voucher
 * WHEN: the Customer applies valid catalog voucher
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns the voucher view
 * THEN: the catalog voucher is applied
 * AND: the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent
 * SCENARIO: Short catalog voucher code is rejected
 * EXAMPLES: seedPurchasableCatalog, shortCatalogVoucherCode, VoucherCodeRule
 * GIVEN: the Customer is selecting a plan
 * WHEN: the Customer applies a catalog voucher shorter than ${VoucherCodeRule.MinLength} characters
 * THEN: the catalog voucher is rejected
 * AND: Vouchera is not asked for the voucher
 * SCENARIO: Remove Catalog Voucher
 * EXAMPLES: seedPurchasableCatalog, seedAppliedValidCatalogVoucher
 * GIVEN: the Customer is selecting a plan with valid catalog voucher applied
 * WHEN: the Customer removes valid catalog voucher
 * THEN: the catalog has no catalog voucher
 * SCENARIO: Apply unusable catalog voucher: ${example}
 * EXAMPLES: seedPurchasableCatalog, seedUnusableCatalogVoucher
 * GIVEN: the Customer is selecting a plan
 * AND: Vouchera has ${example}
 * WHEN: the Customer applies ${example}
 * THEN: My Paradise sends the voucher code to Vouchera
 * THEN: the catalog voucher is rejected
 */
