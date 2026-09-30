// Epic: Get Sign Up Plan
// Orders: 0.0.5

/** Story: Open Plan Deep Link
 * SCENARIO: Unknown plan deep link
 * GIVEN: the plan catalog contains purchasable plans
 * BUT: the deep-link plan id is not in the catalog
 * WHEN: the Customer opens a plan deep link
 * THEN: the plan is not found
 */

/** Story: Apply Catalog Voucher
 * SCENARIO: Apply Catalog Voucher via deep link
 * GIVEN: the plan catalog contains purchasable plans
 * AND: Vouchera has valid catalog voucher
 * WHEN: the Customer applies valid catalog voucher from a promotional voucher link
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns the voucher view
 * THEN: the catalog voucher is applied
 * AND: the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent
 * SCENARIO: Apply Catalog Voucher manually
 * GIVEN: the Customer is selecting a plan
 * AND: Vouchera has valid catalog voucher
 * WHEN: the Customer applies valid catalog voucher
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns the voucher view
 * THEN: the catalog voucher is applied
 * AND: the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent
 * SCENARIO: Short catalog voucher code is rejected
 * GIVEN: the Customer is selecting a plan
 * THEN: the catalog voucher is rejected
 * AND: Vouchera is not asked for the voucher
 * SCENARIO: Remove Catalog Voucher
 * GIVEN: the Customer is selecting a plan with valid catalog voucher applied
 * WHEN: the Customer removes valid catalog voucher
 * THEN: the catalog has no catalog voucher
 */
