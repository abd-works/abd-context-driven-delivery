## Story: Enter Validation Code

### Examples

#### validation code

| example | validation code | code | group |
| --- | --- | --- | --- |
| valid validation code | validation code | 123456 | validation code |
| mismatch validation code | validation code | Hmm. That code didn't work. | validation code |
| expired validation code | validation code | Hmm. That code didn't work. | validation code |
| attempts exceeded validation code | validation code | Attempts limit exceeded. Please try again later. | validation code |
| example | validation code | helper | validation code |

### Scenario: Enter validation code

### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* the User proceeds to check their email
*Then* the User sees the code was sent to *Jeff.anderson@Abdworks.com*
*And* the User can enter a ++validation code++ in Enter Validation Code
*And* the User can Resend
*And* the User can Close
*And* the Activate account operation is disabled
*When* the User enters a ++validation code++ ++valid validation code++
*Then* the Activate account operation is enabled
*When* the User clicks Activate account
*Then* the system confirms the ++Cognito user++ routing through Amplify to Cognito
*And* the User is forwarded to onboarding

### Scenario Outline: Activate with unusable validation code

### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* the User clicks Activate account with ++validation code++ {scenario}
*Then* Enter Validation Code shows helper text {helper}

### Scenario: Resend validation code

### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* the User clicks Resend
*Then* the system emails a new ++validation code++ routing through Amplify to Cognito
*And* the User sees *We sent you a new code. Please check your email.*
*And* Resend waits 60 seconds before it can be used again
