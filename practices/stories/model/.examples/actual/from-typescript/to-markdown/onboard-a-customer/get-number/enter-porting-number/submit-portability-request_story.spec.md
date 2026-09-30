## Story: Submit Portability Request

### Scenario: Port the number

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer enters valid portability and ports their number
*And* Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number
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
