/**
 * Epic: Get Verified Profile
 * Orders: 0.0.7
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Customer Complete Persona Kyc
 */

story('Customer Complete Persona Kyc', () => {
  scenario('Persona verification required', ({ given, when, then }) => {
    given('the Customer has a cart with a plan, number, and SIM and no idNumber', () => {
      // TODO: implement step
    });
    when('the Customer validates whether a Persona inquiry is required', () => {
      // TODO: implement step
    });
    then('a Persona inquiry is required', () => {
      // TODO: implement step
    })
      .and('the Customer is on the Profile KYC step', () => {
        // TODO: implement step
      });
  });

  scenario('Persona verification already complete', ({ given, when, then }) => {
    given('the Customer has identity with an idNumber', () => {
      // TODO: implement step
    });
    when('the Customer validates whether a Persona inquiry is required', () => {
      // TODO: implement step
    });
    then('the Persona inquiry is already complete', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // TODO: implement step
      });
  });

  scenario('Create a completed Persona inquiry', ({ given, when, then }) => {
    given('the Customer has no idNumber on identity', () => {
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona with the Customer email', () => {
      // TODO: implement step
    })
      .and('My Paradise retrieves the Persona document', () => {
        // TODO: implement step
      });
    when('Persona returns the completed inquiry', () => {
      // TODO: implement step
    });
    then('the Customer has a verified Persona inquiry', () => {
      // TODO: implement step
    })
      .and('My Paradise maps the inquiry onto identity and address', () => {
        // TODO: implement step
      })
      .and('Customer verified stays false until the Customer confirms their identity', () => {
        // TODO: implement step
      });
    when('Persona returns the valid Persona document', () => {
      // TODO: implement step
    });
    then('identity expiry date is the Persona document expiration date', () => {
      // TODO: implement step
    });
  });

  scenario('Persona inquiry not completed', ({ given, when, then }) => {
    given('the Customer has no idNumber on identity', () => {
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona with the Customer email', () => {
      // TODO: implement step
    });
    when('Persona returns the failed Persona inquiry', () => {
      // TODO: implement step
    });
    then('the Customer has an unverified Persona inquiry', () => {
      // TODO: implement step
    })
      .and('identity and address stay empty', () => {
        // TODO: implement step
      });
  });

  scenario('No government ID document on inquiry', ({ given, when, then }) => {
    given('the completed Persona inquiry has no government ID document', () => {
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona', () => {
      // TODO: implement step
    })
      .and('My Paradise does not retrieve a Persona document', () => {
        // TODO: implement step
      });
    when('Persona returns the completed inquiry without a government ID', () => {
      // TODO: implement step
    });
    then('identity expiry date is empty', () => {
      // TODO: implement step
    });
  });

  scenario('Persona errors on inquiry load', ({ given, when, then }) => {
    given('the Customer has no idNumber on identity', () => {
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise sends the inquiry request to Persona', () => {
      // TODO: implement step
    });
    when('Persona returns an error', () => {
      // TODO: implement step
    });
    then('the Customer has an unverified Persona inquiry', () => {
      // TODO: implement step
    })
      .and('identity stays empty', () => {
        // TODO: implement step
      });
  });

  scenario('Document not found', ({ given, when, then }) => {
    given('Persona has no Persona document for that document ID', () => {
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise retrieves the Persona document', () => {
      // TODO: implement step
    });
    when('Persona returns that the document is not found', () => {
      // TODO: implement step
    });
    then('identity expiry date is empty', () => {
      // TODO: implement step
    });
  });

  scenario('Document email mismatch', ({ given, when, then }) => {
    given('the Persona document email does not match the Customer email', () => {
      // TODO: implement step
    });
    when('the Customer creates a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise retrieves the Persona document', () => {
      // TODO: implement step
    });
    when('Persona returns unauthorized', () => {
      // TODO: implement step
    });
    then('identity expiry date is empty', () => {
      // TODO: implement step
    });
  });

  scenario('Verify later', ({ given, when, then }) => {
    given('the Customer has no idNumber on identity', () => {
      // TODO: implement step
    });
    when('the Customer proceeds without a Persona inquiry', () => {
      // TODO: implement step
    });
    then('My Paradise does not send an inquiry request to Persona', () => {
      // TODO: implement step
    })
      .and('no Persona inquiry is stored', () => {
        // TODO: implement step
      })
      .and('the Customer is still on the Profile KYC step', () => {
        // TODO: implement step
      });
  });

  scenario('Enter valid identity and address', ({ given, when, then }) => {
    given('the Customer has a My Paradise customer in session', () => {
      // TODO: implement step
    });
    when('the Customer enters valid identity and address', () => {
      // TODO: implement step
    });
    then('all profile requirements are met', () => {
      // TODO: implement step
    })
      .and('the Customer can confirm their identity', () => {
        // TODO: implement step
      });
  });

  scenario('Enter identity after a verified Persona inquiry', ({ given, when, then }) => {
    given('the Customer has a verified Persona inquiry mapped onto valid identity', () => {
      // TODO: implement step
    });
    when('the Customer enters the mapped identity and address', () => {
      // TODO: implement step
    });
    then('all profile requirements are met', () => {
      // TODO: implement step
    })
      .and('the ID fields are present on identity', () => {
        // TODO: implement step
      });
  });

  scenario('Re-enter a verified identity', ({ given, when, then }) => {
    given('the Customer has valid identity already verified', () => {
      // TODO: implement step
    });
    when('the Customer re-enters valid identity', () => {
      // TODO: implement step
    });
    then('the identity is no longer verified', () => {
      // TODO: implement step
    })
      .and('the Customer can confirm their identity again', () => {
        // TODO: implement step
      });
  });

  scenario('Confirm identity with a verified Persona inquiry', ({ given, when, then }) => {
    given('the Customer has entered valid identity and address and has a verified Persona inquiry', () => {
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // TODO: implement step
    });
    then('My Paradise maps identity and address onto the Mavenir engaged party and contact medium', () => {
      // TODO: implement step
    })
      .and('My Paradise sends the profile patch to Mavenir', () => {
        // TODO: implement step
      });
    when('Mavenir patches the customer', () => {
      // TODO: implement step
    });
    then('the Customer identity is persisted', () => {
      // TODO: implement step
    })
      .and('the Customer is verified', () => {
        // TODO: implement step
      });
  });

  scenario('Customer already exists', ({ given, when, then }) => {
    given('another Mavenir customer already has identity idNumber I1234562', () => {
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // TODO: implement step
    });
    then('My Paradise sends the profile patch to Mavenir', () => {
      // TODO: implement step
    })
      .and('the identity cannot be confirmed because a customer with that information already exists', () => {
        // TODO: implement step
      });
  });

  scenario('Profile requirements unmet', ({ given, when, then }) => {
    given('the Customer has not entered identity or address', () => {
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // TODO: implement step
    });
    then('the identity cannot be confirmed', () => {
      // TODO: implement step
    })
      .and('My Paradise does not send a profile patch to Mavenir', () => {
        // TODO: implement step
      });
  });

  scenario('Mavenir profile patch error', ({ given, when, then }) => {
    given('Mavenir returns a profile patch error', () => {
      // TODO: implement step
    });
    when('the Customer confirms their identity', () => {
      // TODO: implement step
    });
    then('My Paradise sends the profile patch to Mavenir', () => {
      // TODO: implement step
    })
      .and('the identity cannot be confirmed', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Collect Identity With Brand Amassador
 */

story('Collect Identity With Brand Amassador', () => {
  // TODO: add main-flow scenario
});
