// Epic: Get Verified Profile
// Orders: 0.0.7

/** Story: Customer Complete Persona Kyc
 * SCENARIO: Persona verification required
 * GIVEN: the Customer has a cart with a plan, number, and SIM and no idNumber
 * WHEN: the Customer validates whether a Persona inquiry is required
 * THEN: a Persona inquiry is required
 * AND: the Customer is on the Profile KYC step
 * SCENARIO: Persona verification already complete
 * GIVEN: the Customer has identity with an idNumber
 * WHEN: the Customer validates whether a Persona inquiry is required
 * THEN: the Persona inquiry is already complete
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Create a completed Persona inquiry
 * GIVEN: the Customer has no idNumber on identity
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona with the Customer email
 * AND: My Paradise retrieves the Persona document
 * WHEN: Persona returns the completed inquiry
 * THEN: the Customer has a verified Persona inquiry
 * AND: My Paradise maps the inquiry onto identity and address
 * AND: Customer verified stays false until the Customer confirms their identity
 * WHEN: Persona returns the valid Persona document
 * THEN: identity expiry date is the Persona document expiration date
 * SCENARIO: Persona inquiry not completed
 * GIVEN: the Customer has no idNumber on identity
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona with the Customer email
 * WHEN: Persona returns the failed Persona inquiry
 * THEN: the Customer has an unverified Persona inquiry
 * AND: identity and address stay empty
 * SCENARIO: No government ID document on inquiry
 * GIVEN: the completed Persona inquiry has no government ID document
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona
 * AND: My Paradise does not retrieve a Persona document
 * WHEN: Persona returns the completed inquiry without a government ID
 * THEN: identity expiry date is empty
 * SCENARIO: Persona errors on inquiry load
 * GIVEN: the Customer has no idNumber on identity
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona
 * WHEN: Persona returns an error
 * THEN: the Customer has an unverified Persona inquiry
 * AND: identity stays empty
 * SCENARIO: Document not found
 * GIVEN: Persona has no Persona document for that document ID
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise retrieves the Persona document
 * WHEN: Persona returns that the document is not found
 * THEN: identity expiry date is empty
 * SCENARIO: Document email mismatch
 * GIVEN: the Persona document email does not match the Customer email
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise retrieves the Persona document
 * WHEN: Persona returns unauthorized
 * THEN: identity expiry date is empty
 * SCENARIO: Verify later
 * GIVEN: the Customer has no idNumber on identity
 * WHEN: the Customer proceeds without a Persona inquiry
 * THEN: My Paradise does not send an inquiry request to Persona
 * AND: no Persona inquiry is stored
 * AND: the Customer is still on the Profile KYC step
 * SCENARIO: Enter valid identity and address
 * GIVEN: the Customer has a My Paradise customer in session
 * WHEN: the Customer enters valid identity and address
 * THEN: all profile requirements are met
 * AND: the Customer can confirm their identity
 * SCENARIO: Enter identity after a verified Persona inquiry
 * GIVEN: the Customer has a verified Persona inquiry mapped onto valid identity
 * WHEN: the Customer enters the mapped identity and address
 * THEN: all profile requirements are met
 * AND: the ID fields are present on identity
 * SCENARIO: Re-enter a verified identity
 * GIVEN: the Customer has valid identity already verified
 * WHEN: the Customer re-enters valid identity
 * THEN: the identity is no longer verified
 * AND: the Customer can confirm their identity again
 * SCENARIO: Confirm identity with a verified Persona inquiry
 * GIVEN: the Customer has entered valid identity and address and has a verified Persona inquiry
 * WHEN: the Customer confirms their identity
 * THEN: My Paradise maps identity and address onto the Mavenir engaged party and contact medium
 * AND: My Paradise sends the profile patch to Mavenir
 * WHEN: Mavenir patches the customer
 * THEN: the Customer identity is persisted
 * AND: the Customer is verified
 * SCENARIO: Customer already exists
 * GIVEN: another Mavenir customer already has identity idNumber I1234562
 * WHEN: the Customer confirms their identity
 * THEN: My Paradise sends the profile patch to Mavenir
 * AND: the identity cannot be confirmed because a customer with that information already exists
 * SCENARIO: Profile requirements unmet
 * GIVEN: the Customer has not entered identity or address
 * WHEN: the Customer confirms their identity
 * THEN: the identity cannot be confirmed
 * AND: My Paradise does not send a profile patch to Mavenir
 * SCENARIO: Mavenir profile patch error
 * GIVEN: Mavenir returns a profile patch error
 * WHEN: the Customer confirms their identity
 * THEN: My Paradise sends the profile patch to Mavenir
 * AND: the identity cannot be confirmed
 */
