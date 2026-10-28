/**
 * Epic: Verify Account
 * Orders: 0.0.0.3
 */

import { scenario, story } from "tests/story-test";
import { enteredValidAccountCredentials } from "./examples";


/**
 * Story: Enter Validation Code
 */

story('Enter Validation Code', () => {
  background('each', ({ given }) => {
    given('the User has submitted valid account credentials', () => {
      // TODO: implement step
    })
      .and('Cognito has an unconfirmed Cognito user', () => {
        // TODO: implement step
      })
      .and('Cognito has sent a validation code to the User', () => {
        // TODO: implement step
      })
      .and('the User has account credentials with valid email and password', () => {
        // TODO: implement step
      });
  });

  scenario('Enter validation code', ({ given, when, then }) => {
    // examples: enteredValidAccountCredentials
    when('the User activates the account with the emailed validation code', () => {
      // TODO: implement step
    });
    then('My Paradise sends the correct confirmation request to Cognito', () => {
      // TODO: implement step
    })
      .and('the account is verified', () => {
        // TODO: implement step
      })
      .and('Cognito issues an account token for the browser session', () => {
        // TODO: implement step
      })
      .but('no Mavenir customer exists for those account credentials', () => {
        // TODO: implement step
      });
  });

  scenario('Resend validation code', ({ given, when, then }) => {
    when('more than 60 seconds has passed', () => {
      // TODO: implement step
    })
      .and('the User resends the validation code', () => {
        // TODO: implement step
      });
    then('Cognito sends a new validation code', () => {
      // TODO: implement step
    })
      .and('My Paradise shows the resend confirmation', () => {
        // TODO: implement step
      });
    when('less than 60 seconds has passed', () => {
      // TODO: implement step
    })
      .and('the User resends the validation code', () => {
        // TODO: implement step
      });
    then('Resend waits 60 seconds before it can be used again', () => {
      // TODO: implement step
    })
      .and('Cognito does not send another validation code during the wait', () => {
        // TODO: implement step
      });
    when('more than 60 seconds has passed', () => {
      // TODO: implement step
    })
      .and('the User resends the validation code', () => {
        // TODO: implement step
      });
    then('Cognito sends another validation code', () => {
      // TODO: implement step
    });
  });

});
