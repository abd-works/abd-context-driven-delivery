/**
 * Epic: Get Verified Profile
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Customer Complete Persona Kyc
 * Actor: Customer
 */

story('Customer Complete Persona Kyc', () => {
  background('each', ({ given }) => {
    scenario('Persona verification required', ({ given, when, then }) => {
      then('no idNumber on ++identity++', () => {});
      when('the Customer validates whether a Persona inquiry is required', () => {});
      then('a Persona inquiry is required', () => {}).and('the Customer is on the Profile KYC step', () => {});
    });
    scenario('Persona verification already complete', ({ given, when, then }) => {
      given('the Customer has ++identity++ with an idNumber', () => {});
      when('the Customer validates whether a Persona inquiry is required', () => {});
      then('the Persona inquiry is already complete', () => {}).and('the Customer is forwarded to Checkout', () => {});
    });
    scenario('Create a completed Persona inquiry', ({ given, when, then }) => {
      given('the Customer has no idNumber on ++identity++', () => {});
      when('the Customer creates a Persona inquiry', () => {});
      then('My Paradise sends the inquiry request to Persona with the Customer email', () => {}).and('My Paradise retrieves the Persona document', () => {});
      when('Persona returns ++Persona inquiry++ ++completed Persona inquiry++', () => {});
      then('the Customer has a verified ++Persona inquiry++', () => {}).and('My Paradise maps the inquiry onto ++identity++ ++valid identity++ and ++address++ ++valid address++', () => {}).and('Customer verified stays false until the Customer confirms their identity', () => {});
      when('Persona returns ++Persona document++ ++valid Persona document++', () => {});
      then('++identity++ expiry date is the ++Persona document++ expiration date', () => {});
    });
    scenario('Persona inquiry not completed', ({ given, when, then }) => {
      when('the Customer creates a Persona inquiry', () => {});
      then('My Paradise sends the inquiry request to Persona with the Customer email', () => {});
      when('Persona returns ++Persona inquiry++ ++failed Persona inquiry++', () => {});
      then('the Customer has an unverified ++Persona inquiry++', () => {}).and('++identity++ and ++address++ stay empty', () => {});
    });
    scenario('No government ID document on inquiry', ({ given, when, then }) => {
      given('the completed ++Persona inquiry++ has no government ID document', () => {});
      when('the Customer creates a Persona inquiry', () => {});
      then('My Paradise sends the inquiry request to Persona', () => {}).and('My Paradise does not retrieve a Persona document', () => {});
      when('Persona returns the completed inquiry without a government ID', () => {});
      then('++identity++ expiry date is empty', () => {});
    });
    scenario('Persona errors on inquiry load', ({ given, when, then }) => {
      when('the Customer creates a Persona inquiry', () => {});
      then('My Paradise sends the inquiry request to Persona', () => {});
      when('Persona returns an error', () => {});
      then('the Customer has an unverified ++Persona inquiry++', () => {}).and('++identity++ stays empty', () => {});
    });
    scenario('Document not found', ({ given, when, then }) => {
      given('Persona has no ++Persona document++ for that document ID', () => {});
      when('the Customer creates a Persona inquiry', () => {});
      then('My Paradise retrieves the Persona document', () => {});
      when('Persona returns that the document is not found', () => {});
      then('++identity++ expiry date is empty', () => {});
    });
    scenario('Document email mismatch', ({ given, when, then }) => {
      given('the ++Persona document++ email does not match the Customer email', () => {});
      when('the Customer creates a Persona inquiry', () => {});
      then('My Paradise retrieves the Persona document', () => {});
      when('Persona returns unauthorized', () => {});
      then('++identity++ expiry date is empty', () => {});
    });
    scenario('Verify later', ({ given, when, then }) => {
      given('the Customer has a ++My Paradise customer++ with no idNumber on ++identity++', () => {});
      when('the Customer proceeds without a Persona inquiry', () => {});
      then('My Paradise does not send an inquiry request to Persona', () => {}).and('no ++Persona inquiry++ is stored', () => {}).and('the Customer is still on the Profile KYC step', () => {});
    });
    scenario('Enter valid identity and address', ({ given, when, then }) => {
      given('the Customer has a ++My Paradise customer++ in session', () => {});
      when('the Customer enters ++identity++ ++valid identity++ and ++address++ ++valid address++', () => {});
      then('all profile requirements are met', () => {}).and('the Customer can confirm their identity', () => {});
    });
    scenario('Enter identity after a verified Persona inquiry', ({ given, when, then }) => {
      given('the Customer has a verified ++Persona inquiry++ mapped onto ++identity++ ++valid identity++', () => {});
      when('the Customer enters the mapped ++identity++ and ++address++', () => {});
      then('all profile requirements are met', () => {}).and('the ID fields are present on ++identity++', () => {});
    });
    scenario('Re-enter a verified identity', ({ given, when, then }) => {
      given('the Customer has ++identity++ ++valid identity++ already verified', () => {});
      when('the Customer re-enters ++identity++ ++valid identity++', () => {});
      then('the identity is no longer verified', () => {}).and('the Customer can confirm their identity again', () => {});
    });
    scenario('Enter incomplete identity or address', ({ given, when, then }) => {
      when('the Customer enters ++identity++ and ++address++ with {field} empty', () => {});
      then('{field} is missing', () => {}).and('the Customer cannot confirm their identity', () => {});
    });
    scenario('Confirm identity with a verified Persona inquiry', ({ given, when, then }) => {
      given('the Customer has entered ++identity++ ++valid identity++ and ++address++ ++valid address++', () => {}).and('the Customer has a verified ++Persona inquiry++', () => {});
      when('the Customer confirms their identity', () => {});
      then('My Paradise maps ++identity++ and ++address++ onto the Mavenir engaged party and contact medium', () => {}).and('My Paradise sends the profile patch to Mavenir', () => {});
      when('Mavenir patches the customer', () => {});
      then('the Customer identity is persisted', () => {}).and('the Customer is verified', () => {}).and('the ++Persona inquiry++ is cleared', () => {});
    });
    scenario('Profile requirements unmet', ({ given, when, then }) => {
      given('the Customer has not entered ++identity++ or ++address++', () => {});
      when('the Customer confirms their identity', () => {});
      then('the identity cannot be confirmed', () => {}).and('My Paradise does not send a profile patch to Mavenir', () => {});
    });
    scenario('Customer already exists', ({ given, when, then }) => {
      given('another Mavenir customer already has ++identity++ idNumber I1234562', () => {});
      when('the Customer confirms their identity', () => {});
      then('My Paradise sends the profile patch to Mavenir', () => {}).and('the identity cannot be confirmed because a customer with that information already exists', () => {});
    });
    scenario('Mavenir profile patch error', ({ given, when, then }) => {
      given('Mavenir returns a profile patch error', () => {});
      when('the Customer confirms their identity', () => {});
      then('My Paradise sends the profile patch to Mavenir', () => {}).and('the identity cannot be confirmed', () => {});
    });
  });
});

/**
 * Story: Collect Identity With Brand Amassador
 * Actor: Ambassador
 */

story('Collect Identity With Brand Amassador', () => {
  background('each', ({ given }) => {
    scenario('Collect identity with Brand Ambassador', ({ given, when, then }) => {
      given('the Customer is choosing how to verify their ID', () => {});
      when('the Customer asks a Brand Ambassador to verify their ID', () => {});
      then('the Ambassador will be in touch to proceed with verification', () => {}).and('the Ambassador collects the Customer\'s ++identity++ documents over WhatsApp', () => {}).and('the Customer proceeds to enter identity in My Paradise', () => {});
    });
  });
});
