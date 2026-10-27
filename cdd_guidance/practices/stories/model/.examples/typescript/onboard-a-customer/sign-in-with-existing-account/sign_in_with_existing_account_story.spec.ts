import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import {
  AccountCredentials,
  accountRepository,
} from '../../../domain/customer/Customer';
import {
  amplifyService,
  SignInFailure,
  SignInStep,
} from '../../../domain/systems/amplify';
import { AccountToken } from '../../../domain/systems/Cognito/Cognito';
import {
  enteredAlreadyRegisteredAccountCredentials,
  incorrectCredentialOutlines,
  enteredInvalidEmailFormat,
  enteredValidAccountCredentials,
} from '../examples/account-credentials.examples';
import { storedUnconfirmedCognitoUser } from '../create-customer/examples/cognito-user.examples';
import { storedAlreadyRegisteredCognitoUser } from './examples/cognito-user.examples';

afterEach(() => {
  amplifyService.reset();
  vi.restoreAllMocks();
});

function namedError(name: string): Error {
  const error = new Error(name);
  error.name = name;
  return error;
}

story('Sign In With Existing Account', () => {
  let signInSpy: MockInstance<typeof amplifyService.signIn>;

  beforeEach(() => {
    signInSpy = vi.spyOn(amplifyService, 'signIn');
  });

  scenario('Sign in with already-registered account credentials', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;

    given('Cognito has an already-registered Cognito user', () => {
      amplifyService.seedCognitoUser(
        storedAlreadyRegisteredCognitoUser,
        enteredAlreadyRegisteredAccountCredentials.password,
      );
    }).and('the Customer is not signed in', async () => {
      await amplifyService.signOut();
    }).and('the Customer has already-registered account credentials', () => {
      accountCredentials = accountRepository.newAccount(
        new AccountCredentials(
          storedAlreadyRegisteredCognitoUser,
          enteredAlreadyRegisteredAccountCredentials.password,
        ),
      );
    });
    when('the Customer authenticates already-registered account credentials', async () => {
      await accountCredentials.authenticateAccount();
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      expect(signInSpy).toHaveBeenCalledWith({
        username: enteredAlreadyRegisteredAccountCredentials.email,
        password: enteredAlreadyRegisteredAccountCredentials.password,
      });
    });
    when('Cognito authenticates the account and issues an account token', () => {});
    then('My Paradise stores the signed-in Cognito user', () => {
      expect(accountCredentials.token).toBeInstanceOf(AccountToken);
      expect(accountCredentials.token).toMatchObject({
        email: enteredAlreadyRegisteredAccountCredentials.email,
        customerId: storedAlreadyRegisteredCognitoUser.customerId,
      });
    }).and('the Cognito user has the Mavenir customer id', () => {
      expect(accountCredentials.customerId).toBe(storedAlreadyRegisteredCognitoUser.customerId);
    });
  });

  scenario('Email format is unmet', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('the Customer has invalid email format account credentials', () => {
      accountCredentials = accountRepository.newAccount(enteredInvalidEmailFormat);
    });
    when('the Customer authenticates invalid email format', async () => {
      try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
    });
    then('My Paradise does not send a sign-in request to Cognito', () => {
      expect(signInSpy).not.toHaveBeenCalled();
    }).and('the authentication is rejected', () => {
      expect(caughtError).toHaveProperty('signIn', 'Account credential requirements are unmet');
    }).and('Cognito does not issue an account token', () => {
      expect(accountCredentials.token).toBeNull();
    });
  });

  incorrectCredentialOutlines.forEach(({ example, credentials }) => {
    scenario(`Authenticate with incorrect account credentials: ${example}`, ({ given, when, then }) => {
      let accountCredentials: AccountCredentials;
      let caughtError: unknown;

      given('Cognito has an already-registered Cognito user', () => {
        amplifyService.seedCognitoUser(
          storedAlreadyRegisteredCognitoUser,
          enteredAlreadyRegisteredAccountCredentials.password,
        );
      }).and('the Customer is not signed in', async () => {
        await amplifyService.signOut();
      }).and(`the Customer has ${example}`, () => {
        accountCredentials = accountRepository.newAccount(credentials);
      });
      when(`the Customer authenticates ${example}`, async () => {
        try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
      });
      then('My Paradise sends the sign-in request to Cognito', () => {
        expect(signInSpy).toHaveBeenCalledWith({
          username: credentials.email,
          password: credentials.password,
        });
      });
      when('Cognito returns NotAuthorizedException', () => {});
      then('the authentication is rejected', () => {
        expect(caughtError).toHaveProperty('signIn', SignInFailure.NotAuthorized);
      }).and('Cognito does not issue an account token', () => {
        expect(accountCredentials.token).toBeNull();
      });
    });
  });

  scenario('Authenticate with unconfirmed account', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('Cognito has an unconfirmed Cognito user', () => {
      amplifyService.seedCognitoUser(
        storedUnconfirmedCognitoUser,
        enteredValidAccountCredentials.password,
      );
    }).and('the Customer is not signed in', async () => {
      await amplifyService.signOut();
    }).and('the Customer has unconfirmed sign-in account credentials', () => {
      accountCredentials = accountRepository.newAccount(
        new AccountCredentials(storedUnconfirmedCognitoUser, enteredValidAccountCredentials.password),
      );
    });
    when('the Customer authenticates unconfirmed sign-in', async () => {
      try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      expect(signInSpy).toHaveBeenCalledWith({
        username: enteredValidAccountCredentials.email,
        password: enteredValidAccountCredentials.password,
      });
    });
    when('Cognito returns CONFIRM_SIGN_UP', () => {});
    then('the authentication is rejected as unconfirmed', () => {
      expect(caughtError).toHaveProperty('signIn', SignInStep.ConfirmSignUp);
    }).and('Cognito does not issue an account token', () => {
      expect(accountCredentials.token).toBeNull();
    });
  });

  scenario('Password reset required', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('Cognito has an already-registered Cognito user', () => {
      amplifyService.seedCognitoUser(
        storedAlreadyRegisteredCognitoUser,
        enteredAlreadyRegisteredAccountCredentials.password,
      );
    }).and('Cognito requires a password reset for already-registered account credentials', () => {
      amplifyService.seedSignInError(
        enteredAlreadyRegisteredAccountCredentials.email,
        namedError(SignInFailure.PasswordResetRequired),
      );
    }).and('the Customer is not signed in', async () => {
      await amplifyService.signOut();
    }).and('the Customer has already-registered account credentials', () => {
      accountCredentials = accountRepository.newAccount(
        new AccountCredentials(
          storedAlreadyRegisteredCognitoUser,
          enteredAlreadyRegisteredAccountCredentials.password,
        ),
      );
    });
    when('the Customer authenticates already-registered account credentials', async () => {
      try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      expect(signInSpy).toHaveBeenCalledWith({
        username: enteredAlreadyRegisteredAccountCredentials.email,
        password: enteredAlreadyRegisteredAccountCredentials.password,
      });
    });
    when('Cognito returns PasswordResetRequiredException', () => {});
    then('the authentication requires a password reset', () => {
      expect(caughtError).toHaveProperty('signIn', SignInFailure.PasswordResetRequired);
    }).and('Cognito does not issue an account token', () => {
      expect(accountCredentials.token).toBeNull();
    });
  });

  scenario('New password required', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('Cognito has an already-registered Cognito user', () => {
      amplifyService.seedCognitoUser(
        storedAlreadyRegisteredCognitoUser,
        enteredAlreadyRegisteredAccountCredentials.password,
      );
    }).and('Cognito requires a new password for already-registered account credentials', () => {
      amplifyService.seedSignInNextStep(
        enteredAlreadyRegisteredAccountCredentials.email,
        SignInStep.NewPasswordRequired,
      );
    }).and('the Customer is not signed in', async () => {
      await amplifyService.signOut();
    }).and('the Customer has already-registered account credentials', () => {
      accountCredentials = accountRepository.newAccount(
        new AccountCredentials(
          storedAlreadyRegisteredCognitoUser,
          enteredAlreadyRegisteredAccountCredentials.password,
        ),
      );
    });
    when('the Customer authenticates already-registered account credentials', async () => {
      try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      expect(signInSpy).toHaveBeenCalledWith({
        username: enteredAlreadyRegisteredAccountCredentials.email,
        password: enteredAlreadyRegisteredAccountCredentials.password,
      });
    });
    when('Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED', () => {});
    then('the authentication requires a new password', () => {
      expect(caughtError).toHaveProperty('signIn', SignInStep.NewPasswordRequired);
    }).and('Cognito does not issue an account token', () => {
      expect(accountCredentials.token).toBeNull();
    });
  });
});
