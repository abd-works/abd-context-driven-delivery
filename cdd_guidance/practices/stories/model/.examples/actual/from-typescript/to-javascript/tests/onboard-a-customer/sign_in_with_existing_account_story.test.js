/**
 * Epic: Sign In With Existing Account
 * Orders: 0.0.10
 */

import { background, scenario, story } from "../story-test.js";
import { enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser, enteredInvalidEmailFormat, enteredValidAccountCredentials, storedUnconfirmedCognitoUser } from "./examples";


/**
 * Story: Sign In With Existing Account
 */

story('Sign In With Existing Account', () => {
    scenario('Sign in with already-registered account credentials', ({ given, when, then }) => {
      // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
      given('Cognito has an already-registered Cognito user', () => {}).and('the Customer is not signed in', () => {}).and('the Customer has already-registered account credentials', () => {});
      when('the Customer authenticates already-registered account credentials', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito authenticates the account and issues an account token', () => {});
      then('My Paradise stores the signed-in Cognito user', () => {}).and('the Cognito user has the Mavenir customer id', () => {});
    });
    scenario('Email format is unmet', ({ given, when, then }) => {
      // examples: enteredInvalidEmailFormat
      given('the Customer has invalid email format account credentials', () => {});
      when('the Customer authenticates invalid email format', () => {});
      then('My Paradise does not send a sign-in request to Cognito', () => {}).and('the authentication is rejected', () => {}).and('Cognito does not issue an account token', () => {});
    });
    scenario('Authenticate with unconfirmed account', ({ given, when, then }) => {
      // examples: enteredValidAccountCredentials, storedUnconfirmedCognitoUser
      given('Cognito has an unconfirmed Cognito user', () => {}).and('the Customer is not signed in', () => {}).and('the Customer has unconfirmed sign-in account credentials', () => {});
      when('the Customer authenticates unconfirmed sign-in', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns CONFIRM_SIGN_UP', () => {});
      then('the authentication is rejected as unconfirmed', () => {}).and('Cognito does not issue an account token', () => {});
    });
    scenario('Password reset required', ({ given, when, then }) => {
      // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
      given('Cognito has an already-registered Cognito user', () => {}).and('Cognito requires a password reset for already-registered account credentials', () => {}).and('the Customer is not signed in', () => {}).and('the Customer has already-registered account credentials', () => {});
      when('the Customer authenticates already-registered account credentials', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns PasswordResetRequiredException', () => {});
      then('the authentication requires a password reset', () => {}).and('Cognito does not issue an account token', () => {});
    });
    scenario('New password required', ({ given, when, then }) => {
      // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
      given('Cognito has an already-registered Cognito user', () => {}).and('Cognito requires a new password for already-registered account credentials', () => {}).and('the Customer is not signed in', () => {}).and('the Customer has already-registered account credentials', () => {});
      when('the Customer authenticates already-registered account credentials', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED', () => {});
      then('the authentication requires a new password', () => {}).and('Cognito does not issue an account token', () => {});
    });
});
