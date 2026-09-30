## Story: Create Unconfirmed Cognito User

### Scenario: Display Create Account

*When* the User proceeds to create an account from the Paradise Mobile website
*Then* the User can enter account credentials
*And* the email and password rules are unmet
*And* the customer cannot save the customer account

### Scenario: Enter Valid account credentials

*When* the User enters valid account credentials
*Then* account credentials are validated continuously
*And* the customer can save the customer account

### Examples

| example |
| --- |
| enteredValidAccountCredentials |

### Scenario: Email already registered

*Given* already-registered account credentials are already registered
*When* the User registers already-registered account credentials
*Then* Email shows the already-registered error

### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredUnconfirmedCognitoUser |

### Scenario: Create Unconfirmed User

*Given* the amplifyService.signUp spy is set up
*When* the User creates their account
*Then* the system creates an unconfirmed Cognito user and emails a validation code

### Examples

| example |
| --- |
| enteredValidAccountCredentials |
| expectedValidAccountCredentials |

### Scenario: Email already registered in Cognito

*Given* an unconfirmed Cognito user exists for already-registered account credentials
*When* Cognito is asked to register already-registered account credentials
*Then* Cognito returns UsernameExistsException
*And* Cognito does not create another Cognito user

### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredUnconfirmedCognitoUser |
