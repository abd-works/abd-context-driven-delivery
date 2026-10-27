// Epic: Load Customer
// Orders: 0.0.0.2

/** Story: Load My Paradise Customer From Midtier And Store In Session
 * BACKGROUND: each
 * GIVEN: Mavenir has a customer and the Cognito user holds its id
 * SCENARIO: Load My Paradise Customer From Midtier And Store In Session
 * EXAMPLES: enteredValidAccountCredentials
 * WHEN: My Paradise loads the customer through Midtier
 * THEN: My Paradise calls Midtier with the correct customer id
 * AND: Midtier maps the Mavenir contact medium to Paradise identity and address
 * SCENARIO: Load customer fails
 * GIVEN: Mavenir no longer has that customer
 * WHEN: My Paradise loads the customer
 * THEN: My Paradise signs the User out
 * AND: My Paradise shows Something went wrong when loading your account
 * SCENARIO: Terminated account
 * EXAMPLES: storedAccountCredentialsWithToken
 * GIVEN: the Customer has an account token
 * AND: the Mavenir customer billing state is terminated
 * WHEN: My Paradise loads the customer
 * THEN: My Paradise signs the Customer out
 * AND: the Customer account is terminated
 */
