/**
 * Epic: Get Verified Profile
 * Orders: 0.0.7
 */

import { background, scenario, story } from "../story-test.js";
import { customerWithProfile, expectedValidIdentity, completedInquiryId, completedPersonaInquiryResult, validDocumentId, validPersonaDocument, expectedValidAddress, failedPersonaInquiryResult, completedInquiryWithoutDocument, enteredValidAddress, enteredValidIdentity, validProfileSeed, reloadCart } from "./examples";

/**
 * Story: Customer Complete Persona Kyc
 */

story('Customer Complete Persona Kyc', () => {
  // typescript body to translate:
  // let createInquirySpy: MockInstance<typeof personaGateway.create>;
  // let readDocumentSpy: MockInstance<typeof personaGateway.readDocument>;
  // let patchProfileSpy: MockInstance<typeof portalGateway.patchProfile>;
  //
  // beforeEach(() => {
  //   createInquirySpy = vi.spyOn(personaGateway, 'create');
  //   readDocumentSpy = vi.spyOn(personaGateway, 'readDocument');
  //   patchProfileSpy = vi.spyOn(portalGateway, 'patchProfile');
  // });
  //
  // incompleteProfileOutlines.forEach(({ example, field, requirement, identity, address }) => {
  // });
  scenario('Persona verification required', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: PersonaInquiryValidation;
    // examples: customerWithProfile
    given('the Customer has a cart with a plan, number, and SIM and no idNumber', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // TODO: implement step
    });
    when('the Customer validates whether a Persona inquiry is required', () => {
      // typescript body to translate:
      // result = cart.customer.validatePersonaInquiry();
      // TODO: implement step
    });
    then('a Persona inquiry is required', () => {
      // typescript body to translate:
      // expect(result).toBe(PersonaInquiryValidation.Required);
      // TODO: implement step
    })
      .and('the Customer is on the Profile KYC step', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
        // TODO: implement step
      });
  });

  scenario('Persona verification already complete', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: PersonaInquiryValidation;
    // examples: customerWithProfile, expectedValidIdentity
    given('the Customer has identity with an idNumber', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile({ idNumber: expectedValidIdentity.idNumber });
      // TODO: implement step
    });
    when('the Customer validates whether a Persona inquiry is required', () => {
      // typescript body to translate:
      // result = cart.customer.validatePersonaInquiry();
      // TODO: implement step
    });
    then('the Persona inquiry is already complete', () => {
      // typescript body to translate:
      // expect(result).toBe(PersonaInquiryValidation.Complete);
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
        // TODO: implement step
      });
  });

  scenario('Create a completed Persona inquiry', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let inquiry: PersonaInquiry;
    // examples: completedInquiryId, completedPersonaInquiryResult, validDocumentId, validPersonaDocument, customerWithProfile, expectedValidAddress, expectedValidIdentity
    given('the Customer has no idNumber on identity', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // personaGateway.seedInquiry(completedPersonaInquiryResult);
      // personaGateway.seedDocument(validPersonaDocument);
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // typescript body to translate:
      // inquiry = cart.customer.createPersonaInquiry();
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona with the Customer email', () => {
      // typescript body to translate:
      // expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
      // TODO: implement step
    })
      .and('My Paradise retrieves the Persona document', () => {
        // typescript body to translate:
        // expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
        // TODO: implement step
      });
    when('Persona returns the completed inquiry', () => {
      // TODO: implement step
    });
    then('the Customer has a verified Persona inquiry', () => {
      // typescript body to translate:
      // expect(inquiry).toBeInstanceOf(PersonaInquiry);
      // expect(inquiry.inquiryId).toBe(completedInquiryId);
      // expect(inquiry.verified).toBe(true);
      // expect(cart.customer.personaInquiry).toBe(inquiry);
      // TODO: implement step
    })
      .and('My Paradise maps the inquiry onto identity and address', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.name).toBe(expectedValidIdentity.name);
        // expect(cart.customer.identity.lastName).toBe(expectedValidIdentity.lastName);
        // expect(cart.customer.identity.dateOfBirth).toBe(expectedValidIdentity.dateOfBirth);
        // expect(cart.customer.identity.idNationality).toBe(expectedValidIdentity.idNationality);
        // expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
        // expect(cart.customer.identity.idType).toBe(expectedValidIdentity.idType);
        // expect(cart.customer.address.street).toBe(expectedValidAddress.street);
        // expect(cart.customer.address.parish).toBe(expectedValidAddress.parish);
        // expect(cart.customer.address.postalCode).toBe(expectedValidAddress.postalCode);
        // TODO: implement step
      })
      .and('Customer verified stays false until the Customer confirms their identity', () => {
        // typescript body to translate:
        // expect(cart.customer.verified).toBe(false);
        // TODO: implement step
      });
    when('Persona returns the valid Persona document', () => {
      // TODO: implement step
    });
    then('identity expiry date is the Persona document expiration date', () => {
      // typescript body to translate:
      // expect(cart.customer.identity.expiryDate).toBe(validPersonaDocument.expirationDate);
      // TODO: implement step
    });
  });

  scenario('Persona inquiry not completed', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let inquiry: PersonaInquiry;
    // examples: failedPersonaInquiryResult, customerWithProfile
    given('the Customer has no idNumber on identity', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // personaGateway.seedInquiry(failedPersonaInquiryResult);
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // typescript body to translate:
      // inquiry = cart.customer.createPersonaInquiry();
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona with the Customer email', () => {
      // typescript body to translate:
      // expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
      // TODO: implement step
    });
    when('Persona returns the failed Persona inquiry', () => {
      // TODO: implement step
    });
    then('the Customer has an unverified Persona inquiry', () => {
      // typescript body to translate:
      // expect(inquiry.inquiryId).toBe(failedPersonaInquiryResult.inquiryId);
      // expect(inquiry.verified).toBe(false);
      // TODO: implement step
    })
      .and('identity and address stay empty', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.idNumber).toBe('');
        // expect(cart.customer.address.street).toBe('');
        // TODO: implement step
      });
  });

  scenario('No government ID document on inquiry', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: completedInquiryWithoutDocument, customerWithProfile
    given('the completed Persona inquiry has no government ID document', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // personaGateway.seedInquiry(completedInquiryWithoutDocument);
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // typescript body to translate:
      // cart.customer.createPersonaInquiry();
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona', () => {
      // typescript body to translate:
      // expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
      // TODO: implement step
    })
      .and('My Paradise does not retrieve a Persona document', () => {
        // typescript body to translate:
        // expect(readDocumentSpy).not.toHaveBeenCalled();
        // TODO: implement step
      });
    when('Persona returns the completed inquiry without a government ID', () => {
      // TODO: implement step
    });
    then('identity expiry date is empty', () => {
      // typescript body to translate:
      // expect(cart.customer.identity.expiryDate).toBe('');
      // TODO: implement step
    });
  });

  scenario('Persona errors on inquiry load', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let inquiry: PersonaInquiry;
    // examples: customerWithProfile
    given('the Customer has no idNumber on identity', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // personaGateway.seedCreateError(new Error('Persona unavailable'));
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // typescript body to translate:
      // inquiry = cart.customer.createPersonaInquiry();
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona', () => {
      // typescript body to translate:
      // expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
      // TODO: implement step
    });
    when('Persona returns an error', () => {
      // TODO: implement step
    });
    then('the Customer has an unverified Persona inquiry', () => {
      // typescript body to translate:
      // expect(inquiry.verified).toBe(false);
      // TODO: implement step
    })
      .and('identity stays empty', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.idNumber).toBe('');
        // TODO: implement step
      });
  });

  scenario('Document not found', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: completedPersonaInquiryResult, validDocumentId, customerWithProfile
    given('Persona has no Persona document for that document ID', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // personaGateway.seedInquiry(completedPersonaInquiryResult);
      // personaGateway.seedReadDocumentError(validDocumentId, new Error('Document not found'));
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // typescript body to translate:
      // cart.customer.createPersonaInquiry();
      // TODO: implement step
    });
    then('My Paradise retrieves the Persona document', () => {
      // typescript body to translate:
      // expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
      // TODO: implement step
    });
    when('Persona returns that the document is not found', () => {
      // TODO: implement step
    });
    then('identity expiry date is empty', () => {
      // typescript body to translate:
      // expect(cart.customer.identity.expiryDate).toBe('');
      // TODO: implement step
    });
  });

  scenario('Document email mismatch', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: completedPersonaInquiryResult, validDocumentId, customerWithProfile
    given('the Persona document email does not match the Customer email', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // personaGateway.seedInquiry(completedPersonaInquiryResult);
      // personaGateway.seedReadDocumentError(validDocumentId, new Error('Unauthorized'));
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // typescript body to translate:
      // cart.customer.createPersonaInquiry();
      // TODO: implement step
    });
    then('My Paradise retrieves the Persona document', () => {
      // typescript body to translate:
      // expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
      // TODO: implement step
    });
    when('Persona returns unauthorized', () => {
      // TODO: implement step
    });
    then('identity expiry date is empty', () => {
      // typescript body to translate:
      // expect(cart.customer.identity.expiryDate).toBe('');
      // TODO: implement step
    });
  });

  scenario('Verify later', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: customerWithProfile
    given('the Customer has no idNumber on identity', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // TODO: implement step
    });
    when('the Customer proceeds without a Persona inquiry', () => {
      // typescript body to translate:
      // cart.customer.verifyLater();
      // TODO: implement step
    });
    then('My Paradise does not send an inquiry request to Persona', () => {
      // typescript body to translate:
      // expect(createInquirySpy).not.toHaveBeenCalled();
      // TODO: implement step
    })
      .and('no Persona inquiry is stored', () => {
        // typescript body to translate:
        // expect(cart.customer.personaInquiry).toBeNull();
        // TODO: implement step
      })
      .and('the Customer is still on the Profile KYC step', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
        // TODO: implement step
      });
  });

  scenario('Enter valid identity and address', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let missing: ProfileRequirement[];
    // examples: customerWithProfile, enteredValidAddress, enteredValidIdentity, expectedValidAddress, expectedValidIdentity
    given('the Customer has a My Paradise customer in session', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // TODO: implement step
    });
    when('the Customer enters valid identity and address', () => {
      // typescript body to translate:
      // missing = cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
      // TODO: implement step
    });
    then('all profile requirements are met', () => {
      // typescript body to translate:
      // expect(missing).toEqual([]);
      // TODO: implement step
    })
      .and('the Customer can confirm their identity', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
        // expect(cart.customer.address.street).toBe(expectedValidAddress.street);
        // TODO: implement step
      });
  });

  scenario('Enter identity after a verified Persona inquiry', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let missing: ProfileRequirement[];
    // examples: completedInquiryId, customerWithProfile, enteredValidAddress, enteredValidIdentity, expectedValidIdentity, validProfileSeed
    given('the Customer has a verified Persona inquiry mapped onto valid identity', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile(validProfileSeed({ inquiryId: completedInquiryId }));
      // TODO: implement step
    });
    when('the Customer enters the mapped identity and address', () => {
      // typescript body to translate:
      // missing = cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
      // TODO: implement step
    });
    then('all profile requirements are met', () => {
      // typescript body to translate:
      // expect(missing).toEqual([]);
      // TODO: implement step
    })
      .and('the ID fields are present on identity', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
        // expect(cart.customer.identity.idType).toBe(expectedValidIdentity.idType);
        // TODO: implement step
      });
  });

  scenario('Re-enter a verified identity', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: completedInquiryId, customerWithProfile, enteredValidAddress, enteredValidIdentity, expectedValidIdentity, validProfileSeed
    given('the Customer has valid identity already verified', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
      // TODO: implement step
    });
    when('the Customer re-enters valid identity', () => {
      // typescript body to translate:
      // cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
      // TODO: implement step
    });
    then('the identity is no longer verified', () => {
      // typescript body to translate:
      // expect(cart.customer.verified).toBe(false);
      // TODO: implement step
    })
      .and('the Customer can confirm their identity again', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
        // TODO: implement step
      });
  });

  scenario('Enter incomplete identity or address: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let missing: ProfileRequirement[];
    // examples: customerWithProfile
    given('the Customer has a My Paradise customer in session', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // TODO: implement step
    });
    when('the Customer enters identity and address with ${field} empty', () => {
      // typescript body to translate:
      // missing = cart.customer.enterProfile(identity, address);
      // TODO: implement step
    });
    then('${field} is missing', () => {
      // typescript body to translate:
      // expect(missing.map(row => row.field)).toContain(field);
      // expect(missing.find(row => row.field === field)?.requirement).toBe(requirement);
      // TODO: implement step
    })
      .and('the Customer cannot confirm their identity', () => {
        // typescript body to translate:
        // expect(missing.length).toBeGreaterThan(0);
        // TODO: implement step
      });
  });

  scenario('Confirm identity with a verified Persona inquiry', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: ReturnType<Cart['customer']['confirmIdentity']>;
    // examples: reloadCart, completedInquiryId, customerWithProfile, expectedValidAddress, expectedValidIdentity, validProfileSeed
    given('the Customer has entered valid identity and address and has a verified Persona inquiry', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // typescript body to translate:
      // result = cart.customer.confirmIdentity();
      // TODO: implement step
    });
    then('My Paradise maps identity and address onto the Mavenir engaged party and contact medium', () => {
      // typescript body to translate:
      // expect(patchProfileSpy).toHaveBeenCalledWith(
      //   expect.objectContaining({ id: 'cus_1', inquiryId: completedInquiryId }),
      //   expect.objectContaining({
      //     givenName: 'Jonathan',
      //     familyName: 'Wick',
      //     preferredGivenName: 'Jonathan',
      //     birthDate: expectedValidIdentity.dateOfBirth,
      //     individualIdentification: expect.objectContaining({
      //       identificationId: expectedValidIdentity.idNumber,
      //       identificationType: expectedValidIdentity.idType,
      //       issuingAuthority: expectedValidIdentity.idNationality,
      //       validated: true,
      //       endDateTime: expectedValidIdentity.expiryDate,
      //     }),
      //   }),
      //   expect.objectContaining({
      //     street1: expectedValidAddress.street,
      //     street2: expectedValidAddress.complement,
      //     city: expectedValidAddress.city,
      //     stateOrProvince: expectedValidAddress.parish,
      //     postCode: expectedValidAddress.postalCode,
      //     country: 'Bermuda',
      //     phoneNumber: expectedValidIdentity.otherPhoneNumber,
      //   }),
      // );
      // TODO: implement step
    })
      .and('My Paradise sends the profile patch to Mavenir', () => {
        // typescript body to translate:
        // expect(patchProfileSpy).toHaveBeenCalledOnce();
        // TODO: implement step
      });
    when('Mavenir patches the customer', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the Customer identity is persisted', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Object);
      // expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
      // TODO: implement step
    })
      .and('the Customer is verified', () => {
        // typescript body to translate:
        // expect(cart.customer.verified).toBe(true);
        // TODO: implement step
      });
  });

  scenario('Customer already exists', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let caught: unknown;
    // examples: completedInquiryId, customerWithProfile, expectedValidIdentity, validProfileSeed
    given('another Mavenir customer already has identity idNumber I1234562', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
      // portalGateway.seedCustomerById('cus_other', 'other@example.com', { idNumber: expectedValidIdentity.idNumber });
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // typescript body to translate:
      // try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
      // TODO: implement step
    });
    then('My Paradise sends the profile patch to Mavenir', () => {
      // typescript body to translate:
      // expect(patchProfileSpy).toHaveBeenCalled();
      // TODO: implement step
    })
      .and('the identity cannot be confirmed because a customer with that information already exists', () => {
        // typescript body to translate:
        // expect(caught).toBeInstanceOf(CustomerException);
        // expect(caught).toHaveProperty('operation', 'confirmIdentity');
        // expect(caught).toHaveProperty('message', 'Customer already exists.');
        // TODO: implement step
      });
  });

  scenario('Profile requirements unmet', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let caught: unknown;
    // examples: customerWithProfile
    given('the Customer has not entered identity or address', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile();
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // typescript body to translate:
      // try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
      // TODO: implement step
    });
    then('the identity cannot be confirmed', () => {
      // typescript body to translate:
      // expect(caught).toBeInstanceOf(CustomerException);
      // expect(caught).toHaveProperty('operation', 'confirmIdentity');
      // TODO: implement step
    })
      .and('My Paradise does not send a profile patch to Mavenir', () => {
        // typescript body to translate:
        // expect(patchProfileSpy).not.toHaveBeenCalled();
        // TODO: implement step
      });
  });

  scenario('Mavenir profile patch error', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let caught: unknown;
    // examples: completedInquiryId, customerWithProfile, validProfileSeed
    given('Mavenir returns a profile patch error', async () => {
      // typescript body to translate:
      // cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
      // portalGateway.seedPatchProfileError(new Error('Mavenir unavailable'));
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // typescript body to translate:
      // try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
      // TODO: implement step
    });
    then('My Paradise sends the profile patch to Mavenir', () => {
      // typescript body to translate:
      // expect(patchProfileSpy).toHaveBeenCalled();
      // TODO: implement step
    })
      .and('the identity cannot be confirmed', () => {
        // typescript body to translate:
        // expect(caught).toBeInstanceOf(CustomerException);
        // expect(caught).toHaveProperty('operation', 'confirmIdentity');
        // expect(caught).toHaveProperty('message', 'Something went wrong, please contact the support.');
        // TODO: implement step
      });
  });
});

/**
 * Story: Collect Identity With Brand Amassador
 */

story('Collect Identity With Brand Amassador', () => {
  // typescript body to translate:
  // it.skip('Flagged — Ambassador WhatsApp collection is off-system', () => {});
  // TODO: add main-flow scenario
});
