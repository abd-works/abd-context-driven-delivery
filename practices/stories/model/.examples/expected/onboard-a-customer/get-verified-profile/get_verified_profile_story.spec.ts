import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { CustomerException } from '../../../domain/customer/Customer';
import {
  PersonaInquiryValidation,
  type ProfileRequirement,
} from '../../../domain/KYC/Profile';
import { type Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { PersonaInquiry, personaGateway } from '../../../domain/systems/persona';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { reloadCart } from '../get-number/examples/cart.examples';
import {
  completedInquiryId,
  completedInquiryWithoutDocument,
  completedPersonaInquiryResult,
  failedPersonaInquiryResult,
  validDocumentId,
  validPersonaDocument,
} from './examples/persona-inquiry.examples';
import {
  customerWithProfile,
  incompleteProfileOutlines,
  enteredValidAddress,
  enteredValidIdentity,
  expectedValidAddress,
  expectedValidIdentity,
  validProfileSeed,
} from './examples/profile.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  portalGateway.reset();
  personaGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Customer Complete Persona Kyc', () => {
  let createInquirySpy: MockInstance<typeof personaGateway.create>;
  let readDocumentSpy: MockInstance<typeof personaGateway.readDocument>;
  let patchProfileSpy: MockInstance<typeof portalGateway.patchProfile>;

  beforeEach(() => {
    createInquirySpy = vi.spyOn(personaGateway, 'create');
    readDocumentSpy = vi.spyOn(personaGateway, 'readDocument');
    patchProfileSpy = vi.spyOn(portalGateway, 'patchProfile');
  });

  scenario('Persona verification required', ({ given, when, then }) => {
    let cart: Cart;
    let result: PersonaInquiryValidation;

    given('the Customer has a cart with a plan, number, and SIM and no idNumber', async () => {
      cart = await customerWithProfile();
    });
    when('the Customer validates whether a Persona inquiry is required', () => {
      result = cart.customer.validatePersonaInquiry();
    });
    then('a Persona inquiry is required', () => {
      expect(result).toBe(PersonaInquiryValidation.Required);
    }).and('the Customer is on the Profile KYC step', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
    });
  });

  scenario('Persona verification already complete', ({ given, when, then }) => {
    let cart: Cart;
    let result: PersonaInquiryValidation;

    given('the Customer has identity with an idNumber', async () => {
      cart = await customerWithProfile({ idNumber: expectedValidIdentity.idNumber });
    });
    when('the Customer validates whether a Persona inquiry is required', () => {
      result = cart.customer.validatePersonaInquiry();
    });
    then('the Persona inquiry is already complete', () => {
      expect(result).toBe(PersonaInquiryValidation.Complete);
    }).and('the Customer is forwarded to Checkout', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
    });
  });

  scenario('Create a completed Persona inquiry', ({ given, when, then }) => {
    let cart: Cart;
    let inquiry: PersonaInquiry;

    given('the Customer has no idNumber on identity', async () => {
      cart = await customerWithProfile();
      personaGateway.seedInquiry(completedPersonaInquiryResult);
      personaGateway.seedDocument(validPersonaDocument);
    });
    when('the Customer creates a Persona inquiry', () => {
      inquiry = cart.customer.createPersonaInquiry();
    });
    then('My Paradise sends the inquiry request to Persona with the Customer email', () => {
      expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
    }).and('My Paradise retrieves the Persona document', () => {
      expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
    });
    when('Persona returns the completed inquiry', () => {});
    then('the Customer has a verified Persona inquiry', () => {
      expect(inquiry).toBeInstanceOf(PersonaInquiry);
      expect(inquiry.inquiryId).toBe(completedInquiryId);
      expect(inquiry.verified).toBe(true);
      expect(cart.customer.personaInquiry).toBe(inquiry);
    }).and('My Paradise maps the inquiry onto identity and address', () => {
      expect(cart.customer.identity.name).toBe(expectedValidIdentity.name);
      expect(cart.customer.identity.lastName).toBe(expectedValidIdentity.lastName);
      expect(cart.customer.identity.dateOfBirth).toBe(expectedValidIdentity.dateOfBirth);
      expect(cart.customer.identity.idNationality).toBe(expectedValidIdentity.idNationality);
      expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
      expect(cart.customer.identity.idType).toBe(expectedValidIdentity.idType);
      expect(cart.customer.address.street).toBe(expectedValidAddress.street);
      expect(cart.customer.address.parish).toBe(expectedValidAddress.parish);
      expect(cart.customer.address.postalCode).toBe(expectedValidAddress.postalCode);
    }).and('Customer verified stays false until the Customer confirms their identity', () => {
      expect(cart.customer.verified).toBe(false);
    });
    when('Persona returns the valid Persona document', () => {});
    then('identity expiry date is the Persona document expiration date', () => {
      expect(cart.customer.identity.expiryDate).toBe(validPersonaDocument.expirationDate);
    });
  });

  scenario('Persona inquiry not completed', ({ given, when, then }) => {
    let cart: Cart;
    let inquiry: PersonaInquiry;

    given('the Customer has no idNumber on identity', async () => {
      cart = await customerWithProfile();
      personaGateway.seedInquiry(failedPersonaInquiryResult);
    });
    when('the Customer creates a Persona inquiry', () => {
      inquiry = cart.customer.createPersonaInquiry();
    });
    then('My Paradise sends the inquiry request to Persona with the Customer email', () => {
      expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
    });
    when('Persona returns the failed Persona inquiry', () => {});
    then('the Customer has an unverified Persona inquiry', () => {
      expect(inquiry.inquiryId).toBe(failedPersonaInquiryResult.inquiryId);
      expect(inquiry.verified).toBe(false);
    }).and('identity and address stay empty', () => {
      expect(cart.customer.identity.idNumber).toBe('');
      expect(cart.customer.address.street).toBe('');
    });
  });

  scenario('No government ID document on inquiry', ({ given, when, then }) => {
    let cart: Cart;

    given('the completed Persona inquiry has no government ID document', async () => {
      cart = await customerWithProfile();
      personaGateway.seedInquiry(completedInquiryWithoutDocument);
    });
    when('the Customer creates a Persona inquiry', () => {
      cart.customer.createPersonaInquiry();
    });
    then('My Paradise sends the inquiry request to Persona', () => {
      expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
    }).and('My Paradise does not retrieve a Persona document', () => {
      expect(readDocumentSpy).not.toHaveBeenCalled();
    });
    when('Persona returns the completed inquiry without a government ID', () => {});
    then('identity expiry date is empty', () => {
      expect(cart.customer.identity.expiryDate).toBe('');
    });
  });

  scenario('Persona errors on inquiry load', ({ given, when, then }) => {
    let cart: Cart;
    let inquiry: PersonaInquiry;

    given('the Customer has no idNumber on identity', async () => {
      cart = await customerWithProfile();
      personaGateway.seedCreateError(new Error('Persona unavailable'));
    });
    when('the Customer creates a Persona inquiry', () => {
      inquiry = cart.customer.createPersonaInquiry();
    });
    then('My Paradise sends the inquiry request to Persona', () => {
      expect(createInquirySpy).toHaveBeenCalledWith(cart.customer.identity.email);
    });
    when('Persona returns an error', () => {});
    then('the Customer has an unverified Persona inquiry', () => {
      expect(inquiry.verified).toBe(false);
    }).and('identity stays empty', () => {
      expect(cart.customer.identity.idNumber).toBe('');
    });
  });

  scenario('Document not found', ({ given, when, then }) => {
    let cart: Cart;

    given('Persona has no Persona document for that document ID', async () => {
      cart = await customerWithProfile();
      personaGateway.seedInquiry(completedPersonaInquiryResult);
      personaGateway.seedReadDocumentError(validDocumentId, new Error('Document not found'));
    });
    when('the Customer creates a Persona inquiry', () => {
      cart.customer.createPersonaInquiry();
    });
    then('My Paradise retrieves the Persona document', () => {
      expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
    });
    when('Persona returns that the document is not found', () => {});
    then('identity expiry date is empty', () => {
      expect(cart.customer.identity.expiryDate).toBe('');
    });
  });

  scenario('Document email mismatch', ({ given, when, then }) => {
    let cart: Cart;

    given('the Persona document email does not match the Customer email', async () => {
      cart = await customerWithProfile();
      personaGateway.seedInquiry(completedPersonaInquiryResult);
      personaGateway.seedReadDocumentError(validDocumentId, new Error('Unauthorized'));
    });
    when('the Customer creates a Persona inquiry', () => {
      cart.customer.createPersonaInquiry();
    });
    then('My Paradise retrieves the Persona document', () => {
      expect(readDocumentSpy).toHaveBeenCalledWith(validDocumentId);
    });
    when('Persona returns unauthorized', () => {});
    then('identity expiry date is empty', () => {
      expect(cart.customer.identity.expiryDate).toBe('');
    });
  });

  scenario('Verify later', ({ given, when, then }) => {
    let cart: Cart;

    given('the Customer has no idNumber on identity', async () => {
      cart = await customerWithProfile();
    });
    when('the Customer proceeds without a Persona inquiry', () => {
      cart.customer.verifyLater();
    });
    then('My Paradise does not send an inquiry request to Persona', () => {
      expect(createInquirySpy).not.toHaveBeenCalled();
    }).and('no Persona inquiry is stored', () => {
      expect(cart.customer.personaInquiry).toBeNull();
    }).and('the Customer is still on the Profile KYC step', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
    });
  });

  scenario('Enter valid identity and address', ({ given, when, then }) => {
    let cart: Cart;
    let missing: ProfileRequirement[];

    given('the Customer has a My Paradise customer in session', async () => {
      cart = await customerWithProfile();
    });
    when('the Customer enters valid identity and address', () => {
      missing = cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
    });
    then('all profile requirements are met', () => {
      expect(missing).toEqual([]);
    }).and('the Customer can confirm their identity', () => {
      expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
      expect(cart.customer.address.street).toBe(expectedValidAddress.street);
    });
  });

  scenario('Enter identity after a verified Persona inquiry', ({ given, when, then }) => {
    let cart: Cart;
    let missing: ProfileRequirement[];

    given('the Customer has a verified Persona inquiry mapped onto valid identity', async () => {
      cart = await customerWithProfile(validProfileSeed({ inquiryId: completedInquiryId }));
    });
    when('the Customer enters the mapped identity and address', () => {
      missing = cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
    });
    then('all profile requirements are met', () => {
      expect(missing).toEqual([]);
    }).and('the ID fields are present on identity', () => {
      expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
      expect(cart.customer.identity.idType).toBe(expectedValidIdentity.idType);
    });
  });

  scenario('Re-enter a verified identity', ({ given, when, then }) => {
    let cart: Cart;

    given('the Customer has valid identity already verified', async () => {
      cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
    });
    when('the Customer re-enters valid identity', () => {
      cart.customer.enterProfile(enteredValidIdentity, enteredValidAddress);
    });
    then('the identity is no longer verified', () => {
      expect(cart.customer.verified).toBe(false);
    }).and('the Customer can confirm their identity again', () => {
      expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
    });
  });

  incompleteProfileOutlines.forEach(({ example, field, requirement, identity, address }) => {
    scenario(`Enter incomplete identity or address: ${example}`, ({ given, when, then }) => {
      let cart: Cart;
      let missing: ProfileRequirement[];

      given('the Customer has a My Paradise customer in session', async () => {
        cart = await customerWithProfile();
      });
      when(`the Customer enters identity and address with ${field} empty`, () => {
        missing = cart.customer.enterProfile(identity, address);
      });
      then(`${field} is missing`, () => {
        expect(missing.map(row => row.field)).toContain(field);
        expect(missing.find(row => row.field === field)?.requirement).toBe(requirement);
      }).and('the Customer cannot confirm their identity', () => {
        expect(missing.length).toBeGreaterThan(0);
      });
    });
  });

  scenario('Confirm identity with a verified Persona inquiry', ({ given, when, then }) => {
    let cart: Cart;
    let result: ReturnType<Cart['customer']['confirmIdentity']>;

    given('the Customer has entered valid identity and address and has a verified Persona inquiry', async () => {
      cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
    });
    when('the Customer confirms their identity', () => {
      result = cart.customer.confirmIdentity();
    });
    then('My Paradise maps identity and address onto the Mavenir engaged party and contact medium', () => {
      expect(patchProfileSpy).toHaveBeenCalledWith(
        expect.objectContaining({ id: 'cus_1', inquiryId: completedInquiryId }),
        expect.objectContaining({
          givenName: 'Jonathan',
          familyName: 'Wick',
          preferredGivenName: 'Jonathan',
          birthDate: expectedValidIdentity.dateOfBirth,
          individualIdentification: expect.objectContaining({
            identificationId: expectedValidIdentity.idNumber,
            identificationType: expectedValidIdentity.idType,
            issuingAuthority: expectedValidIdentity.idNationality,
            validated: true,
            endDateTime: expectedValidIdentity.expiryDate,
          }),
        }),
        expect.objectContaining({
          street1: expectedValidAddress.street,
          street2: expectedValidAddress.complement,
          city: expectedValidAddress.city,
          stateOrProvince: expectedValidAddress.parish,
          postCode: expectedValidAddress.postalCode,
          country: 'Bermuda',
          phoneNumber: expectedValidIdentity.otherPhoneNumber,
        }),
      );
    }).and('My Paradise sends the profile patch to Mavenir', () => {
      expect(patchProfileSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir patches the customer', async () => {
      cart = await reloadCart(cart);
    });
    then('the Customer identity is persisted', () => {
      expect(result).toBeInstanceOf(Object);
      expect(cart.customer.identity.idNumber).toBe(expectedValidIdentity.idNumber);
    }).and('the Customer is verified', () => {
      expect(cart.customer.verified).toBe(true);
    });
  });

  scenario('Customer already exists', ({ given, when, then }) => {
    let cart: Cart;
    let caught: unknown;

    given('another Mavenir customer already has identity idNumber I1234562', async () => {
      cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
      portalGateway.seedCustomerById('cus_other', 'other@example.com', { idNumber: expectedValidIdentity.idNumber });
    });
    when('the Customer confirms their identity', () => {
      try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
    });
    then('My Paradise sends the profile patch to Mavenir', () => {
      expect(patchProfileSpy).toHaveBeenCalled();
    }).and('the identity cannot be confirmed because a customer with that information already exists', () => {
      expect(caught).toBeInstanceOf(CustomerException);
      expect(caught).toHaveProperty('operation', 'confirmIdentity');
      expect(caught).toHaveProperty('message', 'Customer already exists.');
    });
  });

  scenario('Profile requirements unmet', ({ given, when, then }) => {
    let cart: Cart;
    let caught: unknown;

    given('the Customer has not entered identity or address', async () => {
      cart = await customerWithProfile();
    });
    when('the Customer confirms their identity', () => {
      try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
    });
    then('the identity cannot be confirmed', () => {
      expect(caught).toBeInstanceOf(CustomerException);
      expect(caught).toHaveProperty('operation', 'confirmIdentity');
    }).and('My Paradise does not send a profile patch to Mavenir', () => {
      expect(patchProfileSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Mavenir profile patch error', ({ given, when, then }) => {
    let cart: Cart;
    let caught: unknown;

    given('Mavenir returns a profile patch error', async () => {
      cart = await customerWithProfile(validProfileSeed({ validated: true, inquiryId: completedInquiryId }));
      portalGateway.seedPatchProfileError(new Error('Mavenir unavailable'));
    });
    when('the Customer confirms their identity', () => {
      try { cart.customer.confirmIdentity(); } catch (e) { caught = e; }
    });
    then('My Paradise sends the profile patch to Mavenir', () => {
      expect(patchProfileSpy).toHaveBeenCalled();
    }).and('the identity cannot be confirmed', () => {
      expect(caught).toBeInstanceOf(CustomerException);
      expect(caught).toHaveProperty('operation', 'confirmIdentity');
      expect(caught).toHaveProperty('message', 'Something went wrong, please contact the support.');
    });
  });
});

// ---------------------------------------------------------------------------

story('Collect Identity With Brand Amassador', () => {
  it.skip('Flagged — Ambassador WhatsApp collection is off-system', () => {});
});
