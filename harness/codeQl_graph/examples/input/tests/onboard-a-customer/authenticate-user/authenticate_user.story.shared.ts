/**
 * Sub-epic: Authenticate User
 */

import { expect } from 'vitest';
import {
  AccountCredentials,
  AccountCredentialsException,
  AccountCredentialsOperation,
  OnboardingStep,
  ValidationCode,
  ValidationCodeResendWaitException,
  accountCredentialsRepository,
} from '@src/account-credentials/account-credentials';
import { scenario, shareStory, background } from 'tests/story-test';
import {
  alreadyRegisteredAccountCredentials,
  invalidAccountCredentialsOutlineCases,
  invalidAccountCredentialsOutlines,
  invalidEmailFormatAccountCredentials,
  seedAlreadyRegisteredAccountCredentials,
  unknownEmailAccountCredentials,
  unverifiedAccountCredentials,
  wrongPasswordAccountCredentials,
} from './examples/account-credentials.examples';
import {
  emailedValidationCode,
  resentValidationCode,
  resentValidationCodeHelperMessage,
  unusableValidationCodeExamples,
} from './examples/validation-code.examples';

shareStory('Create Account', () => {
  background(({ given }) => {
    given('the User is creating an account', () => undefined);
  });

  scenario('Display Create Account', ({ when, then }) => {
    let accountCredentials: AccountCredentials;

    when('the User proceeds to create an account from the Paradise Mobile website', () => {
      accountCredentials = accountCredentialsRepository.new();
    });
    then('the User can enter account credentials', () => {
      expect(accountCredentials.isUpdatable).toBe(true);
    })
      .and('the email and password rules are unmet', () => {
        const missing = accountCredentials.missingRequirements();
        expect(missing).toContain(accountCredentials.requirements.emailRequired);
        expect(missing).toContain(accountCredentials.requirements.passwordRequired);
      })
      .and('the customer cannot save the customer account', () => {
        expect(accountCredentials.isPersistable).toBe(false);
      });
  });

  scenario('Enter Valid account credentials', ({ when, then }) => {
    let accountCredentials: AccountCredentials;

    when('the User enters valid account credentials', () => {
      accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
    });
    then('account credentials are validated continuously', () => {
      expect(accountCredentials.missingRequirements()).toHaveLength(0);
    })
      .and('the customer can save the customer account', () => {
        expect(accountCredentials.isPersistable).toBe(true);
      });
  });

  scenario('Log out and log back in', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let signingIn: AccountCredentials;

    given('the User has entered valid account credentials', async () => {
      accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
      await accountCredentials.register();
      await accountCredentials.verify(emailedValidationCode);
    });
    when('the User logs out of the site', async () => {
      await accountCredentials.signOut();
    });
    then('the account has no browser session', () => {
      expect(accountCredentials.token).toBeNull();
    });
    when('the User enters the username and password', async () => {
      signingIn = unverifiedAccountCredentials(accountCredentialsRepository);
      await signingIn.authenticateAccount();
    });
    then('the account is logged in', () => {
      expect(signingIn.token?.email).toBe(signingIn.email);
      expect(signingIn.token?.jwt).toBeTruthy();
    });
  });

  invalidAccountCredentialsOutlineCases().forEach(({ example, unmet }) => {
    scenario(`Enter Invalid account credentials: ${example}`, ({ when, then }) => {
      let accountCredentials: AccountCredentials;
      let caughtError: unknown;

      when(`the User registers ${example}`, async () => {
        accountCredentials = invalidAccountCredentialsOutlines(accountCredentialsRepository, example);
        try {
          await accountCredentials.register();
        } catch (error) {
          caughtError = error;
        }
      });
      then('the account cannot be registered', () => {
        expect(caughtError).toBeInstanceOf(AccountCredentialsException);
        expect((caughtError as AccountCredentialsException).operation).toBe(AccountCredentialsOperation.Register);
        expect((caughtError as AccountCredentialsException).message).toBe('Account credential requirements are unmet');
      })
        .and(`the ${unmet} requirement is unmet`, () => {
          expect(accountCredentials.missingRequirements()).toContain(accountCredentials.requirements[unmet]);
        });
    });
  });

  scenario('Email already registered', ({ given, when, then }) => {
    let caughtError: unknown;

    given('already-registered account credentials are already registered', async () => {
      await alreadyRegisteredAccountCredentials(accountCredentialsRepository).register();
    });
    when('the User registers already-registered account credentials', async () => {
      try {
        await alreadyRegisteredAccountCredentials(accountCredentialsRepository).register();
      } catch (error) {
        caughtError = error;
      }
    });
    then('the email is already registered', () => {
      expect(caughtError).toBeInstanceOf(AccountCredentialsException);
      expect((caughtError as AccountCredentialsException).message).toBe('Email is already registered.');
    });
  });

  scenario('Create account', ({ when, then }) => {
    let accountCredentials: AccountCredentials;

    when('the User creates their account', async () => {
      accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
      await accountCredentials.register();
    });
    then('the account is unconfirmed and a validation code is emailed', () => {
      expect(accountCredentials.verified).toBe(false);
      expect(accountCredentials.token).toBeNull();
      expect(accountCredentials.validationCodeWasSent).toBe(true);
      expect(accountCredentials.expectedValidationCode).toBe(emailedValidationCode.code);
    });
  });
});

shareStory('Enter Validation Code', () => {
  scenario('Enter validation code', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;

    given('the User has submitted valid account credentials', async () => {
      accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
      await accountCredentials.register();
    })
      .and('an unconfirmed account exists', async () => {
        const stored = await accountCredentialsRepository.load(accountCredentials.email);
        expect(stored?.verified).toBe(false);
      })
      .and('a validation code has been sent to the User', () => {
        expect(accountCredentials.validationCodeWasSent).toBe(true);
        expect(accountCredentials.expectedValidationCode).toBe(emailedValidationCode.code);
      });
    when('the User verifies the account with the emailed validation code', async () => {
      await accountCredentials.verify(emailedValidationCode);
    });
    then('the account is verified', () => {
      expect(accountCredentials.verified).toBe(true);
    })
      .and('the account has a token for the browser session', () => {
        expect(accountCredentials.token?.email).toBe(accountCredentials.email);
        expect(accountCredentials.token?.jwt).toBeTruthy();
      });
  });

  unusableValidationCodeExamples.forEach(({ example, code, helperMessage }) => {
    scenario(`Activate with unusable validation code: ${example}`, ({ given, when, then }) => {
      let accountCredentials: AccountCredentials;
      let caughtError: unknown;

      given('the User has submitted valid account credentials', async () => {
        accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
        await accountCredentials.register();
      })
        .and('an unconfirmed account exists', async () => {
          const stored = await accountCredentialsRepository.load(accountCredentials.email);
          expect(stored?.verified).toBe(false);
        })
        .and('a validation code has been sent to the User', () => {
          expect(accountCredentials.validationCodeWasSent).toBe(true);
          expect(accountCredentials.expectedValidationCode).toBe(emailedValidationCode.code);
        });
      when(`the User verifies with ${example}`, async () => {
        try {
          await accountCredentials.verify(new ValidationCode(code));
        } catch (error) {
          caughtError = error;
        }
      });
      then('the validation code is rejected', () => {
        expect(caughtError).toBeInstanceOf(AccountCredentialsException);
        expect((caughtError as AccountCredentialsException).operation).toBe(AccountCredentialsOperation.ValidationCode);
        expect((caughtError as AccountCredentialsException).message).toBe(helperMessage);
      });
    });
  });

  scenario('Resend validation code', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;
    const wait = AccountCredentials.RESEND_WAIT_MILLISECONDS;

    given('the User has submitted valid account credentials', async () => {
      accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
      await accountCredentials.register();
    })
      .and('an unconfirmed account exists', async () => {
        const stored = await accountCredentialsRepository.load(accountCredentials.email);
        expect(stored?.verified).toBe(false);
      })
      .and('a validation code has been sent to the User', () => {
        expect(accountCredentials.validationCodeWasSent).toBe(true);
        expect(accountCredentials.expectedValidationCode).toBe(emailedValidationCode.code);
      });
    when('more than 60 seconds has passed', () => {
      accountCredentials._validationCodeSentAt = new Date(Date.now() - wait - 1);
    })
      .and('the User resends the validation code', async () => {
        await accountCredentials.resendValidationCode();
      });
    then('a new validation code is sent', () => {
      expect(accountCredentials.expectedValidationCode).toBe(resentValidationCode.code);
      expect(accountCredentials.validationCodeMessages).toHaveLength(2);
    })
      .and('the Customer is told a new code was sent', () => {
        expect(accountCredentials.resendMessage).toBe(resentValidationCodeHelperMessage);
      });

    when('less than 60 seconds has passed', () => {
      accountCredentials._validationCodeSentAt = new Date();
    })
      .and('the User resends the validation code', async () => {
        try {
          await accountCredentials.resendValidationCode();
        } catch (error) {
          caughtError = error;
        }
      });
    then('resend waits 60 seconds before it can be used again', () => {
      expect(caughtError).toBeInstanceOf(ValidationCodeResendWaitException);
      expect((caughtError as ValidationCodeResendWaitException).availableAt)
        .toEqual(new Date(accountCredentials._validationCodeSentAt!.getTime() + wait));
    })
      .and('another validation code is not sent during the wait', () => {
        expect(accountCredentials.validationCodeMessages).toHaveLength(2);
      });

    when('more than 60 seconds has passed', () => {
      accountCredentials._validationCodeSentAt = new Date(Date.now() - wait - 1);
    })
      .and('the User resends the validation code', async () => {
        await accountCredentials.resendValidationCode();
      });
    then('another validation code is sent', () => {
      expect(accountCredentials.validationCodeMessages).toHaveLength(3);
      expect(accountCredentials.validationCodeMessages.at(-1)?.code).toBe(resentValidationCode.code);
      expect(accountCredentials.resendMessage).toBe(resentValidationCodeHelperMessage);
    });
  });
});

shareStory('Sign In With Existing Account', () => {
  scenario('Sign in with already-registered account credentials', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;

    given('an already-registered account exists', () => {
      seedAlreadyRegisteredAccountCredentials(accountCredentialsRepository, 'cus_existing');
    })
      .and('the Customer is not signed in', () => {
        accountCredentials = alreadyRegisteredAccountCredentials(accountCredentialsRepository);
      })
      .and('the Customer has already-registered account credentials', () => {
        expect(accountCredentials.verified).toBe(true);
        expect(accountCredentials.token).toBeNull();
      });
    when('the Customer authenticates already-registered account credentials', async () => {
      await accountCredentials.authenticateAccount();
    });
    then('the account has a token for the browser session', () => {
      expect(accountCredentials.token?.email).toBe(accountCredentials.email);
      expect(accountCredentials.token?.jwt).toBeTruthy();
    })
      .and('the account holds the customer id', () => {
        expect(accountCredentials.customerId).toBe('cus_existing');
      });
  });

  scenario('Email format is unmet', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('the Customer has invalid email format account credentials', () => {
      accountCredentials = invalidEmailFormatAccountCredentials(accountCredentialsRepository);
    });
    when('the Customer authenticates invalid email format', async () => {
      try {
        await accountCredentials.authenticateAccount();
      } catch (error) {
        caughtError = error;
      }
    });
    then('the authentication is rejected', () => {
      expect(caughtError).toBeInstanceOf(AccountCredentialsException);
      expect((caughtError as AccountCredentialsException).operation).toBe(AccountCredentialsOperation.SignIn);
      expect((caughtError as AccountCredentialsException).message).toBe('Account credential requirements are unmet');
    })
      .and('the account has no token', () => {
        expect(accountCredentials.token).toBeNull();
      });
  });

  scenario('Authenticate with incorrect account credentials: wrong password', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('an already-registered account exists', () => {
      seedAlreadyRegisteredAccountCredentials(accountCredentialsRepository);
    })
      .and('the Customer is not signed in', () => {
        accountCredentials = wrongPasswordAccountCredentials(accountCredentialsRepository);
      })
      .and('the Customer has wrong password', () => {
        expect(accountCredentials.token).toBeNull();
      });
    when('the Customer authenticates wrong password', async () => {
      try {
        await accountCredentials.authenticateAccount();
      } catch (error) {
        caughtError = error;
      }
    });
    then('the authentication is rejected', () => {
      expect(caughtError).toBeInstanceOf(AccountCredentialsException);
      expect((caughtError as AccountCredentialsException).operation).toBe(AccountCredentialsOperation.SignIn);
      expect((caughtError as AccountCredentialsException).message).toBe(
        accountCredentials.requirements.signInMismatch.requirement,
      );
    })
      .and('the account has no token', () => {
        expect(accountCredentials.token).toBeNull();
      });
  });

  scenario('Authenticate with incorrect account credentials: unknown email', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;
    let caughtError: unknown;

    given('an already-registered account exists', () => {
      seedAlreadyRegisteredAccountCredentials(accountCredentialsRepository);
    })
      .and('the Customer is not signed in', () => {
        accountCredentials = unknownEmailAccountCredentials(accountCredentialsRepository);
      })
      .and('the Customer has unknown email', () => {
        expect(accountCredentials.token).toBeNull();
      });
    when('the Customer authenticates unknown email', async () => {
      try {
        await accountCredentials.authenticateAccount();
      } catch (error) {
        caughtError = error;
      }
    });
    then('the authentication is rejected', () => {
      expect(caughtError).toBeInstanceOf(AccountCredentialsException);
      expect((caughtError as AccountCredentialsException).operation).toBe(AccountCredentialsOperation.SignIn);
      expect((caughtError as AccountCredentialsException).message).toBe(
        accountCredentials.requirements.signInMismatch.requirement,
      );
    })
      .and('the account has no token', () => {
        expect(accountCredentials.token).toBeNull();
      });
  });

  scenario('Authenticate with unconfirmed account', ({ given, when, then }) => {
    let accountCredentials: AccountCredentials;

    given('an unconfirmed account exists', async () => {
      await unverifiedAccountCredentials(accountCredentialsRepository).register();
    })
      .and('the Customer is not signed in', () => {
        accountCredentials = unverifiedAccountCredentials(accountCredentialsRepository);
      })
      .and('the Customer has unconfirmed sign-in account credentials', async () => {
        const stored = await accountCredentialsRepository.load(accountCredentials.email);
        expect(stored?.verified).toBe(false);
        expect(stored?.customerId).toBeNull();
        expect(accountCredentials.token).toBeNull();
      });
    when('the Customer authenticates unconfirmed sign-in', async () => {
      await accountCredentials.authenticateAccount();
    });
    then('the account has a token for the browser session', () => {
      expect(accountCredentials.token?.email).toBe(accountCredentials.email);
      expect(accountCredentials.token?.jwt).toBeTruthy();
    })
      .and('the account has no customer', () => {
        expect(accountCredentials.verified).toBe(false);
        expect(accountCredentials.customerId).toBeNull();
      })
      .and('the Customer can enter the validation code', () => {
        expect(accountCredentials.validationCodeWasSent).toBe(true);
        expect(accountCredentials.expectedValidationCode).toBe(emailedValidationCode.code);
      })
      .and('the Customer is on the Verify Account step', () => {
        expect(accountCredentials.onboardingStep).toBe(OnboardingStep.VerifyAccount);
      });
  });
});
