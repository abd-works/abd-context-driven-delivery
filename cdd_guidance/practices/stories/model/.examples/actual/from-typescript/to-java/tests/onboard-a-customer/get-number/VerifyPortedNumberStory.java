// Epic: Verify Ported Number
// Orders: 0.0.1.2

/** Story: Check Port Verification
 * SCENARIO: Enter porting SMS code
 * EXAMPLES: enteredValidPortability, validPortingSmscode, customerWithCartAndPortability
 * GIVEN: the Customer submitted portability and Twilio sent an SMS to the port number
 * AND: Twilio is ready to confirm the SMS code as valid
 * THEN: My Paradise sends the verification check to Twilio with the port number and code
 * WHEN: Twilio creates a verification check (verificationChecks.create)
 * THEN: Twilio returns approved and the Customer is forwarded to Select Sim
 * SCENARIO: Verify with unusable porting SMS code
 * EXAMPLES: enteredValidPortability, mismatchPortingSmscode, customerWithCartAndPortability
 * GIVEN: the Customer submitted portability and has an incorrect verification code
 * THEN: My Paradise sends the verification check to Twilio
 * WHEN: Twilio creates a verification check and returns a non-approved status
 * THEN: the verification is rejected
 * SCENARIO: Resend porting SMS code
 * EXAMPLES: enteredValidPortability, customerWithCartAndPortability
 * GIVEN: the Customer submitted portability and Twilio sent an SMS to the port number
 * WHEN: the Customer requests a new verification code
 * THEN: My Paradise SMSes a porting verification code via Twilio
 * WHEN: Twilio sends the SMS verification
 * THEN: the resend is confirmed
 */
