/**
 * Epic: Create Unconfirmed User
 * Orders: 0.0.0.1
 */

import { background, scenario, story } from "../../story-test.js";
import { enteredValidAccountCredentials, enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser, expectedValidAccountCredentials } from "./examples";


/**
 * Story: Create Unconfirmed Cognito User
 */

story('Create Unconfirmed Cognito User', () => {
    scenario('Display Create Account', ({ given, when, then }) => {
      when('the User proceeds to create an account from the Paradise Mobile website', () => {});
      then('the User can enter account credentials', () => {}).and('the email and password rules are unmet', () => {}).and('the customer cannot save the customer account', () => {});
    });
    scenario('Enter Valid account credentials', ({ given, when, then }) => {
      // examples: enteredValidAccountCredentials
      when('the User enters valid account credentials', () => {});
      then('account credentials are validated continuously', () => {}).and('the customer can save the customer account', () => {});
    });
    scenario('Email already registered', ({ given, when, then }) => {
      // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
      given('already-registered account credentials are already registered', () => {});
      when('the User registers already-registered account credentials', () => {});
      then('Email shows the already-registered error', () => {});
    });
    scenario('Create Unconfirmed User', ({ given, when, then }) => {
      // examples: enteredValidAccountCredentials, expectedValidAccountCredentials
      given('the amplifyService.signUp spy is set up', () => {});
      when('the User creates their account', () => {});
      then('the system creates an unconfirmed Cognito user and emails a validation code', () => {});
    });
    scenario('Email already registered in Cognito', ({ given, when, then }) => {
      // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
      given('an unconfirmed Cognito user exists for already-registered account credentials', () => {});
      when('Cognito is asked to register already-registered account credentials', () => {});
      then('Cognito returns UsernameExistsException', () => {}).and('Cognito does not create another Cognito user', () => {});
    });
});
