// Epic: Get Verified Profile
// Orders: 0.0.5

/** Story: Customer Complete Persona Kyc
 * Actor: Customer
 * SCENARIO: Persona verification required
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * BUT: no idNumber on ++identity++
 * WHEN: the Customer validates whether a Persona inquiry is required
 * THEN: a Persona inquiry is required
 * AND: the Customer is on the Profile KYC step
 * SCENARIO: Persona verification already complete
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has ++identity++ with an idNumber
 * WHEN: the Customer validates whether a Persona inquiry is required
 * THEN: the Persona inquiry is already complete
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Create a completed Persona inquiry
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has no idNumber on ++identity++
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona with the Customer email
 * AND: My Paradise retrieves the Persona document
 * WHEN: Persona returns ++Persona inquiry++ ++completed Persona inquiry++
 * THEN: the Customer has a verified ++Persona inquiry++
 * AND: My Paradise maps the inquiry onto ++identity++ ++valid identity++ and ++address++ ++valid address++
 * AND: Customer verified stays false until the Customer confirms their identity
 * WHEN: Persona returns ++Persona document++ ++valid Persona document++
 * THEN: ++identity++ expiry date is the ++Persona document++ expiration date
 * SCENARIO: Persona inquiry not completed
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona with the Customer email
 * WHEN: Persona returns ++Persona inquiry++ ++failed Persona inquiry++
 * THEN: the Customer has an unverified ++Persona inquiry++
 * AND: ++identity++ and ++address++ stay empty
 * SCENARIO: No government ID document on inquiry
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the completed ++Persona inquiry++ has no government ID document
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona
 * AND: My Paradise does not retrieve a Persona document
 * WHEN: Persona returns the completed inquiry without a government ID
 * THEN: ++identity++ expiry date is empty
 * SCENARIO: Persona errors on inquiry load
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise sends the inquiry request to Persona
 * WHEN: Persona returns an error
 * THEN: the Customer has an unverified ++Persona inquiry++
 * AND: ++identity++ stays empty
 * SCENARIO: Document not found
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: Persona has no ++Persona document++ for that document ID
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise retrieves the Persona document
 * WHEN: Persona returns that the document is not found
 * THEN: ++identity++ expiry date is empty
 * SCENARIO: Document email mismatch
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the ++Persona document++ email does not match the Customer email
 * WHEN: the Customer creates a Persona inquiry
 * THEN: My Paradise retrieves the Persona document
 * WHEN: Persona returns unauthorized
 * THEN: ++identity++ expiry date is empty
 * SCENARIO: Verify later
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has a ++My Paradise customer++ with no idNumber on ++identity++
 * WHEN: the Customer proceeds without a Persona inquiry
 * THEN: My Paradise does not send an inquiry request to Persona
 * AND: no ++Persona inquiry++ is stored
 * AND: the Customer is still on the Profile KYC step
 * SCENARIO: Enter valid identity and address
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has a ++My Paradise customer++ in session
 * WHEN: the Customer enters ++identity++ ++valid identity++ and ++address++ ++valid address++
 * THEN: all profile requirements are met
 * AND: the Customer can confirm their identity
 * SCENARIO: Enter identity after a verified Persona inquiry
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has a verified ++Persona inquiry++ mapped onto ++identity++ ++valid identity++
 * WHEN: the Customer enters the mapped ++identity++ and ++address++
 * THEN: all profile requirements are met
 * AND: the ID fields are present on ++identity++
 * SCENARIO: Re-enter a verified identity
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has ++identity++ ++valid identity++ already verified
 * WHEN: the Customer re-enters ++identity++ ++valid identity++
 * THEN: the identity is no longer verified
 * AND: the Customer can confirm their identity again
 * SCENARIO: Enter incomplete identity or address
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * WHEN: the Customer enters ++identity++ and ++address++ with {field} empty
 * THEN: {field} is missing
 * AND: the Customer cannot confirm their identity
 * SCENARIO: Confirm identity with a verified Persona inquiry
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has entered ++identity++ ++valid identity++ and ++address++ ++valid address++
 * AND: the Customer has a verified ++Persona inquiry++
 * WHEN: the Customer confirms their identity
 * THEN: My Paradise maps ++identity++ and ++address++ onto the Mavenir engaged party and contact medium
 * AND: My Paradise sends the profile patch to Mavenir
 * WHEN: Mavenir patches the customer
 * THEN: the Customer identity is persisted
 * AND: the Customer is verified
 * AND: the ++Persona inquiry++ is cleared
 * SCENARIO: Profile requirements unmet
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: the Customer has not entered ++identity++ or ++address++
 * WHEN: the Customer confirms their identity
 * THEN: the identity cannot be confirmed
 * AND: My Paradise does not send a profile patch to Mavenir
 * SCENARIO: Customer already exists
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: another Mavenir customer already has ++identity++ idNumber I1234562
 * WHEN: the Customer confirms their identity
 * THEN: My Paradise sends the profile patch to Mavenir
 * AND: the identity cannot be confirmed because a customer with that information already exists
 * SCENARIO: Mavenir profile patch error
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM
 * GIVEN: Mavenir returns a profile patch error
 * WHEN: the Customer confirms their identity
 * THEN: My Paradise sends the profile patch to Mavenir
 * AND: the identity cannot be confirmed
 */

/** Story: Collect Identity With Brand Amassador
 * Actor: Ambassador
 * SCENARIO: Collect identity with Brand Ambassador
 * GIVEN: the Customer is choosing how to verify their ID
 * WHEN: the Customer asks a Brand Ambassador to verify their ID
 * THEN: the Ambassador will be in touch to proceed with verification
 * AND: the Ambassador collects the Customer's ++identity++ documents over WhatsApp
 * AND: the Customer proceeds to enter identity in My Paradise
 */
