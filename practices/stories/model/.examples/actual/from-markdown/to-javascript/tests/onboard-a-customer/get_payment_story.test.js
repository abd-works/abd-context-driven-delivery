/**
 * Epic: Get Payment
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Enter Payment
 * Actor: Customer
 */

story('Enter Payment', () => {
  background('each', ({ given }) => {
    scenario('Enter Payment', ({ given, when, then }) => {
      given('payUpFront is off', () => {}).and('Mavenir CCS authorizes ++payment authorization++ ++stub auth++', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {});
      when('Mavenir authorizes the card and returns the hosted payment page', () => {});
      then('My Paradise stores ++payment authorization++ ++stub auth++', () => {});
    });
    scenario('Pay upfront', ({ given, when, then }) => {
      given('payUpFront is on', () => {}).and('the cart has ++plan++ ++Essentials++', () => {}).and('Mavenir CCS authorizes ++payment authorization++ ++stub auth++', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {});
      when('Mavenir authorizes the card and returns the hosted payment page', () => {});
      then('My Paradise stores ++payment authorization++ ++stub auth++', () => {});
    });
    scenario('Payment authorization fails to load', ({ given, when, then }) => {
      given('payUpFront is off', () => {}).but('Mavenir CCS does not return a payment authorization', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir', () => {});
      when('Mavenir does not return a payment authorization', () => {});
      then('the payment authorization cannot be loaded', () => {});
    });
    scenario('FAC authorization timeout', ({ given, when, then }) => {
      given('payUpFront is off', () => {}).but('Mavenir does not return a transaction id', () => {});
      when('the Customer proceeds to adding their payment', () => {});
      then('My Paradise sends the card authorization request to Mavenir', () => {});
      when('Mavenir does not return a transaction id', () => {});
      then('the payment authorization cannot be loaded', () => {});
    });
  });
});

/**
 * Story: Authorize Card
 * Actor: My Paradise
 */

story('Authorize Card', () => {
  background('each', ({ given }) => {
    scenario('Payment completed', ({ given, when, then }) => {
      given('the Customer has ++payment authorization++ ++stub auth++', () => {}).and('Mavenir CCS has ++payment status++ ++completed auth++', () => {});
      when('the Customer authorizes their card', () => {});
      then('My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++', () => {});
      when('Mavenir returns ++payment status++ ++completed auth++', () => {});
      then('the payment is authorized', () => {}).and('the payment step does not place the order', () => {});
    });
    scenario('Card not verified', ({ given, when, then }) => {
      given('the Customer has ++payment authorization++ ++stub auth++', () => {}).and('Mavenir CCS has ++payment status++ ++failed auth++', () => {}).and('payment attempts are under the maximum', () => {});
      when('the Customer authorizes their card', () => {});
      then('My Paradise sends the tokenized card request to Mavenir', () => {});
      when('Mavenir returns ++payment status++ ++failed auth++', () => {});
      then('the card is not verified', () => {}).and('My Paradise requests a fresh payment authorization from Mavenir', () => {});
    });
    scenario('Maximum payment attempts', ({ given, when, then }) => {
      given('the Customer has ++payment authorization++ ++stub auth++', () => {}).and('Mavenir CCS has ++payment status++ ++failed auth++', () => {}).and('payment attempts equal the maximum', () => {});
      when('the Customer authorizes their card', () => {});
      then('My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++', () => {});
      when('Mavenir returns ++payment status++ ++failed auth++', () => {});
      then('My Paradise records the failed card addition with Zendesk', () => {}).and('the payment step does not place the order', () => {});
    });
  });
});

/**
 * Story: Provide Apple Pay Certificate
 * Actor: My Paradise
 */

story('Provide Apple Pay Certificate', () => {
  background('each', ({ given }) => {
    scenario('Provide Apple Pay certificate', ({ given, when, then }) => {
      given('the Apple Pay merchant certificate is available', () => {});
      when('My Paradise provides the Apple Pay certificate', () => {});
      then('My Paradise sends the certificate request to Apple', () => {});
      when('Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++', () => {});
      then('My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++', () => {});
    });
  });
});

/**
 * Story: Adjust Credit Manually
 * Actor: Care
 */

story('Adjust Credit Manually', () => {
  background('each', ({ given }) => {
    scenario('Adjust credit for pay-upfront or voucher', ({ given, when, then }) => {
      given('the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++', () => {}).and('the ++Mavenir customer++ has completed onboarding in My Paradise', () => {}).but('the credit adjustment was not applied after checkout', () => {});
      when('the Care agent manually adjusts the credit amount in Mavenir DEP', () => {});
      then('the ++Mavenir customer++ billing account is credited the adjustment amount', () => {});
    });
  });
});
