## Story: Sign In With Existing Account

### Scenario: Sign in with already-registered account credentials

*Given* Cognito has an already-registered Cognito user
*And* the Customer is not signed in
*And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito authenticates the account and issues an account token
*Then* My Paradise stores the signed-in Cognito user
*And* the Cognito user has the Mavenir customer id

### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |

### Scenario: Email format is unmet

*Given* the Customer has invalid email format account credentials
*When* the Customer authenticates invalid email format
*Then* My Paradise does not send a sign-in request to Cognito
*And* the authentication is rejected
*And* Cognito does not issue an account token

### Examples

| example |
| --- |
| enteredInvalidEmailFormat |

### Scenario: Authenticate with unconfirmed account

*Given* Cognito has an unconfirmed Cognito user
*And* the Customer is not signed in
*And* the Customer has unconfirmed sign-in account credentials
*When* the Customer authenticates unconfirmed sign-in
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns CONFIRM_SIGN_UP
*Then* the authentication is rejected as unconfirmed
*And* Cognito does not issue an account token

### Examples

| example |
| --- |
| enteredValidAccountCredentials |
| storedUnconfirmedCognitoUser |

### Scenario: Password reset required

*Given* Cognito has an already-registered Cognito user
*And* Cognito requires a password reset for already-registered account credentials
*And* the Customer is not signed in
*And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns PasswordResetRequiredException
*Then* the authentication requires a password reset
*And* Cognito does not issue an account token

### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |

### Scenario: New password required

*Given* Cognito has an already-registered Cognito user
*And* Cognito requires a new password for already-registered account credentials
*And* the Customer is not signed in
*And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED
*Then* the authentication requires a new password
*And* Cognito does not issue an account token

### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |
