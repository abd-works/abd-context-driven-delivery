## Story: Enter Validation Code

### Story Background: each

*Given* the User has submitted valid account credentials
*And* Cognito has an unconfirmed Cognito user
*And* Cognito has sent a validation code to the User
*And* the User has account credentials with valid email and password

### Scenario: Enter validation code

*When* the User activates the account with the emailed validation code
*Then* My Paradise sends the correct confirmation request to Cognito
*And* the account is verified
*And* Cognito issues an account token for the browser session
*But* no Mavenir customer exists for those account credentials

### Examples

| example |
| --- |
| enteredValidAccountCredentials |

### Scenario: Resend validation code

*When* more than 60 seconds has passed
*And* the User resends the validation code
*Then* Cognito sends a new validation code
*And* My Paradise shows the resend confirmation
*When* less than 60 seconds has passed
*And* the User resends the validation code
*Then* Resend waits 60 seconds before it can be used again
*And* Cognito does not send another validation code during the wait
*When* more than 60 seconds has passed
*And* the User resends the validation code
*Then* Cognito sends another validation code
