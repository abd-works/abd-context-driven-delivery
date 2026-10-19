## Story: Check Port Verification

### Scenario: Enter porting SMS code

*Given* the Customer submitted portability and Twilio sent an SMS to the port number
*And* Twilio is ready to confirm the SMS code as valid
*Then* My Paradise sends the verification check to Twilio with the port number and code
*When* Twilio creates a verification check (verificationChecks.create)
*Then* Twilio returns approved and the Customer is forwarded to Select Sim

### Examples

| example |
| --- |
| enteredValidPortability |
| validPortingSmscode |
| customerWithCartAndPortability |

### Scenario: Verify with unusable porting SMS code

*Given* the Customer submitted portability and has an incorrect verification code
*Then* My Paradise sends the verification check to Twilio
*When* Twilio creates a verification check and returns a non-approved status
*Then* the verification is rejected

### Examples

| example |
| --- |
| enteredValidPortability |
| mismatchPortingSmscode |
| customerWithCartAndPortability |

### Scenario: Resend porting SMS code

*Given* the Customer submitted portability and Twilio sent an SMS to the port number
*When* the Customer requests a new verification code
*Then* My Paradise SMSes a porting verification code via Twilio
*When* Twilio sends the SMS verification
*Then* the resend is confirmed

### Examples

| example |
| --- |
| enteredValidPortability |
| customerWithCartAndPortability |
