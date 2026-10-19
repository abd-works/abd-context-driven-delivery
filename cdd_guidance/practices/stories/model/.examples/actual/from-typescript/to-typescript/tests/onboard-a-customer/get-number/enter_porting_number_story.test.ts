/**
 * Epic: Enter Porting Number
 * Orders: 0.0.1.0
 */

import { scenario, story } from "tests/story-test";
import { storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart } from "./examples";


/**
 * Story: Submit Portability Request
 */

story('Submit Portability Request', () => {
  scenario('Port the number', ({ given, when, then }) => {
    // examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart
    given('a My Paradise customer with a Mavenir shopping cart', () => {
      // TODO: implement step
    });
    when('the Customer enters valid portability and ports their number', () => {
      // TODO: implement step
    })
      .and('Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number', () => {
        // TODO: implement step
      });
    then('the Customer is forwarded to Verify Ported Number', () => {
      // TODO: implement step
    });
  });

  scenario('Port the number — SMS verification skipped', ({ given, when, then }) => {
    // examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle
    given('a My Paradise customer with a Mavenir shopping cart', () => {
      // TODO: implement step
    })
      .and('Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send', () => {
        // TODO: implement step
      });
    when('the Customer enters valid portability and ports their number', () => {
      // TODO: implement step
    });
    when('Mavenir processes the portability request and Twilio rate-limits the SMS send', () => {
      // TODO: implement step
    });
    then('portability is stored on the line with verification skipped', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Select Sim — no verification step required', () => {
        // TODO: implement step
      });
  });

});
