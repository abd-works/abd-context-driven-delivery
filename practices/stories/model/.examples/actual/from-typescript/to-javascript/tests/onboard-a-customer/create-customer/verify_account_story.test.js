/**
 * Epic: Verify Account
 */

import { background, scenario, story } from "../../story-test.js";

/**
 * Story: Enter Validation Code
 */

story('Enter Validation Code', () => {
  background('each', ({ given }) => {
    given('the User has submitted valid account credentials', () => {});
    scenario('Enter validation code', ({ given, when, then }) => {
      when('the User activates the account with the emailed validation code', () => {});
      then('My Paradise sends the correct confirmation request to Cognito', () => {}).and('the account is verified', () => {}).and('Cognito issues an account token for the browser session', () => {}).but('no Mavenir customer exists for those account credentials', () => {});
    });
    scenario('Resend validation code', ({ given, when, then }) => {
      when('more than 60 seconds has passed', () => {}).and('the User resends the validation code', () => {});
      then('Cognito sends a new validation code', () => {}).and('My Paradise shows the resend confirmation', () => {});
      when('less than 60 seconds has passed', () => {}).and('the User resends the validation code', () => {});
      then('Resend waits 60 seconds before it can be used again', () => {}).and('Cognito does not send another validation code during the wait', () => {});
      when('more than 60 seconds has passed', () => {}).and('the User resends the validation code', () => {});
      then('Cognito sends another validation code', () => {});
    });
  });
});
