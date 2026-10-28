// Epic: Create Customer
// Orders: 0.0.0

/** Story: Create Customer
 * BACKGROUND: each
 * GIVEN: the User has a verified account with an account token
 * SCENARIO: Create customer
 * EXAMPLES: enteredValidAccountCredentials
 * WHEN: the User creates their Paradise account
 * THEN: My Paradise sends the correct create request to Mavenir
 * WHEN: Mavenir creates the customer
 * THEN: the customer has a Mavenir customer id
 * AND: My Paradise stores the customer id on the Cognito user
 * SCENARIO: Mavenir customer already exists
 * EXAMPLES: enteredValidAccountCredentials
 * GIVEN: Mavenir already has a customer for that email
 * WHEN: the User creates their Paradise account
 * THEN: My Paradise shows Could not create customer
 */
