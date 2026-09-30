// Epic: Create Unconfirmed User
// Orders: 0.0.0.1

/** Story: Create Unconfirmed Cognito User
 * SCENARIO: Display Create Account
 * WHEN: the User proceeds to create an account from the Paradise Mobile website
 * THEN: the User can enter account credentials
 * AND: the email and password rules are unmet
 * AND: the customer cannot save the customer account
 * SCENARIO: Enter Valid account credentials
 * EXAMPLES: enteredValidAccountCredentials
 * WHEN: the User enters valid account credentials
 * THEN: account credentials are validated continuously
 * AND: the customer can save the customer account
 * SCENARIO: Email already registered
 * EXAMPLES: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
 * GIVEN: already-registered account credentials are already registered
 * WHEN: the User registers already-registered account credentials
 * THEN: Email shows the already-registered error
 * SCENARIO: Create Unconfirmed User
 * EXAMPLES: enteredValidAccountCredentials, expectedValidAccountCredentials
 * GIVEN: the amplifyService.signUp spy is set up
 * WHEN: the User creates their account
 * THEN: the system creates an unconfirmed Cognito user and emails a validation code
 * SCENARIO: Email already registered in Cognito
 * EXAMPLES: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
 * GIVEN: an unconfirmed Cognito user exists for already-registered account credentials
 * WHEN: Cognito is asked to register already-registered account credentials
 * THEN: Cognito returns UsernameExistsException
 * AND: Cognito does not create another Cognito user
 */
