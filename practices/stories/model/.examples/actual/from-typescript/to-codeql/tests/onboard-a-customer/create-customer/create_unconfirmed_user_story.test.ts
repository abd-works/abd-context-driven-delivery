/**
 * Epic: Create Unconfirmed User
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Create Unconfirmed Cognito User
 */

story('Create Unconfirmed Cognito User', () => {
  scenario('Display Create Account', ({ given, when, then }) => {
    when('the User proceeds to create an account from the Paradise Mobile website', () => {
      // TODO: implement step
    });
    then('the User can enter account credentials', () => {
      // TODO: implement step
    })
      .and('the email and password rules are unmet', () => {
        // TODO: implement step
      })
      .and('the customer cannot save the customer account', () => {
        // TODO: implement step
      });
  });

  scenario('Enter Valid account credentials', ({ given, when, then }) => {
    when('the User enters valid account credentials', () => {
      // TODO: implement step
    });
    then('account credentials are validated continuously', () => {
      // TODO: implement step
    })
      .and('the customer can save the customer account', () => {
        // TODO: implement step
      });
  });

  scenario('Email already registered', ({ given, when, then }) => {
    given('already-registered account credentials are already registered', () => {
      // TODO: implement step
    });
    when('the User registers already-registered account credentials', () => {
      // TODO: implement step
    });
    then('Email shows the already-registered error', () => {
      // TODO: implement step
    });
  });

  scenario('Create Unconfirmed User', ({ given, when, then }) => {
    given('the amplifyService.signUp spy is set up', () => {
      // TODO: implement step
    });
    when('the User creates their account', () => {
      // TODO: implement step
    });
    then('the system creates an unconfirmed Cognito user and emails a validation code', () => {
      // TODO: implement step
    });
  });

  scenario('Email already registered in Cognito', ({ given, when, then }) => {
    given('an unconfirmed Cognito user exists for already-registered account credentials', () => {
      // TODO: implement step
    });
    when('Cognito is asked to register already-registered account credentials', () => {
      // TODO: implement step
    });
    then('Cognito returns UsernameExistsException', () => {
      // TODO: implement step
    })
      .and('Cognito does not create another Cognito user', () => {
        // TODO: implement step
      });
  });

});
