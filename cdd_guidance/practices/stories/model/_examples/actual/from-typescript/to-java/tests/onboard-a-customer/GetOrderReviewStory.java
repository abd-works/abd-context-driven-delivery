// Epic: Get Order Review
// Orders: 0.0.3

/** Story: Check The Order
 * SCENARIO: Check the order: ${example}
 * EXAMPLES: seedCustomerCart, loadCart, stubBundle
 * GIVEN: the Customer has completed account setup, number, SIM, and profile
 * WHEN: My Paradise loads the order state from the Mavenir shopping cart
 * THEN: the Customer is forwarded to Checkout
 * AND: the order summary shows the plan
 * AND: the order summary shows the number and SIM
 * AND: the order summary shows the profile
 */

/** Story: Upgrade To Data Freedom
 * SCENARIO: Upgrade plan from review: ${example}
 * EXAMPLES: customerWithCart, reloadCart
 * GIVEN: ${currentPlan.name} is in the Mavenir shopping cart
 * WHEN: My Paradise patches the Mavenir shopping cart with ${newPlan.name}
 * THEN: My Paradise sends the patch cart request to Mavenir with ${newPlan.name} bundleId
 * WHEN: Mavenir returns the updated Mavenir shopping cart with ${newPlan.name}
 * THEN: My Paradise stores ${newPlan.name} as the cart bundle
 */

/** Story: Change Plan From Review
 * SCENARIO: Select a different plan from review
 * EXAMPLES: customerWithCart, reloadCart, enteredChosenAvailableNumber, essentials, dataFreedom
 * GIVEN: the Customer has opened plan selection from review with Essentials in the cart
 * WHEN: My Paradise patches the Mavenir shopping cart with Data Freedom
 * THEN: My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId
 * WHEN: Mavenir returns the updated Mavenir shopping cart with Data Freedom
 * THEN: My Paradise stores Data Freedom as the cart bundle loaded from the gateway
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Keep current plan from review
 * EXAMPLES: customerWithCart, enteredChosenAvailableNumber, essentials
 * GIVEN: the Customer has opened plan selection from review with Essentials in the cart
 * WHEN: the Customer keeps their current plan
 * THEN: the cart bundle remains Essentials
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Plan update fails from review
 * EXAMPLES: customerWithCart, reloadCart, essentials, dataFreedom
 * GIVEN: the Customer has opened plan selection from review with Essentials in the cart
 * WHEN: My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error
 * THEN: My Paradise shows Failed to update new plan choice.
 * WHEN: My Paradise reloads the shopping cart
 * THEN: the cart bundle remains Essentials
 */
