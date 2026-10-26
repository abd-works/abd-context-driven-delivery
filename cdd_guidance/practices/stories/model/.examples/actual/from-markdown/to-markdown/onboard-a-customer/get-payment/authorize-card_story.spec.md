## Story: Authorize Card

### Examples

#### payment status

| payment status | example | transactionId | status | reason | group |
| --- | --- | --- | --- | --- | --- |
| payment status | completed auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | completed | APPROVED | payment status |
| payment status | failed auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | failed | DECLINED | payment status |

### Scenario: Payment completed

*Given* the Customer has ++payment authorization++ ++stub auth++
*And* Mavenir CCS has ++payment status++ ++completed auth++
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
*When* Mavenir returns ++payment status++ ++completed auth++
*Then* the payment is authorized
*And* the payment step does not place the order

### Scenario: Card not verified

*Given* the Customer has ++payment authorization++ ++stub auth++
*And* Mavenir CCS has ++payment status++ ++failed auth++
*And* payment attempts are under the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir
*When* Mavenir returns ++payment status++ ++failed auth++
*Then* the card is not verified
*And* My Paradise requests a fresh payment authorization from Mavenir

### Scenario: Maximum payment attempts

*Given* the Customer has ++payment authorization++ ++stub auth++
*And* Mavenir CCS has ++payment status++ ++failed auth++
*And* payment attempts equal the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
*When* Mavenir returns ++payment status++ ++failed auth++
*Then* My Paradise records the failed card addition with Zendesk
*And* the payment step does not place the order
