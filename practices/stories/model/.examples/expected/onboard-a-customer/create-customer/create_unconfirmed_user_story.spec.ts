/**
 * Sub-epic: Create Unconfirmed User
 */

import { background, scenario, story } from 'stories/story-test';
import { vi } from 'vitest';
import type { MockInstance } from 'vitest';
import {
  enteredAlreadyRegisteredAccountCredentials,
  enteredValidAccountCredentials,
  expectedValidAccountCredentials,
  enteredInvalidPasswordLetters,
  enteredInvalidPasswordNumber,
  enteredInvalidPasswordSymbol,
  enteredInvalidPasswordLength,
  enteredInvalidConfirmRequired,
  enteredInvalidConfirmMismatch,
  enteredInvalidEmailRequired,
  enteredInvalidEmailFormat,
} from '../examples/account-credentials.examples';
import { storedAlreadyRegisteredUnconfirmedCognitoUser } from './examples/cognito-user.examples';
import { accountRepository, AccountCredentials } from '../../../domain/customer/Customer';
import { amplifyService } from '../../../domain/systems/amplify';

story('Create Unconfirmed Cognito User', () => {
  background(({ given }) => {
    scenario('Display Create Account', ({ when, then }) => {
      let accountCredentials: AccountCredentials;
      when('the User proceeds to create an account from the Paradise Mobile website', () => {
        accountCredentials = accountRepository.newAccount();
      });
      then('the User can enter account credentials', () => {
        expect(accountCredentials.isUpdatable).toBe(true);
      })
        .and('the email and password rules are unmet', () => {
          const missing = accountCredentials.missingRequirements();
          expect(missing).toContain(accountCredentials.requirements.emailRequired);
          expect(missing).toContain(accountCredentials.requirements.passwordRequired);
          expect(missing).toContain(accountCredentials.requirements.confirmRequired);
        })
        .and('the customer cannot save the customer account', () => {
          expect(accountCredentials.isPersistable).toBe(false);
        });
    });

    scenario('Enter Valid account credentials', ({ when, then }) => {
      let accountCredentials: AccountCredentials;

      when('the User enters valid account credentials', () => {
        accountCredentials = accountRepository.newAccount(enteredValidAccountCredentials);
      });
      then('account credentials are validated continuously', () => {
        expect(accountCredentials.missingRequirements()).toHaveLength(0);
      })
        .and('the customer can save the customer account', () => {
          expect(accountCredentials.isPersistable).toBe(true);
        });
    });
    
    const outlines = [
      { example: 'missing email',            unmet: 'emailRequired',    credentials: enteredInvalidEmailRequired },
      { example: 'invalid email format',     unmet: 'emailFormat',      credentials: enteredInvalidEmailFormat },
      { example: 'missing password',         unmet: 'passwordRequired', credentials: new AccountCredentials(enteredValidAccountCredentials.email, '', '', '', false) },
      { example: 'password missing letters', unmet: 'passwordLetters',  credentials: enteredInvalidPasswordLetters },
      { example: 'password missing number',  unmet: 'passwordNumber',   credentials: enteredInvalidPasswordNumber },
      { example: 'password missing symbol',  unmet: 'passwordSymbol',   credentials: enteredInvalidPasswordSymbol },
      { example: 'password too short',       unmet: 'passwordLength',   credentials: enteredInvalidPasswordLength },
      { example: 'confirm password missing', unmet: 'confirmRequired',  credentials: enteredInvalidConfirmRequired },
      { example: 'confirm password mismatch',unmet: 'confirmMismatch',  credentials: enteredInvalidConfirmMismatch },
    ];

    outlines.forEach(({ example, unmet, credentials }) => {
      scenario(`Enter Invalid account credentials: ${example}`, ({ when, then }) => {
        let accountCredentials: AccountCredentials;
        when(`the User validates ${example}`, () => {
          accountCredentials = accountRepository.newAccount(credentials);
        });
        then(`the ${unmet} requirement is unmet`, () => {
          const missing = accountCredentials.missingRequirements();
          const expectedRequirement = (accountCredentials.requirements as any)[unmet];
          expect(missing).toContain(expectedRequirement);
        })
        .and('the customer cannot save the customer account', () => {
          expect(accountCredentials.isPersistable).toBe(false);
        });
      });
    });

    scenario('Email already registered', ({ given, when, then }) => {
      let caughtError: unknown;

      given('already-registered account credentials are already registered', async () => {
        amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
      });
      when('the User registers already-registered account credentials', async () => {
        const accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
        try { await accountCredentials.register(); } catch (e) { caughtError = e; }
      });
      then('Email shows the already-registered error', () => {
        expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
      });
    });


    scenario('Create Unconfirmed User', ({ given, when, then }) => {
      let accountCredentials: AccountCredentials;
      let amplifySignUpSpy: MockInstance<typeof amplifyService.signUp>;

      given('the amplifyService.signUp spy is set up', () => {
        amplifySignUpSpy = vi.spyOn(amplifyService, 'signUp');
      });
      when('the User creates their account', async () => {
        accountCredentials = accountRepository.newAccount(enteredValidAccountCredentials);
        await accountCredentials.register();
      });
      then('the system creates an unconfirmed Cognito user and emails a validation code', () => {
        expect(amplifySignUpSpy).toHaveBeenCalledWith({
          username: expectedValidAccountCredentials.email,
          password: expectedValidAccountCredentials.password,
          options: { userAttributes: {
            email: expectedValidAccountCredentials.email,
            'custom:language': 'en',
            'custom:role': 'customer',
            'custom:serviceproviderId': '100000000',
          }},
        });
        expect(accountCredentials.verified).toBe(false);
        expect(accountCredentials.token).toBeNull();
        expect(accountCredentials.customerId).toBeNull();
        expect(amplifyService.sentValidationCodesFor(expectedValidAccountCredentials.email)).toContain('123456');
      });
    });

    scenario('Email already registered in Cognito', ({ given, when, then }) => {
      let caughtError: unknown;
      given('an unconfirmed Cognito user exists for already-registered account credentials', async () => {
        amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
      });
      when('Cognito is asked to register already-registered account credentials', async () => {
        const accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
        try { await accountCredentials.register(); } catch (e) { caughtError = e; }
      });
      then('Cognito returns UsernameExistsException', () => {
        expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
      })
        .and('Cognito does not create another Cognito user', () => {});
    });
  }); 

});
