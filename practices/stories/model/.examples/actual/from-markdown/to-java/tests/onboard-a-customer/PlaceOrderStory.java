// Epic: Place Order
// Orders: 0.0.8

/** Story: Create Billing Account
 * Actor: My Paradise
 * SCENARIO: Create billing account
 * background: background
 * background-step: Given | the Customer has a configured cart
 * background-step: But | the Customer has no billing account
 * WHEN: the Customer creates a billing account
 * THEN: My Paradise sends the billing account request to Mavenir
 * WHEN: Mavenir creates the billing account
 * THEN: the Customer has a billing account
 * AND: the Customer is on the Done step
 * SCENARIO: Billing account already exists
 * background: background
 * background-step: Given | the Customer has a configured cart
 * background-step: But | the Customer has no billing account
 * GIVEN: the Customer already has a billing account
 * WHEN: the Customer creates a billing account
 * THEN: the billing account is rejected
 * AND: Mavenir does not receive a billing account request
 * SCENARIO: Billing account creation fails
 * background: background
 * background-step: Given | the Customer has a configured cart
 * background-step: But | the Customer has no billing account
 * GIVEN: Mavenir returns an error for the billing account request
 * WHEN: the Customer creates a billing account
 * THEN: the billing account cannot be created
 * AND: the Customer has no billing account
 */

/** Story: Create Product Order
 * Actor: My Paradise
 * SCENARIO: Create product order
 * background: background
 * background-step: Given | the Customer has a billing account
 * background-step: And | the cart has plan, number, and SIM
 * GIVEN: the Customer is verified
 * WHEN: the Customer places the product order
 * THEN: My Paradise sends the product order request to Mavenir
 * WHEN: Mavenir creates the product order
 * THEN: the order succeeded with pay-up-front
 * AND: the Customer onboarding is done
 * SCENARIO: Pay-up-front charge fails
 * background: background
 * background-step: Given | the Customer has a billing account
 * background-step: And | the cart has plan, number, and SIM
 * GIVEN: the pay-up-front charge fails
 * WHEN: the Customer places the product order
 * THEN: My Paradise does not send a product order to Mavenir
 * AND: the order succeeded without pay-up-front
 * SCENARIO: Product order fails
 * background: background
 * background-step: Given | the Customer has a billing account
 * background-step: And | the cart has plan, number, and SIM
 * GIVEN: Mavenir returns an error for the product order
 * WHEN: the Customer places the product order
 * THEN: the order did not succeed
 * SCENARIO: Onboarding is already done
 * background: background
 * background-step: Given | the Customer has a billing account
 * background-step: And | the cart has plan, number, and SIM
 * GIVEN: the Customer onboarding is already done
 * WHEN: the Customer places the product order
 * THEN: the product order is rejected
 * AND: Mavenir does not receive a product order request
 * SCENARIO: Unverified with no bypass and no portability
 * background: background
 * background-step: Given | the Customer has a billing account
 * background-step: And | the cart has plan, number, and SIM
 * GIVEN: the Customer is not verified
 * AND: the plan does not bypass verification
 * AND: the cart has no portability
 * WHEN: the Customer places the product order
 * THEN: My Paradise does not send a product order to Mavenir
 * AND: the cart is marked to submit the order later
 * AND: the Customer onboarding is done
 */

/** Story: View Order Result
 * Actor: Customer
 * SCENARIO: View order result
 * GIVEN: the order result is {example}
 * WHEN: the Customer views their order result
 * THEN: the order is {outcome}
 */

/** Story: Create Order Ticket
 * Actor: My Paradise
 * SCENARIO: Create order ticket
 * GIVEN: the Customer {example}
 * WHEN: the Customer creates the order ticket
 * THEN: My Paradise sends the {subject} ticket to Zendesk
 * WHEN: Zendesk creates the ticket
 * THEN: the ticket is created for the Customer
 */

/** Story: View Order History
 * Actor: Care
 * SCENARIO: View Order History
 * background: background
 * background-step: Given | the Customer has a product order in Mavenir
 * background-step: And | Care is in Customer Management → Order History
 * WHEN: Care views Order History for the Customer
 * THEN: Care sees the product order with status badges
 */
