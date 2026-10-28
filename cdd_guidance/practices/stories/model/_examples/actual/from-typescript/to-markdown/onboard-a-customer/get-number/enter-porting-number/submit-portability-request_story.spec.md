## Story: Submit Portability Request

### Scenario: Port the number

*Given* a My Paradise customer with a Mavenir shopping cart
*And* ${storedHeldAvailableNumber} is available as a temporary port-in MSISDN
*When* the Customer enters valid portability and ports their number
*Then* My Paradise submits the portability request to Mavenir with the customer's portability details
*And* Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number
*When* Mavenir assigns ${storedHeldAvailableNumber} as a temporary port-in MSISDN and patches the shopping cart, and Twilio sends the SMS verification
*Then* the Customer is forwarded to Verify Ported Number

### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredValidPortability |
| customerWithCart |
| stubBundle |
| reloadCart |

### Scenario: Port the number — SMS verification skipped

*Given* a My Paradise customer with a Mavenir shopping cart
*And* Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send
*When* the Customer enters valid portability and ports their number
*When* Mavenir processes the portability request and Twilio rate-limits the SMS send
*Then* portability is stored on the line with verification skipped
*And* the Customer is forwarded to Select Sim — no verification step required

### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredValidPortability |
| customerWithCart |
| stubBundle |

### Scenario: Port the number: ${example}

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer submits portability and ports their number
*Then* submit returns error: ${expectedMessage}

### Examples

| example |
| --- |
| customerWithCart |
| stubBundle |
