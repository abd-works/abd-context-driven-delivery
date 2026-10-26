// Epic: Sign In With Existing Account
// Orders: 0.0.10

/** Story: Sign In With Existing Account
 * SCENARIO: Sign in with already-registered account credentials
 * EXAMPLES: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
 * GIVEN: Cognito has an already-registered Cognito user
 * AND: the Customer is not signed in
 * AND: the Customer has already-registered account credentials
 * WHEN: the Customer authenticates already-registered account credentials
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito authenticates the account and issues an account token
 * THEN: My Paradise stores the signed-in Cognito user
 * AND: the Cognito user has the Mavenir customer id
 * SCENARIO: Email format is unmet
 * EXAMPLES: enteredInvalidEmailFormat
 * GIVEN: the Customer has invalid email format account credentials
 * WHEN: the Customer authenticates invalid email format
 * THEN: My Paradise does not send a sign-in request to Cognito
 * AND: the authentication is rejected
 * AND: Cognito does not issue an account token
 * SCENARIO: Authenticate with unconfirmed account
 * EXAMPLES: enteredValidAccountCredentials, storedUnconfirmedCognitoUser
 * GIVEN: Cognito has an unconfirmed Cognito user
 * AND: the Customer is not signed in
 * AND: the Customer has unconfirmed sign-in account credentials
 * WHEN: the Customer authenticates unconfirmed sign-in
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns CONFIRM_SIGN_UP
 * THEN: the authentication is rejected as unconfirmed
 * AND: Cognito does not issue an account token
 * SCENARIO: Password reset required
 * EXAMPLES: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
 * GIVEN: Cognito has an already-registered Cognito user
 * AND: Cognito requires a password reset for already-registered account credentials
 * AND: the Customer is not signed in
 * AND: the Customer has already-registered account credentials
 * WHEN: the Customer authenticates already-registered account credentials
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns PasswordResetRequiredException
 * THEN: the authentication requires a password reset
 * AND: Cognito does not issue an account token
 * SCENARIO: New password required
 * EXAMPLES: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
 * GIVEN: Cognito has an already-registered Cognito user
 * AND: Cognito requires a new password for already-registered account credentials
 * AND: the Customer is not signed in
 * AND: the Customer has already-registered account credentials
 * WHEN: the Customer authenticates already-registered account credentials
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED
 * THEN: the authentication requires a new password
 * AND: Cognito does not issue an account token
 */
