/**
 * Epic: Enter Porting Number
 * Orders: 0.0.1.0
 */

import { background, scenario, story } from "../../story-test.js";
import { storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart } from "./examples";


/**
 * Story: Submit Portability Request
 */

story('Submit Portability Request', () => {
    scenario('Port the number', ({ given, when, then }) => {
      // examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart
      given('a My Paradise customer with a Mavenir shopping cart', () => {});
      when('the Customer enters valid portability and ports their number', () => {}).and('Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number', () => {});
      then('the Customer is forwarded to Verify Ported Number', () => {});
    });
    scenario('Port the number — SMS verification skipped', ({ given, when, then }) => {
      // examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle
      given('a My Paradise customer with a Mavenir shopping cart', () => {}).and('Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send', () => {});
      when('the Customer enters valid portability and ports their number', () => {});
      when('Mavenir processes the portability request and Twilio rate-limits the SMS send', () => {});
      then('portability is stored on the line with verification skipped', () => {}).and('the Customer is forwarded to Select Sim — no verification step required', () => {});
    });
});
