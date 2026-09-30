/**
 * Epic: Get Payment
 * Orders: 0.0.4
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Enter Payment
 */

story('Enter Payment', () => {
    scenario('Enter Payment', ({ given, when, then }) => {
      given('the Customer is at Checkout with Essentials', () => {}).and('Mavenir CCS authorizes stub auth', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {});
      when('Mavenir authorizes the card and returns the hosted payment page', () => {});
      then('the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING', () => {});
    });
    scenario('Payment authorization fails to load', ({ given, when, then }) => {
      given('the Customer is at Checkout with Essentials', () => {}).but('Mavenir CCS does not return a payment authorization', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir', () => {});
      when('Mavenir does not return a payment authorization', () => {});
      then('the payment authorization cannot be loaded', () => {});
    });
    scenario('FAC authorization timeout', ({ given, when, then }) => {
      given('the Customer is at Checkout with Essentials', () => {}).but('Mavenir does not return a transaction id', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir', () => {});
      when('Mavenir does not return a transaction id', () => {});
      then('the payment authorization cannot be loaded', () => {});
    });
});

/**
 * Story: Authorize Card
 */

story('Authorize Card', () => {
    scenario('Payment completed', ({ given, when, then }) => {
      given('the Customer has stub auth', () => {}).and('Mavenir CCS has completed auth', () => {});
      when('the Customer authorizes their card', () => {});
      then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {});
      when('Mavenir returns completed auth', () => {});
      then('the payment is authorized', () => {}).and('the payment step does not place the order', () => {});
    });
    scenario('Card not verified', ({ given, when, then }) => {
      given('the Customer has stub auth', () => {}).and('Mavenir CCS has failed auth', () => {}).and('payment attempts are under the maximum', () => {});
      when('the Customer authorizes their card', () => {});
      then('My Paradise sends the tokenized card request to Mavenir', () => {});
      when('Mavenir returns failed auth', () => {});
      then('the card is not verified', () => {}).and('My Paradise requests a fresh payment authorization from Mavenir', () => {});
    });
    scenario('Maximum payment attempts', ({ given, when, then }) => {
      given('the Customer has stub auth', () => {}).and('Mavenir CCS has failed auth', () => {}).and('payment attempts equal the maximum', () => {});
      when('the Customer authorizes their card', () => {});
      then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {});
      when('Mavenir returns failed auth', () => {});
      then('My Paradise records the failed card addition with Zendesk', () => {}).and('the payment step does not place the order', () => {});
    });
});

/**
 * Story: Provide Apple Pay Certificate
 */

story('Provide Apple Pay Certificate', () => {
    scenario('Provide Apple Pay certificate', ({ given, when, then }) => {
      given('the Apple Pay merchant certificate is available', () => {});
      when('My Paradise provides the Apple Pay certificate', () => {});
      then('My Paradise sends the certificate request to Apple', () => {});
      when('Apple returns Bermuda Apple Pay cert', () => {});
      then('My Paradise returns Bermuda Apple Pay cert', () => {});
    });
});
