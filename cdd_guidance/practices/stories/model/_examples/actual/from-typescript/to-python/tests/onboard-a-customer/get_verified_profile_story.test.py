from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import customerWithProfile, expectedValidIdentity, completedInquiryId, completedPersonaInquiryResult, validDocumentId, validPersonaDocument, expectedValidAddress, failedPersonaInquiryResult, completedInquiryWithoutDocument, enteredValidAddress, enteredValidIdentity, validProfileSeed, reloadCart


# Epic: Get Verified Profile
# Orders: 0.0.7

# Story: Customer Complete Persona Kyc
with story("Customer Complete Persona Kyc"):
    # typescript body to translate:
    # let createInquirySpy: MockInstance<typeof personaGateway.create>;
    # let readDocumentSpy: MockInstance<typeof personaGateway.readDocument>;
    # let patchProfileSpy: MockInstance<typeof portalGateway.patchProfile>;
    #
    # beforeEach(() => {
    #   createInquirySpy = vi.spyOn(personaGateway, 'create');
    #   readDocumentSpy = vi.spyOn(personaGateway, 'readDocument');
    #   patchProfileSpy = vi.spyOn(portalGateway, 'patchProfile');
    # });
    #
    # incompleteProfileOutlines.forEach(({ example, field, requirement, identity, address }) => {
    # });
        with scenario("Persona verification required"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: PersonaInquiryValidation;
            # examples: customerWithProfile
            with given("the Customer has a cart with a plan, number, and SIM and no idNumber"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                pass
            with when("the Customer validates whether a Persona inquiry is required"):
                # typescript body to translate:
                # result = cart.customer.validatePersonaInquiry();
                pass
            with then("a Persona inquiry is required"):
                # typescript body to translate:
                # expect(result).toBe(PersonaInquiryValidation.Required);
                pass
            with and_("the Customer is on the Profile KYC step"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
                pass
        with scenario("Persona verification already complete"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: PersonaInquiryValidation;
            # examples: customerWithProfile, expectedValidIdentity
            with given("the Customer has identity with an idNumber"):
                # typescript body to translate:
                # cart = await customerWithProfile({ idNumber: expectedValidIdentity.idNumber });
                pass
            with when("the Customer validates whether a Persona inquiry is required"):
                # typescript body to translate:
                # result = cart.customer.validatePersonaInquiry();
                pass
            with then("the Persona inquiry is already complete"):
                # typescript body to translate:
                # expect(result).toBe(PersonaInquiryValidation.Complete);
                pass
            with and_("the Customer is forwarded to Checkout"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
                pass
        with scenario("Create a completed Persona inquiry"):
            # typescript body to translate:
            # let cart: Cart;
            # let inquiry: PersonaInquiry;
            # examples: completedInquiryId, completedPersonaInquiryResult, validDocumentId, validPersonaDocument, customerWithProfile, expectedValidAddress, expectedValidIdentity
            with given("the Customer has no idNumber on identity"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                # personaGateway.seedInquiry(completedPersonaInquiryResult);
                # personaGateway.seedDocument(validPersonaDocument);
                pass
            with when("the Customer creates a Persona inquiry"):
                # typescript body to translate:
                # inquiry = cart.customer.createPersonaInquiry();
                pass
            with then("My Paradise sends the inquiry request to Persona with the Customer email"):
                # typescript body to translate:
                # expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
                pass
            with and_("My Paradise retrieves the Persona document"):
                # typescript body to translate:
                # expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
                pass
            with when("Persona returns the completed inquiry"):
                pass
            with then("the Customer has a verified Persona inquiry"):
                # typescript body to translate:
                # expect(inquiry).toBeInstanceOf(PersonaInquiry);
                # expect(inquiry.inquiryId).toBe(completedInquiryId);
                # expect(inquiry.verified).toBe(true);
                # expect(cart.customer.personaInquiry).toBe(inquiry);
                pass
            with and_("My Paradise maps the inquiry onto identity and address"):
                # typescript body to translate:
                # expect(cart.customer.identity.name).toBe(expectedValidIdentity.name);
                # expect(cart.customer.identity.lastName).toBe(expectedValidIdentity.lastName);
                # expect(cart.customer.identity.dateOfBirth).toBe(expectedValidIdentity.dateOfBirth);
                # expect(cart.customer.identity.idNationality).toBe(expectedValidIdentity.idNationality);
                # expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
                # expect(cart.customer.identity.idType).toBe(expectedValidIdentity.idType);
                # expect(cart.customer.address.street).toBe(expectedValidAddress.street);
                # expect(cart.customer.address.parish).toBe(expectedValidAddress.parish);
                # expect(cart.customer.address.postalCode).toBe(expectedValidAddress.postalCode);
                pass
            with and_("Customer verified stays false until the Customer confirms their identity"):
                # typescript body to translate:
                # expect(cart.customer.verified).toBe(false);
                pass
            with when("Persona returns the valid Persona document"):
                pass
            with then("identity expiry date is the Persona document expiration date"):
                # typescript body to translate:
                # expect(cart.customer.identity.expiryDate).toBe(validPersonaDocument.expirationDate);
                pass
        with scenario("Persona inquiry not completed"):
            # typescript body to translate:
            # let cart: Cart;
            # let inquiry: PersonaInquiry;
            # examples: failedPersonaInquiryResult, customerWithProfile
            with given("the Customer has no idNumber on identity"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                # personaGateway.seedInquiry(failedPersonaInquiryResult);
                pass
            with when("the Customer creates a Persona inquiry"):
                # typescript body to translate:
                # inquiry = cart.customer.createPersonaInquiry();
                pass
            with then("My Paradise sends the inquiry request to Persona with the Customer email"):
                # typescript body to translate:
                # expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
                pass
            with when("Persona returns the failed Persona inquiry"):
                pass
            with then("the Customer has an unverified Persona inquiry"):
                # typescript body to translate:
                # expect(inquiry.inquiryId).toBe(failedPersonaInquiryResult.inquiryId);
                # expect(inquiry.verified).toBe(false);
                pass
            with and_("identity and address stay empty"):
                # typescript body to translate:
                # expect(cart.customer.identity.idNumber).toBe('');
                # expect(cart.customer.address.street).toBe('');
                pass
        with scenario("No government ID document on inquiry"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: completedInquiryWithoutDocument, customerWithProfile
            with given("the completed Persona inquiry has no government ID document"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                # personaGateway.seedInquiry(completedInquiryWithoutDocument);
                pass
            with when("the Customer creates a Persona inquiry"):
                # typescript body to translate:
                # cart.customer.createPersonaInquiry();
                pass
            with then("My Paradise sends the inquiry request to Persona"):
                # typescript body to translate:
                # expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
                pass
            with and_("My Paradise does not retrieve a Persona document"):
                # typescript body to translate:
                # expect(readDocumentSpy).not.toHaveBeenCalled();
                pass
            with when("Persona returns the completed inquiry without a government ID"):
                pass
            with then("identity expiry date is empty"):
                # typescript body to translate:
                # expect(cart.customer.identity.expiryDate).toBe('');
                pass
        with scenario("Persona errors on inquiry load"):
            # typescript body to translate:
            # let cart: Cart;
            # let inquiry: PersonaInquiry;
            # examples: customerWithProfile
            with given("the Customer has no idNumber on identity"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                # personaGateway.seedCreateError(new Error('Persona unavailable'));
                pass
            with when("the Customer creates a Persona inquiry"):
                # typescript body to translate:
                # inquiry = cart.customer.createPersonaInquiry();
                pass
            with then("My Paradise sends the inquiry request to Persona"):
                # typescript body to translate:
                # expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
                pass
            with when("Persona returns an error"):
                pass
            with then("the Customer has an unverified Persona inquiry"):
                # typescript body to translate:
                # expect(inquiry.verified).toBe(false);
                pass
            with and_("identity stays empty"):
                # typescript body to translate:
                # expect(cart.customer.identity.idNumber).toBe('');
                pass
        with scenario("Document not found"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: completedPersonaInquiryResult, validDocumentId, customerWithProfile
            with given("Persona has no Persona document for that document ID"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                # personaGateway.seedInquiry(completedPersonaInquiryResult);
                # personaGateway.seedReadDocumentError(validDocumentId, new Error('Document not found'));
                pass
            with when("the Customer creates a Persona inquiry"):
                # typescript body to translate:
                # cart.customer.createPersonaInquiry();
                pass
            with then("My Paradise retrieves the Persona document"):
                # typescript body to translate:
                # expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
                pass
            with when("Persona returns that the document is not found"):
                pass
            with then("identity expiry date is empty"):
                # typescript body to translate:
                # expect(cart.customer.identity.expiryDate).toBe('');
                pass
        with scenario("Document email mismatch"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: completedPersonaInquiryResult, validDocumentId, customerWithProfile
            with given("the Persona document email does not match the Customer email"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                # personaGateway.seedInquiry(completedPersonaInquiryResult);
                # personaGateway.seedReadDocumentError(validDocumentId, new Error('Unauthorized'));
                pass
            with when("the Customer creates a Persona inquiry"):
                # typescript body to translate:
                # cart.customer.createPersonaInquiry();
                pass
            with then("My Paradise retrieves the Persona document"):
                # typescript body to translate:
                # expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
                pass
            with when("Persona returns unauthorized"):
                pass
            with then("identity expiry date is empty"):
                # typescript body to translate:
                # expect(cart.customer.identity.expiryDate).toBe('');
                pass
        with scenario("Verify later"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: customerWithProfile
            with given("the Customer has no idNumber on identity"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                pass
            with when("the Customer proceeds without a Persona inquiry"):
                # typescript body to translate:
                # cart.customer.verifyLater();
                pass
            with then("My Paradise does not send an inquiry request to Persona"):
                # typescript body to translate:
                # expect(createInquirySpy).not.toHaveBeenCalled();
                pass
            with and_("no Persona inquiry is stored"):
                # typescript body to translate:
                # expect(cart.customer.personaInquiry).toBeNull();
                pass
            with and_("the Customer is still on the Profile KYC step"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
                pass
        with scenario("Enter valid identity and address"):
            # typescript body to translate:
            # let cart: Cart;
            # let missing: ProfileRequirement[];
            # examples: customerWithProfile, enteredValidAddress, enteredValidIdentity, expectedValidAddress, expectedValidIdentity
            with given("the Customer has a My Paradise customer in session"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                pass
            with when("the Customer enters valid identity and address"):
                # typescript body to translate:
                # missing = cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
                pass
            with then("all profile requirements are met"):
                # typescript body to translate:
                # expect(missing).toEqual([]);
                pass
            with and_("the Customer can confirm their identity"):
                # typescript body to translate:
                # expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
                # expect(cart.customer.address.street).toBe(expectedValidAddress.street);
                pass
        with scenario("Enter identity after a verified Persona inquiry"):
            # typescript body to translate:
            # let cart: Cart;
            # let missing: ProfileRequirement[];
            # examples: completedInquiryId, customerWithProfile, enteredValidAddress, enteredValidIdentity, expectedValidIdentity, validProfileSeed
            with given("the Customer has a verified Persona inquiry mapped onto valid identity"):
                # typescript body to translate:
                # cart = await customerWithProfile(validProfileSeed({ inquiryId: completedInquiryId }));
                pass
            with when("the Customer enters the mapped identity and address"):
                # typescript body to translate:
                # missing = cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
                pass
            with then("all profile requirements are met"):
                # typescript body to translate:
                # expect(missing).toEqual([]);
                pass
            with and_("the ID fields are present on identity"):
                # typescript body to translate:
                # expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
                # expect(cart.customer.identity.idType).toBe(expectedValidIdentity.idType);
                pass
        with scenario("Re-enter a verified identity"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: completedInquiryId, customerWithProfile, enteredValidAddress, enteredValidIdentity, expectedValidIdentity, validProfileSeed
            with given("the Customer has valid identity already verified"):
                # typescript body to translate:
                # cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
                pass
            with when("the Customer re-enters valid identity"):
                # typescript body to translate:
                # cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
                pass
            with then("the identity is no longer verified"):
                # typescript body to translate:
                # expect(cart.customer.verified).toBe(false);
                pass
            with and_("the Customer can confirm their identity again"):
                # typescript body to translate:
                # expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
                pass
        with scenario("Enter incomplete identity or address: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # let missing: ProfileRequirement[];
            # examples: customerWithProfile
            with given("the Customer has a My Paradise customer in session"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                pass
            with when("the Customer enters identity and address with ${field} empty"):
                # typescript body to translate:
                # missing = cart.customer.enterProfile(identity, address);
                pass
            with then("${field} is missing"):
                # typescript body to translate:
                # expect(missing.map(row => row.field)).toContain(field);
                # expect(missing.find(row => row.field === field)?.requirement).toBe(requirement);
                pass
            with and_("the Customer cannot confirm their identity"):
                # typescript body to translate:
                # expect(missing.length).toBeGreaterThan(0);
                pass
        with scenario("Confirm identity with a verified Persona inquiry"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: ReturnType<Cart['customer']['confirmIdentity']>;
            # examples: reloadCart, completedInquiryId, customerWithProfile, expectedValidAddress, expectedValidIdentity, validProfileSeed
            with given("the Customer has entered valid identity and address and has a verified Persona inquiry"):
                # typescript body to translate:
                # cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
                pass
            with when("the Customer confirms their identity"):
                # typescript body to translate:
                # result = cart.customer.confirmIdentity();
                pass
            with then("My Paradise maps identity and address onto the Mavenir engaged party and contact medium"):
                # typescript body to translate:
                # expect(patchProfileSpy).toHaveBeenCalledWith(
                #   expect.objectContaining({ id: 'cus_1', inquiryId: completedInquiryId }),
                #   expect.objectContaining({
                #     givenName: 'Jonathan',
                #     familyName: 'Wick',
                #     preferredGivenName: 'Jonathan',
                #     birthDate: expectedValidIdentity.dateOfBirth,
                #     individualIdentification: expect.objectContaining({
                #       identificationId: expectedValidIdentity.idNumber,
                #       identificationType: expectedValidIdentity.idType,
                #       issuingAuthority: expectedValidIdentity.idNationality,
                #       validated: true,
                #       endDateTime: expectedValidIdentity.expiryDate,
                #     }),
                #   }),
                #   expect.objectContaining({
                #     street1: expectedValidAddress.street,
                #     street2: expectedValidAddress.complement,
                #     city: expectedValidAddress.city,
                #     stateOrProvince: expectedValidAddress.parish,
                #     postCode: expectedValidAddress.postalCode,
                #     country: 'Bermuda',
                #     phoneNumber: expectedValidIdentity.otherPhoneNumber,
                #   }),
                # );
                pass
            with and_("My Paradise sends the profile patch to Mavenir"):
                # typescript body to translate:
                # expect(patchProfileSpy).toHaveBeenCalledOnce();
                pass
            with when("Mavenir patches the customer"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the Customer identity is persisted"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Object);
                # expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
                pass
            with and_("the Customer is verified"):
                # typescript body to translate:
                # expect(cart.customer.verified).toBe(true);
                pass
        with scenario("Customer already exists"):
            # typescript body to translate:
            # let cart: Cart;
            # let caught: unknown;
            # examples: completedInquiryId, customerWithProfile, expectedValidIdentity, validProfileSeed
            with given("another Mavenir customer already has identity idNumber I1234562"):
                # typescript body to translate:
                # cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
                # portalGateway.seedCustomerById('cus_other', 'other@example.com', { idNumber: expectedValidIdentity.idNumber });
                pass
            with when("the Customer confirms their identity"):
                # typescript body to translate:
                # try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
                pass
            with then("My Paradise sends the profile patch to Mavenir"):
                # typescript body to translate:
                # expect(patchProfileSpy).toHaveBeenCalled();
                pass
            with and_("the identity cannot be confirmed because a customer with that information already exists"):
                # typescript body to translate:
                # expect(caught).toBeInstanceOf(CustomerException);
                # expect(caught).toHaveProperty('operation', 'confirmIdentity');
                # expect(caught).toHaveProperty('message', 'Customer already exists.');
                pass
        with scenario("Profile requirements unmet"):
            # typescript body to translate:
            # let cart: Cart;
            # let caught: unknown;
            # examples: customerWithProfile
            with given("the Customer has not entered identity or address"):
                # typescript body to translate:
                # cart = await customerWithProfile();
                pass
            with when("the Customer confirms their identity"):
                # typescript body to translate:
                # try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
                pass
            with then("the identity cannot be confirmed"):
                # typescript body to translate:
                # expect(caught).toBeInstanceOf(CustomerException);
                # expect(caught).toHaveProperty('operation', 'confirmIdentity');
                pass
            with and_("My Paradise does not send a profile patch to Mavenir"):
                # typescript body to translate:
                # expect(patchProfileSpy).not.toHaveBeenCalled();
                pass
        with scenario("Mavenir profile patch error"):
            # typescript body to translate:
            # let cart: Cart;
            # let caught: unknown;
            # examples: completedInquiryId, customerWithProfile, validProfileSeed
            with given("Mavenir returns a profile patch error"):
                # typescript body to translate:
                # cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
                # portalGateway.seedPatchProfileError(new Error('Mavenir unavailable'));
                pass
            with when("the Customer confirms their identity"):
                # typescript body to translate:
                # try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
                pass
            with then("My Paradise sends the profile patch to Mavenir"):
                # typescript body to translate:
                # expect(patchProfileSpy).toHaveBeenCalled();
                pass
            with and_("the identity cannot be confirmed"):
                # typescript body to translate:
                # expect(caught).toBeInstanceOf(CustomerException);
                # expect(caught).toHaveProperty('operation', 'confirmIdentity');
                # expect(caught).toHaveProperty('message', 'Something went wrong, please contact the support.');
                pass

# Story: Collect Identity With Brand Amassador
with story("Collect Identity With Brand Amassador"):
    # typescript body to translate:
    # it.skip('Flagged — Ambassador WhatsApp collection is off-system', () => {});
        pass
