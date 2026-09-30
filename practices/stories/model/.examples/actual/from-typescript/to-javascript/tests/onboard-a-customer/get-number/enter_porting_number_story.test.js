/**
 * Epic: Enter Porting Number
 */

import { background, scenario, story } from "../../story-test.js";

/**
 * Story: Submit Portability Request
 */

story('Submit Portability Request', () => {
  background('each', ({ given }) => {
    scenario('Port the number', ({ given, when, then }) => {
      given('a My Paradise customer with a Mavenir shopping cart', () => {});
      when('the Customer enters valid portability and ports their number', () => {}).and('Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number', () => {});
      then('the Customer is forwarded to Verify Ported Number', () => {});
    });
    scenario('Port the number — SMS verification skipped', ({ given, when, then }) => {
      given('a My Paradise customer with a Mavenir shopping cart', () => {}).and('Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send', () => {});
      when('the Customer enters valid portability and ports their number', () => {}).and('Mavenir processes the portability request and Twilio rate-limits the SMS send', () => {});
      then('portability is stored on the line with verification skipped', () => {}).and('the Customer is forwarded to Select Sim — no verification step required', () => {});
    });
  });
});
