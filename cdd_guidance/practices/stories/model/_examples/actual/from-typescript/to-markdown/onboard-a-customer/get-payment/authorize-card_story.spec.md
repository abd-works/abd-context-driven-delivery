## Story: Authorize Card

### Scenario: Payment completed

*Given* the Customer has stub auth
*And* Mavenir CCS has completed auth
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for stub auth
*When* Mavenir returns completed auth
*Then* the payment is authorized
*And* the payment step does not place the order

### Examples

| example |
| --- |
| reloadCart |
| customerReadyForPayment |
| paymentWithAuthorization |
| stubAuth |
| completedAuth |

### Scenario: Card not verified

*Given* the Customer has stub auth
*And* Mavenir CCS has failed auth
*And* payment attempts are under the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir
*When* Mavenir returns failed auth
*Then* the card is not verified
*And* My Paradise requests a fresh payment authorization from Mavenir

### Examples

| example |
| --- |
| customerReadyForPayment |
| maxPaymentAttempts |
| paymentWithAuthorization |
| stubAuth |
| failedAuth |

### Scenario: Maximum payment attempts

*Given* the Customer has stub auth
*And* Mavenir CCS has failed auth
*And* payment attempts equal the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for stub auth
*When* Mavenir returns failed auth
*Then* My Paradise records the failed card addition with Zendesk
*And* the payment step does not place the order

### Examples

| example |
| --- |
| reloadCart |
| customerReadyForPayment |
| maxPaymentAttempts |
| paymentWithAuthorization |
| stubAuth |
| failedAuth |
