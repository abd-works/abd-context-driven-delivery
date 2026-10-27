## Story: Sign In With Existing Account

### Scenario: Sign in with already-registered account credentials

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* the Customer is not signed in
*And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito authenticates the account and issues an ++account token++
*Then* My Paradise stores ++Cognito user++ ++signed-in Cognito user++
*And* the Cognito user has the Mavenir customer id

### Scenario: Email format is unmet

*Given* the Customer has ++account credentials++ ++invalid email format++
*When* the Customer authenticates ++account credentials++ ++invalid email format++
*Then* My Paradise does not send a sign-in request to Cognito
*And* the authentication is rejected
*And* Cognito does not issue an ++account token++

### Scenario Outline: Authenticate with incorrect account credentials

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* the Customer has ++account credentials++ {example}
*When* the Customer authenticates ++account credentials++ {example}
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++NotAuthorizedException++
*Then* the authentication is rejected
*And* Cognito does not issue an ++account token++

### Scenario: Authenticate with unconfirmed account

*Given* Cognito has ++Cognito user++ ++unconfirmed Cognito user++
*When* the Customer authenticates ++account credentials++ ++unconfirmed sign-in++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++CONFIRM_SIGN_UP++
*Then* the authentication is rejected as unconfirmed
*And* Cognito does not issue an ++account token++

### Scenario: Password reset required

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* Cognito requires a password reset for ++already-registered account credentials++
*And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++PasswordResetRequiredException++
*Then* the authentication requires a password reset
*And* Cognito does not issue an ++account token++

### Scenario: New password required

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* Cognito requires a new password for ++already-registered account credentials++
*And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++
*Then* the authentication requires a new password
*And* Cognito does not issue an ++account token++
