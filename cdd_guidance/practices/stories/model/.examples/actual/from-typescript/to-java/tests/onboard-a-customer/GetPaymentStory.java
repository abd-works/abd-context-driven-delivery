// Epic: Get Payment
// Orders: 0.0.4

/** Story: Enter Payment
 * SCENARIO: Enter Payment
 * GIVEN: the Customer is at Checkout with Essentials
 * AND: Mavenir CCS authorizes stub auth
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
 * WHEN: Mavenir authorizes the card and returns the hosted payment page
 * THEN: the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING
 * SCENARIO: Payment authorization fails to load
 * GIVEN: the Customer is at Checkout with Essentials
 * BUT: Mavenir CCS does not return a payment authorization
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir
 * WHEN: Mavenir does not return a payment authorization
 * THEN: the payment authorization cannot be loaded
 * SCENARIO: FAC authorization timeout
 * GIVEN: the Customer is at Checkout with Essentials
 * BUT: Mavenir does not return a transaction id
 * WHEN: the Customer proceeds to adding their payment
 * THEN: My Paradise sends the card authorization request to Mavenir
 * WHEN: Mavenir does not return a transaction id
 * THEN: the payment authorization cannot be loaded
 */

/** Story: Authorize Card
 * SCENARIO: Payment completed
 * GIVEN: the Customer has stub auth
 * AND: Mavenir CCS has completed auth
 * WHEN: the Customer authorizes their card
 * THEN: My Paradise sends the tokenized card request to Mavenir for stub auth
 * WHEN: Mavenir returns completed auth
 * THEN: the payment is authorized
 * AND: the payment step does not place the order
 * SCENARIO: Card not verified
 * GIVEN: the Customer has stub auth
 * AND: Mavenir CCS has failed auth
 * AND: payment attempts are under the maximum
 * WHEN: the Customer authorizes their card
 * THEN: My Paradise sends the tokenized card request to Mavenir
 * WHEN: Mavenir returns failed auth
 * THEN: the card is not verified
 * AND: My Paradise requests a fresh payment authorization from Mavenir
 * SCENARIO: Maximum payment attempts
 * GIVEN: the Customer has stub auth
 * AND: Mavenir CCS has failed auth
 * AND: payment attempts equal the maximum
 * WHEN: the Customer authorizes their card
 * THEN: My Paradise sends the tokenized card request to Mavenir for stub auth
 * WHEN: Mavenir returns failed auth
 * THEN: My Paradise records the failed card addition with Zendesk
 * AND: the payment step does not place the order
 */

/** Story: Provide Apple Pay Certificate
 * SCENARIO: Provide Apple Pay certificate
 * GIVEN: the Apple Pay merchant certificate is available
 * WHEN: My Paradise provides the Apple Pay certificate
 * THEN: My Paradise sends the certificate request to Apple
 * WHEN: Apple returns Bermuda Apple Pay cert
 * THEN: My Paradise returns Bermuda Apple Pay cert
 */
