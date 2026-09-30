/**
 * Epic: Verify Ported Number
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Check Port Verification
 */

story('Check Port Verification', () => {
  scenario('Enter porting SMS code', ({ given, when, then }) => {
    given('the Customer submitted portability and Twilio sent an SMS to the port number', () => {
      // TODO: implement step
    })
      .and('Twilio is ready to confirm the SMS code as valid', () => {
        // TODO: implement step
      });
    then('My Paradise sends the verification check to Twilio with the port number and code', () => {
      // TODO: implement step
    });
    when('Twilio creates a verification check (verificationChecks.create)', () => {
      // TODO: implement step
    });
    then('Twilio returns approved and the Customer is forwarded to Select Sim', () => {
      // TODO: implement step
    });
  });

  scenario('Verify with unusable porting SMS code', ({ given, when, then }) => {
    given('the Customer submitted portability and has an incorrect verification code', () => {
      // TODO: implement step
    });
    then('My Paradise sends the verification check to Twilio', () => {
      // TODO: implement step
    });
    when('Twilio creates a verification check and returns a non-approved status', () => {
      // TODO: implement step
    });
    then('the verification is rejected', () => {
      // TODO: implement step
    });
  });

  scenario('Resend porting SMS code', ({ given, when, then }) => {
    given('the Customer submitted portability and Twilio sent an SMS to the port number', () => {
      // TODO: implement step
    });
    when('the Customer requests a new verification code', () => {
      // TODO: implement step
    });
    then('My Paradise SMSes a porting verification code via Twilio', () => {
      // TODO: implement step
    });
    when('Twilio sends the SMS verification', () => {
      // TODO: implement step
    });
    then('the resend is confirmed', () => {
      // TODO: implement step
    });
  });

});
