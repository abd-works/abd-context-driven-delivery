/**
 * Epic: Verify Ported Number
 */

import { background, scenario, story } from "../../story-test.js";

/**
 * Story: Check Port Verification
 */

story('Check Port Verification', () => {
  background('each', ({ given }) => {
    scenario('Enter porting SMS code', ({ given, when, then }) => {
      given('the Customer submitted portability and Twilio sent an SMS to the port number', () => {}).and('Twilio is ready to confirm the SMS code as valid', () => {});
      then('My Paradise sends the verification check to Twilio with the port number and code', () => {});
      when('Twilio creates a verification check (verificationChecks.create)', () => {});
      then('Twilio returns approved and the Customer is forwarded to Select Sim', () => {});
    });
    scenario('Verify with unusable porting SMS code', ({ given, when, then }) => {
      given('the Customer submitted portability and has an incorrect verification code', () => {});
      then('My Paradise sends the verification check to Twilio', () => {});
      when('Twilio creates a verification check and returns a non-approved status', () => {});
      then('the verification is rejected', () => {});
    });
    scenario('Resend porting SMS code', ({ given, when, then }) => {
      given('the Customer submitted portability and Twilio sent an SMS to the port number', () => {});
      when('the Customer requests a new verification code', () => {});
      then('My Paradise SMSes a porting verification code via Twilio', () => {});
      when('Twilio sends the SMS verification', () => {});
      then('the resend is confirmed', () => {});
    });
  });
});
