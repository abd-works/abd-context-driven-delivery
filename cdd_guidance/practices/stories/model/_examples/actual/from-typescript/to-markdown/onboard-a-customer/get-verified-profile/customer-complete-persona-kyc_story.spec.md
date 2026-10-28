## Story: Customer Complete Persona Kyc

### Scenario: Persona verification required

*Given* the Customer has a cart with a plan, number, and SIM and no idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* a Persona inquiry is required
*And* the Customer is on the Profile KYC step

### Examples

| example |
| --- |
| customerWithProfile |

### Scenario: Persona verification already complete

*Given* the Customer has identity with an idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* the Persona inquiry is already complete
*And* the Customer is forwarded to Checkout

### Examples

| example |
| --- |
| customerWithProfile |
| expectedValidIdentity |

### Scenario: Create a completed Persona inquiry

*Given* the Customer has no idNumber on identity
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*And* My Paradise retrieves the Persona document
*When* Persona returns the completed inquiry
*Then* the Customer has a verified Persona inquiry
*And* My Paradise maps the inquiry onto identity and address
*And* Customer verified stays false until the Customer confirms their identity
*When* Persona returns the valid Persona document
*Then* identity expiry date is the Persona document expiration date

### Examples

| example |
| --- |
| completedInquiryId |
| completedPersonaInquiryResult |
| validDocumentId |
| validPersonaDocument |
| customerWithProfile |
| expectedValidAddress |
| expectedValidIdentity |

### Scenario: Persona inquiry not completed

*Given* the Customer has no idNumber on identity
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*When* Persona returns the failed Persona inquiry
*Then* the Customer has an unverified Persona inquiry
*And* identity and address stay empty

### Examples

| example |
| --- |
| failedPersonaInquiryResult |
| customerWithProfile |

### Scenario: No government ID document on inquiry

*Given* the completed Persona inquiry has no government ID document
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*And* My Paradise does not retrieve a Persona document
*When* Persona returns the completed inquiry without a government ID
*Then* identity expiry date is empty

### Examples

| example |
| --- |
| completedInquiryWithoutDocument |
| customerWithProfile |

### Scenario: Persona errors on inquiry load

*Given* the Customer has no idNumber on identity
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*When* Persona returns an error
*Then* the Customer has an unverified Persona inquiry
*And* identity stays empty

### Examples

| example |
| --- |
| customerWithProfile |

### Scenario: Document not found

*Given* Persona has no Persona document for that document ID
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns that the document is not found
*Then* identity expiry date is empty

### Examples

| example |
| --- |
| completedPersonaInquiryResult |
| validDocumentId |
| customerWithProfile |

### Scenario: Document email mismatch

*Given* the Persona document email does not match the Customer email
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns unauthorized
*Then* identity expiry date is empty

### Examples

| example |
| --- |
| completedPersonaInquiryResult |
| validDocumentId |
| customerWithProfile |

### Scenario: Verify later

*Given* the Customer has no idNumber on identity
*When* the Customer proceeds without a Persona inquiry
*Then* My Paradise does not send an inquiry request to Persona
*And* no Persona inquiry is stored
*And* the Customer is still on the Profile KYC step

### Examples

| example |
| --- |
| customerWithProfile |

### Scenario: Enter valid identity and address

*Given* the Customer has a My Paradise customer in session
*When* the Customer enters valid identity and address
*Then* all profile requirements are met
*And* the Customer can confirm their identity

### Examples

| example |
| --- |
| customerWithProfile |
| enteredValidAddress |
| enteredValidIdentity |
| expectedValidAddress |
| expectedValidIdentity |

### Scenario: Enter identity after a verified Persona inquiry

*Given* the Customer has a verified Persona inquiry mapped onto valid identity
*When* the Customer enters the mapped identity and address
*Then* all profile requirements are met
*And* the ID fields are present on identity

### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| enteredValidAddress |
| enteredValidIdentity |
| expectedValidIdentity |
| validProfileSeed |

### Scenario: Re-enter a verified identity

*Given* the Customer has valid identity already verified
*When* the Customer re-enters valid identity
*Then* the identity is no longer verified
*And* the Customer can confirm their identity again

### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| enteredValidAddress |
| enteredValidIdentity |
| expectedValidIdentity |
| validProfileSeed |

### Scenario: Enter incomplete identity or address: ${example}

*Given* the Customer has a My Paradise customer in session
*When* the Customer enters identity and address with ${field} empty
*Then* ${field} is missing
*And* the Customer cannot confirm their identity

### Examples

| example |
| --- |
| customerWithProfile |

### Scenario: Confirm identity with a verified Persona inquiry

*Given* the Customer has entered valid identity and address and has a verified Persona inquiry
*When* the Customer confirms their identity
*Then* My Paradise maps identity and address onto the Mavenir engaged party and contact medium
*And* My Paradise sends the profile patch to Mavenir
*When* Mavenir patches the customer
*Then* the Customer identity is persisted
*And* the Customer is verified

### Examples

| example |
| --- |
| reloadCart |
| completedInquiryId |
| customerWithProfile |
| expectedValidAddress |
| expectedValidIdentity |
| validProfileSeed |

### Scenario: Customer already exists

*Given* another Mavenir customer already has identity idNumber I1234562
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed because a customer with that information already exists

### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| expectedValidIdentity |
| validProfileSeed |

### Scenario: Profile requirements unmet

*Given* the Customer has not entered identity or address
*When* the Customer confirms their identity
*Then* the identity cannot be confirmed
*And* My Paradise does not send a profile patch to Mavenir

### Examples

| example |
| --- |
| customerWithProfile |

### Scenario: Mavenir profile patch error

*Given* Mavenir returns a profile patch error
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed

### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| validProfileSeed |
