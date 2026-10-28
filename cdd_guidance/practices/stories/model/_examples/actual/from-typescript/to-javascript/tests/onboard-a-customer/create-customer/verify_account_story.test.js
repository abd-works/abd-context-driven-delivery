/**
 * Epic: Verify Account
 * Orders: 0.0.0.3
 */

import { background, scenario, story } from "../../story-test.js";
import { enteredValidAccountCredentials } from "./examples";

/**
 * Story: Enter Validation Code
 */

// background-examples: {"storedUnconfirmedCognitoUser": {}, "enteredValidAccountCredentials": {}, "unusableValidationCodeExamples": {}, "enteredValidValidationCode": {}}
story('Enter Validation Code', () => {
  // typescript body to translate:
  // afterEach(() => vi.useRealTimers());
  //
  // let confirmSignUpSpy: MockInstance<typeof amplifyService.confirmSignUp>;
  // let signInSpy: MockInstance<typeof amplifyService.signIn>;
  // beforeEach(() => {
  //   confirmSignUpSpy = vi.spyOn(amplifyService, 'confirmSignUp');
  //   signInSpy = vi.spyOn(amplifyService, 'signIn');
  // });
  background('each', ({ given }) => {
    given('the User has submitted valid account credentials', () => {
      // TODO: implement step
    })
      .and('Cognito has an unconfirmed Cognito user', () => {
        // typescript body to translate:
        // amplifyService.seedCognitoUser(storedUnconfirmedCognitoUser);
        // TODO: implement step
      })
      .and('Cognito has sent a validation code to the User', () => {
        // typescript body to translate:
        // amplifyService.seedValidationCode(enteredValidAccountCredentials.email, enteredValidValidationCode);
        // emailedValidationCode = enteredValidValidationCode;
        // TODO: implement step
      })
      .and('the User has account credentials with valid email and password', () => {
        // typescript body to translate:
        // const cognitoUser = amplifyService.getUser(enteredValidAccountCredentials.email)!;
        // accountCredentials = accountRepository.newAccount(
        //   new AccountCredentials(cognitoUser, enteredValidAccountCredentials.password),
        // );
        // TODO: implement step
      });
  });
  scenario('Enter validation code', ({ given, when, then }) => {
    // examples: enteredValidAccountCredentials
    when('the User activates the account with the emailed validation code', async () => {
      // typescript body to translate:
      // await accountCredentials.activate(emailedValidationCode);
      // TODO: implement step
    });
    then('My Paradise sends the correct confirmation request to Cognito', () => {
      // typescript body to translate:
      // expect(confirmSignUpSpy).toHaveBeenCalledWith({
      //   username: enteredValidAccountCredentials.email,
      //   confirmationCode: emailedValidationCode.code,
      // });
      // TODO: implement step
    })
      .and('the account is verified', () => {
        // typescript body to translate:
        // expect(accountCredentials.verified).toBe(true);
        // TODO: implement step
      })
      .and('Cognito issues an account token for the browser session', () => {
        // typescript body to translate:
        // expect(signInSpy).toHaveBeenCalledWith({
        //   username: enteredValidAccountCredentials.email,
        //   password: enteredValidAccountCredentials.password,
        // });
        // expect(accountCredentials.token).toMatchObject({
        //   email: enteredValidAccountCredentials.email,
        //   customerId: null,
        // });
        // TODO: implement step
      })
      .but('no Mavenir customer exists for those account credentials', () => {
        // typescript body to translate:
        // expect(accountCredentials.customerId).toBeNull();
        // TODO: implement step
      });
  });

  scenario('Activate with unusable validation code: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let caughtError: unknown;
    when('the User activates with ${example}', async () => {
      // typescript body to translate:
      // try { await accountCredentials.activate(validationCode); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('Enter Validation Code shows ${helper}', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('validationCode', helper);
      // TODO: implement step
    });
  });

  scenario('Resend validation code', ({ given, when, then }) => {
    // typescript body to translate:
    // let caughtError: unknown;
    when('more than 60 seconds has passed', () => {
      // typescript body to translate:
      // vi.useFakeTimers();
      // vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 60_000));
      // TODO: implement step
    })
      .and('the User resends the validation code', async () => {
        // typescript body to translate:
        // await accountCredentials.resendValidationCode();
        // TODO: implement step
      });
    then('Cognito sends a new validation code', () => {
      // typescript body to translate:
      // expect(amplifyService.validationCodeSendsFor(accountCredentials.email).at(-1)?.kind)
      //   .toBe('resend');
      // TODO: implement step
    })
      .and('My Paradise shows the resend confirmation', () => {
        // typescript body to translate:
        // expect(accountCredentials.resendMessage)
        //   .toBe('We sent you a new code. Please check your email.');
        // TODO: implement step
      });
    when('less than 60 seconds has passed', () => {
      // typescript body to translate:
      // vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 119_999));
      // TODO: implement step
    })
      .and('the User resends the validation code', async () => {
        // typescript body to translate:
        // try { await accountCredentials.resendValidationCode(); } catch (e) { caughtError = e; }
        // TODO: implement step
      });
    then('Resend waits 60 seconds before it can be used again', () => {
      // typescript body to translate:
      // expect(caughtError).toBeInstanceOf(ValidationCodeResendWaitException);
      // expect((caughtError as ValidationCodeResendWaitException).availableAt)
      //   .toEqual(new Date(emailedValidationCode.sentAt.getTime() + 120_000));
      // TODO: implement step
    })
      .and('Cognito does not send another validation code during the wait', () => {
        // typescript body to translate:
        // expect(amplifyService.validationCodeSendsFor(accountCredentials.email))
        //   .toHaveLength(2);
        // TODO: implement step
      });
    when('more than 60 seconds has passed', () => {
      // typescript body to translate:
      // vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 120_000));
      // TODO: implement step
    })
      .and('the User resends the validation code', async () => {
        // typescript body to translate:
        // await accountCredentials.resendValidationCode();
        // TODO: implement step
      });
    then('Cognito sends another validation code', () => {
      // typescript body to translate:
      // expect(amplifyService.validationCodeSendsFor(accountCredentials.email))
      //   .toHaveLength(3);
      // TODO: implement step
    });
  });
});
