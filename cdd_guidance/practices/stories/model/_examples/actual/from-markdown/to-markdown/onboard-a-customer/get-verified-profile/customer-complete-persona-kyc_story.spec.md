## Story: Customer Complete Persona Kyc

### Scenario: Persona verification required

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*But* no idNumber on ++identity++
*When* the Customer validates whether a Persona inquiry is required
*Then* a Persona inquiry is required
*And* the Customer is on the Profile KYC step

### Scenario: Persona verification already complete

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has ++identity++ with an idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* the Persona inquiry is already complete
*And* the Customer is forwarded to Checkout

### Scenario: Create a completed Persona inquiry

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has no idNumber on ++identity++
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*And* My Paradise retrieves the Persona document
*When* Persona returns ++Persona inquiry++ ++completed Persona inquiry++
*Then* the Customer has a verified ++Persona inquiry++
*And* My Paradise maps the inquiry onto ++identity++ ++valid identity++ and ++address++ ++valid address++
*And* Customer verified stays false until the Customer confirms their identity
*When* Persona returns ++Persona document++ ++valid Persona document++
*Then* ++identity++ expiry date is the ++Persona document++ expiration date

### Scenario: Persona inquiry not completed

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*When* Persona returns ++Persona inquiry++ ++failed Persona inquiry++
*Then* the Customer has an unverified ++Persona inquiry++
*And* ++identity++ and ++address++ stay empty

### Scenario: No government ID document on inquiry

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the completed ++Persona inquiry++ has no government ID document
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*And* My Paradise does not retrieve a Persona document
*When* Persona returns the completed inquiry without a government ID
*Then* ++identity++ expiry date is empty

### Scenario: Persona errors on inquiry load

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*When* Persona returns an error
*Then* the Customer has an unverified ++Persona inquiry++
*And* ++identity++ stays empty

### Scenario: Document not found

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* Persona has no ++Persona document++ for that document ID
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns that the document is not found
*Then* ++identity++ expiry date is empty

### Scenario: Document email mismatch

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the ++Persona document++ email does not match the Customer email
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns unauthorized
*Then* ++identity++ expiry date is empty

### Scenario: Verify later

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has a ++My Paradise customer++ with no idNumber on ++identity++
*When* the Customer proceeds without a Persona inquiry
*Then* My Paradise does not send an inquiry request to Persona
*And* no ++Persona inquiry++ is stored
*And* the Customer is still on the Profile KYC step

### Scenario: Enter valid identity and address

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has a ++My Paradise customer++ in session
*When* the Customer enters ++identity++ ++valid identity++ and ++address++ ++valid address++
*Then* all profile requirements are met
*And* the Customer can confirm their identity

### Scenario: Enter identity after a verified Persona inquiry

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has a verified ++Persona inquiry++ mapped onto ++identity++ ++valid identity++
*When* the Customer enters the mapped ++identity++ and ++address++
*Then* all profile requirements are met
*And* the ID fields are present on ++identity++

### Scenario: Re-enter a verified identity

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has ++identity++ ++valid identity++ already verified
*When* the Customer re-enters ++identity++ ++valid identity++
*Then* the identity is no longer verified
*And* the Customer can confirm their identity again

### Scenario Outline: Enter incomplete identity or address

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*When* the Customer enters ++identity++ and ++address++ with {field} empty
*Then* {field} is missing
*And* the Customer cannot confirm their identity

### Scenario: Confirm identity with a verified Persona inquiry

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has entered ++identity++ ++valid identity++ and ++address++ ++valid address++
*And* the Customer has a verified ++Persona inquiry++
*When* the Customer confirms their identity
*Then* My Paradise maps ++identity++ and ++address++ onto the Mavenir engaged party and contact medium
*And* My Paradise sends the profile patch to Mavenir
*When* Mavenir patches the customer
*Then* the Customer identity is persisted
*And* the Customer is verified
*And* the ++Persona inquiry++ is cleared

### Scenario: Profile requirements unmet

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has not entered ++identity++ or ++address++
*When* the Customer confirms their identity
*Then* the identity cannot be confirmed
*And* My Paradise does not send a profile patch to Mavenir

### Scenario: Customer already exists

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* another Mavenir customer already has ++identity++ idNumber I1234562
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed because a customer with that information already exists

### Scenario: Mavenir profile patch error

### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* Mavenir returns a profile patch error
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed
