// Epic: Get Payment
// Orders: 0.0.7

/** Story: Enter Payment
 * Actor: Customer
 * background-examples: {"stub auth": {"payment authorization": "payment authorization", "example": "stub auth", "transactionId": "d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3", "totalAmount": "1", "salesChannel": "ON-BOARDING", "group": "payment authorization"}}
 * BACKGROUND: background
 * SCENARIO: Enter Payment
 * background: background
 * background-step: Given | the Customer has completed order review and is on Checkout
 * background-step: And | the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: `payUpFront` is off
 * AND: Mavenir CCS authorizes ++payment authorization++ ++stub auth++
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
 * WHEN: Mavenir authorizes the card and returns the hosted payment page
 * THEN: My Paradise stores ++payment authorization++ ++stub auth++
 * SCENARIO: Pay upfront
 * background: background
 * background-step: Given | the Customer has completed order review and is on Checkout
 * background-step: And | the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: `payUpFront` is on
 * AND: the cart has ++plan++ ++Essentials++
 * AND: Mavenir CCS authorizes ++payment authorization++ ++stub auth++
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
 * WHEN: Mavenir authorizes the card and returns the hosted payment page
 * THEN: My Paradise stores ++payment authorization++ ++stub auth++
 * SCENARIO: Payment authorization fails to load
 * background: background
 * background-step: Given | the Customer has completed order review and is on Checkout
 * background-step: And | the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: `payUpFront` is off
 * BUT: Mavenir CCS does not return a payment authorization
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir
 * WHEN: Mavenir does not return a payment authorization
 * THEN: the payment authorization cannot be loaded
 * SCENARIO: FAC authorization timeout
 * background: background
 * background-step: Given | the Customer has completed order review and is on Checkout
 * background-step: And | the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: `payUpFront` is off
 * BUT: Mavenir does not return a transaction id
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir
 * WHEN: Mavenir does not return a transaction id
 * THEN: the payment authorization cannot be loaded
 */

/** Story: Authorize Card
 * Actor: My Paradise
 * background-examples: {"completed auth": {"payment status": "payment status", "example": "completed auth", "transactionId": "d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3", "status": "completed", "reason": "APPROVED", "group": "payment status"}, "failed auth": {"payment status": "payment status", "example": "failed auth", "transactionId": "d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3", "status": "failed", "reason": "DECLINED", "group": "payment status"}}
 * BACKGROUND: background
 * SCENARIO: Payment completed
 * background: background
 * GIVEN: the Customer has ++payment authorization++ ++stub auth++
 * AND: Mavenir CCS has ++payment status++ ++completed auth++
 * WHEN: the Customer authorizes their card
 * THEN: My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
 * WHEN: Mavenir returns ++payment status++ ++completed auth++
 * THEN: the payment is authorized
 * AND: the payment step does not place the order
 * SCENARIO: Card not verified
 * background: background
 * GIVEN: the Customer has ++payment authorization++ ++stub auth++
 * AND: Mavenir CCS has ++payment status++ ++failed auth++
 * AND: payment attempts are under the maximum
 * WHEN: the Customer authorizes their card
 * THEN: My Paradise sends the tokenized card request to Mavenir
 * WHEN: Mavenir returns ++payment status++ ++failed auth++
 * THEN: the card is not verified
 * AND: My Paradise requests a fresh payment authorization from Mavenir
 * SCENARIO: Maximum payment attempts
 * background: background
 * GIVEN: the Customer has ++payment authorization++ ++stub auth++
 * AND: Mavenir CCS has ++payment status++ ++failed auth++
 * AND: payment attempts equal the maximum
 * WHEN: the Customer authorizes their card
 * THEN: My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
 * WHEN: Mavenir returns ++payment status++ ++failed auth++
 * THEN: My Paradise records the failed card addition with Zendesk
 * AND: the payment step does not place the order
 */

/** Story: Provide Apple Pay Certificate
 * Actor: My Paradise
 * background-examples: {"Bermuda Apple Pay cert": {"Apple Pay certificate": "Apple Pay certificate", "example": "Bermuda Apple Pay cert", "keyIdentifier": "CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b", "group": "Apple Pay certificate"}}
 * BACKGROUND: background
 * SCENARIO: Provide Apple Pay certificate
 * background: background
 * GIVEN: the Apple Pay merchant certificate is available
 * WHEN: My Paradise provides the Apple Pay certificate
 * THEN: My Paradise sends the certificate request to Apple
 * WHEN: Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
 * THEN: My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
 */

/** Story: Adjust Credit Manually
 * Actor: Care
 * SCENARIO: Adjust credit for pay-upfront or voucher
 * GIVEN: the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++
 * AND: the ++Mavenir customer++ has completed onboarding in My Paradise
 * BUT: the credit adjustment was not applied after checkout
 * WHEN: the Care agent manually adjusts the credit amount in Mavenir DEP
 * THEN: the ++Mavenir customer++ billing account is credited the adjustment amount
 */
