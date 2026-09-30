/**
 * Epic: Get Payment
 * Orders: 0.0.4
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Enter Payment
 */

story('Enter Payment', () => {
  scenario('Enter Payment', ({ given, when, then }) => {
    given('the Customer is at Checkout with Essentials', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS authorizes stub auth', () => {
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
    then('the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING', () => {
      // TODO: implement step
    });
  });

  scenario('Payment authorization fails to load', ({ given, when, then }) => {
    given('the Customer is at Checkout with Essentials', () => {
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
    given('the Customer is at Checkout with Essentials', () => {
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
 * Story: Authorize Card
 */

story('Authorize Card', () => {
  scenario('Payment completed', ({ given, when, then }) => {
    given('the Customer has stub auth', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS has completed auth', () => {
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {
      // TODO: implement step
    });
    when('Mavenir returns completed auth', () => {
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
    given('the Customer has stub auth', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS has failed auth', () => {
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
    when('Mavenir returns failed auth', () => {
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
    given('the Customer has stub auth', () => {
      // TODO: implement step
    })
      .and('Mavenir CCS has failed auth', () => {
        // TODO: implement step
      })
      .and('payment attempts equal the maximum', () => {
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {
      // TODO: implement step
    });
    when('Mavenir returns failed auth', () => {
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
    when('Apple returns Bermuda Apple Pay cert', () => {
      // TODO: implement step
    });
    then('My Paradise returns Bermuda Apple Pay cert', () => {
      // TODO: implement step
    });
  });

});
