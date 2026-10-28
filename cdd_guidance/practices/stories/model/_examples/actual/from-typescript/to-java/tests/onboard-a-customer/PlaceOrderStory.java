// Epic: Place Order
// Orders: 0.0.9

/** Story: Create Billing Account
 * SCENARIO: Create billing account
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder, expectedBillingAccountRequest
 * GIVEN: the Customer has a configured cart and no billing account
 * WHEN: the Customer creates a billing account
 * THEN: My Paradise sends the billing account request to Mavenir
 * WHEN: Mavenir creates the billing account
 * THEN: the Customer has a billing account
 * AND: the Customer is on the Done step
 * SCENARIO: Billing account already exists
 * EXAMPLES: customerReadyToPlaceOrder
 * GIVEN: the Customer already has a billing account
 * WHEN: the Customer creates a billing account
 * THEN: the billing account is rejected
 * AND: Mavenir does not receive a billing account request
 * SCENARIO: Billing account creation fails
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder
 * GIVEN: Mavenir returns an error for the billing account request
 * WHEN: the Customer creates a billing account
 * THEN: the billing account cannot be created
 * WHEN: My Paradise reloads the customer
 * THEN: the Customer has no billing account
 */

/** Story: Create Product Order
 * SCENARIO: Create product order
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder, expectedProductOrderRequest
 * GIVEN: the Customer is verified and has a billing account, plan, number, and eSIM
 * WHEN: the Customer places the product order
 * THEN: My Paradise sends the product order request to Mavenir
 * WHEN: Mavenir creates the product order
 * THEN: the order succeeded with pay-up-front
 * AND: the Customer onboarding is done
 * SCENARIO: Pay-up-front charge fails
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder
 * GIVEN: the pay-up-front charge fails
 * WHEN: the Customer places the product order
 * THEN: My Paradise does not send a product order to Mavenir
 * WHEN: My Paradise reloads the cart
 * THEN: the order succeeded without pay-up-front
 * SCENARIO: Product order fails
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder
 * GIVEN: Mavenir returns an error for the product order
 * WHEN: the Customer places the product order
 * THEN: My Paradise sends the product order request to Mavenir
 * WHEN: My Paradise reloads the cart
 * THEN: the order did not succeed
 * SCENARIO: Onboarding is already done
 * EXAMPLES: customerReadyToPlaceOrder
 * GIVEN: the Customer onboarding is already done
 * WHEN: the Customer places the product order
 * THEN: the product order is rejected
 * AND: Mavenir does not receive a product order request
 * SCENARIO: Unverified with no bypass and no portability
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder
 * GIVEN: the Customer is not verified and the plan does not bypass verification
 * WHEN: the Customer places the product order
 * THEN: My Paradise does not send a product order to Mavenir
 * AND: the cart is marked to submit the order later
 * WHEN: My Paradise reloads the cart
 * THEN: the Customer onboarding is done
 */

/** Story: View Order Result
 * SCENARIO: View order result: ${example}
 * EXAMPLES: reloadCart, customerReadyToPlaceOrder
 * GIVEN: the order result is ${example}
 * WHEN: the Customer views their order result
 */

/** Story: Create Order Ticket
 * SCENARIO: Create order ticket: ${example}
 * EXAMPLES: customerReadyToPlaceOrder, expectedTicketRequest, requesterName
 * GIVEN: the Customer ${example}
 * WHEN: the Customer creates the order ticket
 * THEN: My Paradise sends the ${subject} ticket to Zendesk
 * WHEN: Zendesk creates the ticket
 * THEN: the ticket is created for the Customer
 */
