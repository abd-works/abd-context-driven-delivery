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
  // typescript body to translate:
  // let signInSpy: MockInstance<typeof amplifyService.signIn>;
  //
  // beforeEach(() => {
  //   signInSpy = vi.spyOn(amplifyService, 'signIn');
  // });
  //
  // incorrectCredentialOutlines.forEach(({ example, credentials }) => {
  // });
  scenario('Sign in with already-registered account credentials', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
    given('Cognito has an already-registered Cognito user', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(
      //   storedAlreadyRegisteredCognitoUser,
      //   enteredAlreadyRegisteredAccountCredentials.password,
      // );
      // TODO: implement step
    })
      .and('the Customer is not signed in', async () => {
        // typescript body to translate:
        // await amplifyService.signOut();
        // TODO: implement step
      })
      .and('the Customer has already-registered account credentials', () => {
        // typescript body to translate:
        // accountCredentials = accountRepository.newAccount(
        //   new AccountCredentials(
        //     storedAlreadyRegisteredCognitoUser,
        //     enteredAlreadyRegisteredAccountCredentials.password,
        //   ),
        // );
        // TODO: implement step
      });
    when('the Customer authenticates already-registered account credentials', async () => {
      // typescript body to translate:
      // await accountCredentials.authenticateAccount();
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // typescript body to translate:
      // expect(signInSpy).toHaveBeenCalledWith({
      //   username: enteredAlreadyRegisteredAccountCredentials.email,
      //   password: enteredAlreadyRegisteredAccountCredentials.password,
      // });
      // TODO: implement step
    });
    when('Cognito authenticates the account and issues an account token', () => {
      // TODO: implement step
    });
    then('My Paradise stores the signed-in Cognito user', () => {
      // typescript body to translate:
      // expect(accountCredentials.token).toBeInstanceOf(AccountToken);
      // expect(accountCredentials.token).toMatchObject({
      //   email: enteredAlreadyRegisteredAccountCredentials.email,
      //   customerId: storedAlreadyRegisteredCognitoUser.customerId,
      // });
      // TODO: implement step
    })
      .and('the Cognito user has the Mavenir customer id', () => {
        // typescript body to translate:
        // expect(accountCredentials.customerId).toBe(storedAlreadyRegisteredCognitoUser.customerId);
        // TODO: implement step
      });
  });

  scenario('Email format is unmet', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // let caughtError: unknown;
    // examples: enteredInvalidEmailFormat
    given('the Customer has invalid email format account credentials', () => {
      // typescript body to translate:
      // accountCredentials = accountRepository.newAccount(enteredInvalidEmailFormat);
      // TODO: implement step
    });
    when('the Customer authenticates invalid email format', async () => {
      // typescript body to translate:
      // try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('My Paradise does not send a sign-in request to Cognito', () => {
      // typescript body to translate:
      // expect(signInSpy).not.toHaveBeenCalled();
      // TODO: implement step
    })
      .and('the authentication is rejected', () => {
        // typescript body to translate:
        // expect(caughtError).toHaveProperty('signIn', 'Account credential requirements are unmet');
        // TODO: implement step
      })
      .and('Cognito does not issue an account token', () => {
        // typescript body to translate:
        // expect(accountCredentials.token).toBeNull();
        // TODO: implement step
      });
  });

  scenario('Authenticate with incorrect account credentials: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // let caughtError: unknown;
    // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
    given('Cognito has an already-registered Cognito user', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(
      //   storedAlreadyRegisteredCognitoUser,
      //   enteredAlreadyRegisteredAccountCredentials.password,
      // );
      // TODO: implement step
    })
      .and('the Customer is not signed in', async () => {
        // typescript body to translate:
        // await amplifyService.signOut();
        // TODO: implement step
      })
      .and('the Customer has ${example}', () => {
        // typescript body to translate:
        // accountCredentials = accountRepository.newAccount(credentials);
        // TODO: implement step
      });
    when('the Customer authenticates ${example}', async () => {
      // typescript body to translate:
      // try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // typescript body to translate:
      // expect(signInSpy).toHaveBeenCalledWith({
      //   username: credentials.email,
      //   password: credentials.password,
      // });
      // TODO: implement step
    });
    when('Cognito returns NotAuthorizedException', () => {
      // TODO: implement step
    });
    then('the authentication is rejected', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('signIn', SignInFailure.NotAuthorized);
      // TODO: implement step
    })
      .and('Cognito does not issue an account token', () => {
        // typescript body to translate:
        // expect(accountCredentials.token).toBeNull();
        // TODO: implement step
      });
  });

  scenario('Authenticate with unconfirmed account', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // let caughtError: unknown;
    // examples: enteredValidAccountCredentials, storedUnconfirmedCognitoUser
    given('Cognito has an unconfirmed Cognito user', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(
      //   storedUnconfirmedCognitoUser,
      //   enteredValidAccountCredentials.password,
      // );
      // TODO: implement step
    })
      .and('the Customer is not signed in', async () => {
        // typescript body to translate:
        // await amplifyService.signOut();
        // TODO: implement step
      })
      .and('the Customer has unconfirmed sign-in account credentials', () => {
        // typescript body to translate:
        // accountCredentials = accountRepository.newAccount(
        //   new AccountCredentials(storedUnconfirmedCognitoUser, enteredValidAccountCredentials.password),
        // );
        // TODO: implement step
      });
    when('the Customer authenticates unconfirmed sign-in', async () => {
      // typescript body to translate:
      // try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // typescript body to translate:
      // expect(signInSpy).toHaveBeenCalledWith({
      //   username: enteredValidAccountCredentials.email,
      //   password: enteredValidAccountCredentials.password,
      // });
      // TODO: implement step
    });
    when('Cognito returns CONFIRM_SIGN_UP', () => {
      // TODO: implement step
    });
    then('the authentication is rejected as unconfirmed', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('signIn', SignInStep.ConfirmSignUp);
      // TODO: implement step
    })
      .and('Cognito does not issue an account token', () => {
        // typescript body to translate:
        // expect(accountCredentials.token).toBeNull();
        // TODO: implement step
      });
  });

  scenario('Password reset required', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // let caughtError: unknown;
    // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
    given('Cognito has an already-registered Cognito user', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(
      //   storedAlreadyRegisteredCognitoUser,
      //   enteredAlreadyRegisteredAccountCredentials.password,
      // );
      // TODO: implement step
    })
      .and('Cognito requires a password reset for already-registered account credentials', () => {
        // typescript body to translate:
        // amplifyService.seedSignInError(
        //   enteredAlreadyRegisteredAccountCredentials.email,
        //   namedError(SignInFailure.PasswordResetRequired),
        // );
        // TODO: implement step
      })
      .and('the Customer is not signed in', async () => {
        // typescript body to translate:
        // await amplifyService.signOut();
        // TODO: implement step
      })
      .and('the Customer has already-registered account credentials', () => {
        // typescript body to translate:
        // accountCredentials = accountRepository.newAccount(
        //   new AccountCredentials(
        //     storedAlreadyRegisteredCognitoUser,
        //     enteredAlreadyRegisteredAccountCredentials.password,
        //   ),
        // );
        // TODO: implement step
      });
    when('the Customer authenticates already-registered account credentials', async () => {
      // typescript body to translate:
      // try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // typescript body to translate:
      // expect(signInSpy).toHaveBeenCalledWith({
      //   username: enteredAlreadyRegisteredAccountCredentials.email,
      //   password: enteredAlreadyRegisteredAccountCredentials.password,
      // });
      // TODO: implement step
    });
    when('Cognito returns PasswordResetRequiredException', () => {
      // TODO: implement step
    });
    then('the authentication requires a password reset', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('signIn', SignInFailure.PasswordResetRequired);
      // TODO: implement step
    })
      .and('Cognito does not issue an account token', () => {
        // typescript body to translate:
        // expect(accountCredentials.token).toBeNull();
        // TODO: implement step
      });
  });

  scenario('New password required', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // let caughtError: unknown;
    // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
    given('Cognito has an already-registered Cognito user', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(
      //   storedAlreadyRegisteredCognitoUser,
      //   enteredAlreadyRegisteredAccountCredentials.password,
      // );
      // TODO: implement step
    })
      .and('Cognito requires a new password for already-registered account credentials', () => {
        // typescript body to translate:
        // amplifyService.seedSignInNextStep(
        //   enteredAlreadyRegisteredAccountCredentials.email,
        //   SignInStep.NewPasswordRequired,
        // );
        // TODO: implement step
      })
      .and('the Customer is not signed in', async () => {
        // typescript body to translate:
        // await amplifyService.signOut();
        // TODO: implement step
      })
      .and('the Customer has already-registered account credentials', () => {
        // typescript body to translate:
        // accountCredentials = accountRepository.newAccount(
        //   new AccountCredentials(
        //     storedAlreadyRegisteredCognitoUser,
        //     enteredAlreadyRegisteredAccountCredentials.password,
        //   ),
        // );
        // TODO: implement step
      });
    when('the Customer authenticates already-registered account credentials', async () => {
      // typescript body to translate:
      // try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // typescript body to translate:
      // expect(signInSpy).toHaveBeenCalledWith({
      //   username: enteredAlreadyRegisteredAccountCredentials.email,
      //   password: enteredAlreadyRegisteredAccountCredentials.password,
      // });
      // TODO: implement step
    });
    when('Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED', () => {
      // TODO: implement step
    });
    then('the authentication requires a new password', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('signIn', SignInStep.NewPasswordRequired);
      // TODO: implement step
    })
      .and('Cognito does not issue an account token', () => {
        // typescript body to translate:
        // expect(accountCredentials.token).toBeNull();
        // TODO: implement step
      });
  });
});
