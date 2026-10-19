import { afterEach, beforeEach, vi } from 'vitest';
import { background, scenario, story } from 'stories/story-test';
import type { MockInstance } from 'vitest';
import {
  AccountCredentials,
  ValidationCodeResendWaitException,
  accountRepository,
} from '../../../domain/customer/Customer';
import { amplifyService } from '../../../domain/systems/amplify';
import { ValidationCode } from '../../../domain/systems/Cognito/Cognito';
import { storedUnconfirmedCognitoUser } from './examples/cognito-user.examples';
import { enteredValidAccountCredentials } from '../examples/account-credentials.examples';
import {
  unusableValidationCodeExamples,
  enteredValidValidationCode,
} from './examples/validation-code.examples';

story('Enter Validation Code', () => {
  afterEach(() => vi.useRealTimers());

  let confirmSignUpSpy: MockInstance<typeof amplifyService.confirmSignUp>;
  let signInSpy: MockInstance<typeof amplifyService.signIn>;
  beforeEach(() => {
    confirmSignUpSpy = vi.spyOn(amplifyService, 'confirmSignUp');
    signInSpy = vi.spyOn(amplifyService, 'signIn');
  });

  background('each', ({ given }) => {
    let accountCredentials: AccountCredentials;
    let emailedValidationCode: ValidationCode;

    given('the User has submitted valid account credentials', () => {})
      .and('Cognito has an unconfirmed Cognito user', () => {
        amplifyService.seedCognitoUser(storedUnconfirmedCognitoUser);
      })
      .and('Cognito has sent a validation code to the User', () => {
        amplifyService.seedValidationCode(enteredValidAccountCredentials.email, enteredValidValidationCode);
        emailedValidationCode = enteredValidValidationCode;
      })
      .and('the User has account credentials with valid email and password', () => {
        const cognitoUser = amplifyService.getUser(enteredValidAccountCredentials.email)!;
        accountCredentials = accountRepository.newAccount(
          new AccountCredentials(cognitoUser, enteredValidAccountCredentials.password),
        );
      });

    scenario('Enter validation code', ({ when, then }) => {
      when('the User activates the account with the emailed validation code', async () => {
        await accountCredentials.activate(emailedValidationCode);
      });
      then('My Paradise sends the correct confirmation request to Cognito', () => {
        expect(confirmSignUpSpy).toHaveBeenCalledWith({
          username: enteredValidAccountCredentials.email,
          confirmationCode: emailedValidationCode.code,
        });
      })
        .and('the account is verified', () => {
          expect(accountCredentials.verified).toBe(true);
        })
        .and('Cognito issues an account token for the browser session', () => {
          expect(signInSpy).toHaveBeenCalledWith({
            username: enteredValidAccountCredentials.email,
            password: enteredValidAccountCredentials.password,
          });
          expect(accountCredentials.token).toMatchObject({
            email: enteredValidAccountCredentials.email,
            customerId: null,
          });
        })
        .but('no Mavenir customer exists for those account credentials', () => {
          expect(accountCredentials.customerId).toBeNull();
        });
    });

    unusableValidationCodeExamples.forEach(({ example, validationCode, helper }) => {
      scenario(`Activate with unusable validation code: ${example}`, ({ when, then }) => {
        let caughtError: unknown;

        when(`the User activates with ${example}`, async () => {
          try { await accountCredentials.activate(validationCode); } catch (e) { caughtError = e; }
        });
        then(`Enter Validation Code shows ${helper}`, () => {
          expect(caughtError).toHaveProperty('validationCode', helper);
        });
      });
    });

    scenario('Resend validation code', ({ when, then }) => {
      let caughtError: unknown;

      when('more than 60 seconds has passed', async () => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 60_000));
      })
        .and('the User resends the validation code', async () => {
          await accountCredentials.resendValidationCode();
        });
      then('Cognito sends a new validation code', () => {
        expect(amplifyService.validationCodeSendsFor(accountCredentials.email).at(-1)?.kind)
          .toBe('resend');
      })
        .and('My Paradise shows the resend confirmation', () => {
          expect(accountCredentials.resendMessage)
            .toBe('We sent you a new code. Please check your email.');
        });

      when('less than 60 seconds has passed', async () => {
        vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 119_999));
      })
        .and('the User resends the validation code', async () => {
          try { await accountCredentials.resendValidationCode(); } catch (e) { caughtError = e; }
        });
      then('Resend waits 60 seconds before it can be used again', () => {
        expect(caughtError).toBeInstanceOf(ValidationCodeResendWaitException);
        expect((caughtError as ValidationCodeResendWaitException).availableAt)
          .toEqual(new Date(emailedValidationCode.sentAt.getTime() + 120_000));
      })
        .and('Cognito does not send another validation code during the wait', () => {
          expect(amplifyService.validationCodeSendsFor(accountCredentials.email))
            .toHaveLength(2);
        });

      when('more than 60 seconds has passed', async () => {
        vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 120_000));
      })
        .and('the User resends the validation code', async () => {
          await accountCredentials.resendValidationCode();
        });
      then('Cognito sends another validation code', () => {
        expect(amplifyService.validationCodeSendsFor(accountCredentials.email))
          .toHaveLength(3);
      });
    });
  });
});
