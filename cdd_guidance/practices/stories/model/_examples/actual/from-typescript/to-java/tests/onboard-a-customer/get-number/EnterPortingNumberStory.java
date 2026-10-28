// Epic: Enter Porting Number
// Orders: 0.0.1.0

/** Story: Submit Portability Request
 * SCENARIO: Port the number
 * EXAMPLES: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * AND: ${storedHeldAvailableNumber} is available as a temporary port-in MSISDN
 * WHEN: the Customer enters valid portability and ports their number
 * THEN: My Paradise submits the portability request to Mavenir with the customer's portability details
 * AND: Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number
 * WHEN: Mavenir assigns ${storedHeldAvailableNumber} as a temporary port-in MSISDN and patches the shopping cart, and Twilio sends the SMS verification
 * THEN: the Customer is forwarded to Verify Ported Number
 * SCENARIO: Port the number — SMS verification skipped
 * EXAMPLES: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * AND: Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send
 * WHEN: the Customer enters valid portability and ports their number
 * WHEN: Mavenir processes the portability request and Twilio rate-limits the SMS send
 * THEN: portability is stored on the line with verification skipped
 * AND: the Customer is forwarded to Select Sim — no verification step required
 * SCENARIO: Port the number: ${example}
 * EXAMPLES: customerWithCart, stubBundle
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * WHEN: the Customer submits portability and ports their number
 * THEN: submit returns error: ${expectedMessage}
 */
