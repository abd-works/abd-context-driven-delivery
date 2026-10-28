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
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    when('the User proceeds to create an account from the Paradise Mobile website', () => {
      // typescript body to translate:
      // accountCredentials = accountRepository.newAccount();
      // TODO: implement step
    });
    then('the User can enter account credentials', () => {
      // typescript body to translate:
      // expect(accountCredentials.isUpdatable).toBe(true);
      // TODO: implement step
    })
      .and('the email and password rules are unmet', () => {
        // typescript body to translate:
        // const missing = accountCredentials.missingRequirements();
        // expect(missing).toContain(accountCredentials.requirements.emailRequired);
        // expect(missing).toContain(accountCredentials.requirements.passwordRequired);
        // expect(missing).toContain(accountCredentials.requirements.confirmRequired);
        // TODO: implement step
      })
      .and('the customer cannot save the customer account', () => {
        // typescript body to translate:
        // expect(accountCredentials.isPersistable).toBe(false);
        // TODO: implement step
      });
  });

  scenario('Enter Valid account credentials', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // examples: enteredValidAccountCredentials
    when('the User enters valid account credentials', () => {
      // typescript body to translate:
      // accountCredentials = accountRepository.newAccount(enteredValidAccountCredentials);
      // TODO: implement step
    });
    then('account credentials are validated continuously', () => {
      // typescript body to translate:
      // expect(accountCredentials.missingRequirements()).toHaveLength(0);
      // TODO: implement step
    })
      .and('the customer can save the customer account', () => {
        // typescript body to translate:
        // expect(accountCredentials.isPersistable).toBe(true);
        // TODO: implement step
      });
  });

  scenario('Enter Invalid account credentials: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    when('the User validates ${example}', () => {
      // typescript body to translate:
      // accountCredentials = accountRepository.newAccount(credentials);
      // TODO: implement step
    });
    then('the ${unmet} requirement is unmet', () => {
      // typescript body to translate:
      // const missing = accountCredentials.missingRequirements();
      // const expectedRequirement = (accountCredentials.requirements as any)[unmet];
      // expect(missing).toContain(expectedRequirement);
      // TODO: implement step
    })
      .and('the customer cannot save the customer account', () => {
        // typescript body to translate:
        // expect(accountCredentials.isPersistable).toBe(false);
        // TODO: implement step
      });
  });

  scenario('Email already registered', ({ given, when, then }) => {
    // typescript body to translate:
    // let caughtError: unknown;
    // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
    given('already-registered account credentials are already registered', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
      // TODO: implement step
    });
    when('the User registers already-registered account credentials', async () => {
      // typescript body to translate:
      // const accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
      // try { await accountCredentials.register(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('Email shows the already-registered error', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
      // TODO: implement step
    });
  });

  scenario('Create Unconfirmed User', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials: AccountCredentials;
    // let amplifySignUpSpy: MockInstance<typeof amplifyService.signUp>;
    // examples: enteredValidAccountCredentials, expectedValidAccountCredentials
    given('the amplifyService.signUp spy is set up', () => {
      // typescript body to translate:
      // amplifySignUpSpy = vi.spyOn(amplifyService, 'signUp');
      // TODO: implement step
    });
    when('the User creates their account', async () => {
      // typescript body to translate:
      // accountCredentials = accountRepository.newAccount(enteredValidAccountCredentials);
      // await accountCredentials.register();
      // TODO: implement step
    });
    then('the system creates an unconfirmed Cognito user and emails a validation code', () => {
      // typescript body to translate:
      // expect(amplifySignUpSpy).toHaveBeenCalledWith({
      //   username: expectedValidAccountCredentials.email,
      //   password: expectedValidAccountCredentials.password,
      //   options: { userAttributes: {
      //     email: expectedValidAccountCredentials.email,
      //     'custom:language': 'en',
      //     'custom:role': 'customer',
      //     'custom:serviceproviderId': '100000000',
      //   }},
      // });
      // expect(accountCredentials.verified).toBe(false);
      // expect(accountCredentials.token).toBeNull();
      // expect(accountCredentials.customerId).toBeNull();
      // expect(amplifyService.sentValidationCodesFor(expectedValidAccountCredentials.email)).toContain('123456');
      // TODO: implement step
    });
  });

  scenario('Email already registered in Cognito', ({ given, when, then }) => {
    // typescript body to translate:
    // let caughtError: unknown;
    // examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
    given('an unconfirmed Cognito user exists for already-registered account credentials', () => {
      // typescript body to translate:
      // amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
      // TODO: implement step
    });
    when('Cognito is asked to register already-registered account credentials', async () => {
      // typescript body to translate:
      // const accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
      // try { await accountCredentials.register(); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('Cognito returns UsernameExistsException', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
      // TODO: implement step
    })
      .and('Cognito does not create another Cognito user', () => {
        // TODO: implement step
      });
  });
});
