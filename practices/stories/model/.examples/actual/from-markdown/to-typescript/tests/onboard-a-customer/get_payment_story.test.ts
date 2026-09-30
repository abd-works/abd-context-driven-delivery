/**
 * Epic: Get Payment
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Enter Payment
 * Actor: Customer
 */

story('Enter Payment', () => {
  scenario('Enter Payment', ({ given, when, then }) => {
    given('payUpFront is off', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS authorizes ++payment authorization++ ++stub auth++', () => {
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {
      // TODO: implement step
    });
    when('Mavenir authorizes the card and returns the hosted payment page', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    });
  });

  scenario('Pay upfront', ({ given, when, then }) => {
    given('payUpFront is on', () => {
      // TODO: implement step
    })
      .and('the cart has ++plan++ ++Essentials++', () => {
        // TODO: implement step
      })
      .and('Mavenir CCS authorizes ++payment authorization++ ++stub auth++', () => {
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {
      // TODO: implement step
    });
    when('Mavenir authorizes the card and returns the hosted payment page', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    });
  });

  scenario('Payment authorization fails to load', ({ given, when, then }) => {
    given('payUpFront is off', () => {
      // TODO: implement step
    })
      .but('Mavenir CCS does not return a payment authorization', () => {
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir does not return a payment authorization', () => {
      // TODO: implement step
    });
    then('the payment authorization cannot be loaded', () => {
      // TODO: implement step
    });
  });

  scenario('FAC authorization timeout', ({ given, when, then }) => {
    given('payUpFront is off', () => {
      // TODO: implement step
    })
      .but('Mavenir does not return a transaction id', () => {
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir does not return a transaction id', () => {
      // TODO: implement step
    });
    then('the payment authorization cannot be loaded', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Evaluate Payment Flags
 */

story('Evaluate Payment Flags', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Authorize Card
 * Actor: My Paradise
 */

story('Authorize Card', () => {
  scenario('Payment completed', ({ given, when, then }) => {
    given('the Customer has ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS has ++payment status++ ++completed auth++', () => {
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    });
    when('Mavenir returns ++payment status++ ++completed auth++', () => {
      // TODO: implement step
    });
    then('the payment is authorized', () => {
      // TODO: implement step
    })
      .and('the payment step does not place the order', () => {
        // TODO: implement step
      });
  });

  scenario('Card not verified', ({ given, when, then }) => {
    given('the Customer has ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS has ++payment status++ ++failed auth++', () => {
        // TODO: implement step
      })
      .and('payment attempts are under the maximum', () => {
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir returns ++payment status++ ++failed auth++', () => {
      // TODO: implement step
    });
    then('the card is not verified', () => {
      // TODO: implement step
    })
      .and('My Paradise requests a fresh payment authorization from Mavenir', () => {
        // TODO: implement step
      });
  });

  scenario('Maximum payment attempts', ({ given, when, then }) => {
    given('the Customer has ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS has ++payment status++ ++failed auth++', () => {
        // TODO: implement step
      })
      .and('payment attempts equal the maximum', () => {
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++', () => {
      // TODO: implement step
    });
    when('Mavenir returns ++payment status++ ++failed auth++', () => {
      // TODO: implement step
    });
    then('My Paradise records the failed card addition with Zendesk', () => {
      // TODO: implement step
    })
      .and('the payment step does not place the order', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Provide Apple Pay Certificate
 * Actor: My Paradise
 */

story('Provide Apple Pay Certificate', () => {
  scenario('Provide Apple Pay certificate', ({ given, when, then }) => {
    given('the Apple Pay merchant certificate is available', () => {
      // TODO: implement step
    });
    when('My Paradise provides the Apple Pay certificate', () => {
      // TODO: implement step
    });
    then('My Paradise sends the certificate request to Apple', () => {
      // TODO: implement step
    });
    when('Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++', () => {
      // TODO: implement step
    });
    then('My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Adjust Credit Manually
 * Actor: Care
 */

story('Adjust Credit Manually', () => {
  scenario('Adjust credit for pay-upfront or voucher', ({ given, when, then }) => {
    given('the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++', () => {
      // TODO: implement step
    })
      .and('the ++Mavenir customer++ has completed onboarding in My Paradise', () => {
        // TODO: implement step
      })
      .but('the credit adjustment was not applied after checkout', () => {
        // TODO: implement step
      });
    when('the Care agent manually adjusts the credit amount in Mavenir DEP', () => {
      // TODO: implement step
    });
    then('the ++Mavenir customer++ billing account is credited the adjustment amount', () => {
      // TODO: implement step
    });
  });

});
