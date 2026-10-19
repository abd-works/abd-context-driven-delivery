// Epic: Create Empty Cart
// Orders: 0.0.0.0

/** Story: Ensure Cart on Customer
 * SCENARIO: Load Cart — no cart
 * EXAMPLES: storedAccountCredentialsWithToken
 * GIVEN: the Customer enters the onboarding journey with a valid account token and no cart
 * WHEN: My Paradise loads the cart for the customer
 * THEN: My Paradise finds no cart on the customer
 * SCENARIO: Create Cart
 * EXAMPLES: storedAccountCredentialsWithToken
 * GIVEN: the Customer enters the onboarding journey with a valid account token and no cart
 * WHEN: My Paradise creates a cart for the customer
 * THEN: My Paradise sends the create request to Midtier with the customer id
 * WHEN: Mavenir creates the shopping cart
 * THEN: My Paradise stores the cart on the customer
 * AND: the Customer proceeds to Get Number
 * SCENARIO: customer already has a Mavenir shopping cart
 * EXAMPLES: storedAccountCredentialsWithToken, newMavenirShoppingCart
 * GIVEN: the Customer enters the onboarding journey with a valid account token
 * AND: the customer has a Mavenir shopping cart
 * WHEN: My Paradise loads the cart for the customer
 * THEN: My Paradise finds the cart on the customer
 * AND: the Customer proceeds to Get Number
 * SCENARIO: cart already exists
 * EXAMPLES: storedAccountCredentialsWithToken, newMavenirShoppingCart
 * GIVEN: the Customer enters the onboarding journey and already has a cart loaded
 * WHEN: My Paradise creates a cart for the customer
 * THEN: My Paradise reports a cart creation error
 */
