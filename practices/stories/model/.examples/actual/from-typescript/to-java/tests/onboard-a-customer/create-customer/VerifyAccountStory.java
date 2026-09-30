// Epic: Verify Account
// Orders: 0.0.0.3

/** Story: Enter Validation Code
 * BACKGROUND: each
 * GIVEN: the User has submitted valid account credentials
 * AND: Cognito has an unconfirmed Cognito user
 * AND: Cognito has sent a validation code to the User
 * AND: the User has account credentials with valid email and password
 * SCENARIO: Enter validation code
 * EXAMPLES: enteredValidAccountCredentials
 * WHEN: the User activates the account with the emailed validation code
 * THEN: My Paradise sends the correct confirmation request to Cognito
 * AND: the account is verified
 * AND: Cognito issues an account token for the browser session
 * BUT: no Mavenir customer exists for those account credentials
 * SCENARIO: Resend validation code
 * WHEN: more than 60 seconds has passed
 * AND: the User resends the validation code
 * THEN: Cognito sends a new validation code
 * AND: My Paradise shows the resend confirmation
 * WHEN: less than 60 seconds has passed
 * AND: the User resends the validation code
 * THEN: Resend waits 60 seconds before it can be used again
 * AND: Cognito does not send another validation code during the wait
 * WHEN: more than 60 seconds has passed
 * AND: the User resends the validation code
 * THEN: Cognito sends another validation code
 */
