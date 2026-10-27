// Epic: Get Sign Up Plan
// Orders: 0.0.0

/** Story: Open Plan Deep Link
 * Actor: Customer
 * SCENARIO: Open Plan Deep Link
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * background-step: And | the Customer arrived at sign-up from the Paradise Mobile website
 * WHEN: the Customer opens a plan deep link for ++plan++ ++{scenario}++
 * THEN: ++{scenario}++ is selected
 * AND: the Customer continues to Enter Account Credentials
 * SCENARIO: Unknown plan deep link
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * background-step: And | the Customer arrived at sign-up from the Paradise Mobile website
 * GIVEN: the plan catalog contains purchasable plans
 * BUT: the deep-link plan id is not in the catalog
 * WHEN: the Customer opens a plan deep link
 * THEN: the plan is not found
 */

/** Story: Apply Catalog Voucher
 * Actor: Customer
 * SCENARIO: Apply Catalog Voucher via deep link
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * GIVEN: Vouchera has ++catalog voucher++ ++valid catalog voucher++
 * WHEN: the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns the voucher view
 * THEN: the catalog voucher is applied
 * AND: the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent
 * SCENARIO: Apply Catalog Voucher manually
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * GIVEN: the Customer is selecting a plan
 * AND: Vouchera has ++catalog voucher++ ++valid catalog voucher++
 * WHEN: the Customer applies ++catalog voucher++ ++valid catalog voucher++
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns the voucher view
 * THEN: the catalog voucher is applied
 * AND: the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent
 * SCENARIO: Short catalog voucher code is rejected
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * GIVEN: the Customer is selecting a plan
 * WHEN: the Customer applies a catalog voucher shorter than 4 characters
 * THEN: the catalog voucher is rejected
 * AND: Vouchera is not asked for the voucher
 * SCENARIO: Remove Catalog Voucher
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * GIVEN: the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied
 * WHEN: the Customer removes ++catalog voucher++ ++valid catalog voucher++
 * THEN: the catalog has no catalog voucher
 * SCENARIO: Apply unusable catalog voucher
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * GIVEN: the Customer is selecting a plan
 * AND: Vouchera has ++catalog voucher++ ++{scenario}++
 * WHEN: the Customer applies ++{scenario}++
 * THEN: My Paradise sends the voucher code to Vouchera
 * WHEN: Vouchera returns
 * THEN: the catalog voucher is rejected
 */
