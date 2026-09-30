// Epic: Get Order Review
// Orders: 0.0.3

/** Story: Change Plan From Review
 * SCENARIO: Select a different plan from review
 * GIVEN: the Customer has opened plan selection from review with Essentials in the cart
 * WHEN: My Paradise patches the Mavenir shopping cart with Data Freedom
 * THEN: My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId
 * WHEN: Mavenir returns the updated Mavenir shopping cart with Data Freedom
 * THEN: My Paradise stores Data Freedom as the cart bundle loaded from the gateway
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Keep current plan from review
 * GIVEN: the Customer has opened plan selection from review with Essentials in the cart
 * WHEN: the Customer keeps their current plan
 * THEN: the cart bundle remains Essentials
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Plan update fails from review
 * GIVEN: the Customer has opened plan selection from review with Essentials in the cart
 * WHEN: My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error
 * THEN: My Paradise shows Failed to update new plan choice.
 * WHEN: My Paradise reloads the shopping cart
 * THEN: the cart bundle remains Essentials
 */
