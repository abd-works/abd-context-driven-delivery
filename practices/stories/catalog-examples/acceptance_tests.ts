/**
 * Sub-epic: Create Customer — Story: Create Unconfirmed User
 * Catalog excerpt from pml-domainmodel/stories/onboard-a-customer/create-customer/create_customer_story.test.ts
 */

import { afterEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { background, scenario, story } from 'stories/story-test';
import { amplifyService } from '../../../domain/systems/amplify';
import {
  AccountCredentials,
  accountRepository,
} from '../../../domain/customer/Customer';
import { CreditServiceProviderId } from '../../../domain/systems/mavenir/billing';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import {
  enteredAlreadyRegisteredAccountCredentials,
  enteredValidAccountCredentials,
  expectedValidAccountCredentials,
  invalidCredentialOutlines,
} from '../examples/account-credentials.examples';
import { storedAlreadyRegisteredUnconfirmedCognitoUser } from './examples/cognito-user.examples';

afterEach(() => {
  amplifyService.reset();
  portalGateway.reset();
  shoppingCartGateway.reset();
  vi.restoreAllMocks();
});

story('Create Unconfirmed User', () => {
  background(({ given }) => {
    scenario('Display Create Account', ({ when, then }) => {
      let accountCredentials: AccountCredentials;
      when('the User proceeds to create an account from the Paradise Mobile website', () => {
        accountCredentials = accountRepository.newAccount();
      });
      then('the User can enter account credentials', () => {
        expect(accountCredentials.isUpdatable).toBe(true);
      })
        .but('the email and password rules are unmet', () => {
          const missing = accountCredentials.missingRequirements();
          expect(missing).toContain(accountCredentials.requirements.emailRequired);
          expect(missing).toContain(accountCredentials.requirements.passwordRequired);
          expect(missing).toContain(accountCredentials.requirements.confirmRequired);
        })
        .but('the customer cannot save the customer account', () => {
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

    invalidCredentialOutlines.forEach(({ example, unmet, credentials }) => {
      scenario(`Enter Invalid account credentials: ${example}`, ({ when, then }) => {
        let accountCredentials: AccountCredentials;
        let caughtError: unknown;

        when(`the User registers ${example}`, async () => {
          accountCredentials = accountRepository.newAccount(credentials);
          try { await accountCredentials.register(); } catch (e) { caughtError = e; }
        });
        then('the account cannot be registered', () => {
          expect(caughtError).toHaveProperty('register', 'Account credential requirements are unmet');
        }).and(`the ${unmet} requirement is unmet`, () => {
          const missing = accountCredentials.missingRequirements();
          const expectedRequirement = (accountCredentials.requirements as Record<string, unknown>)[unmet];
          expect(missing).toContain(expectedRequirement);
        });
      });
    });

    scenario('Email already registered', ({ given, when, then }) => {
      let caughtError: unknown;
      let accountCredentials: AccountCredentials;
      given('already-registered account credentials are already registered', async () => {
        amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
      });
      when('the User registers already-registered account credentials', async () => {
        accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
        try { await accountCredentials.register(); } catch (e) { caughtError = e; }
      });
      then('the email is already registered', () => {
        expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
      })
        .and('the system displays that the email is already registered', () => {
          expect(accountCredentials.errorMessage).toBe('The email address is already in use. Please use a different email address.');
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
            'custom:serviceproviderId': CreditServiceProviderId.Paradise,
          }},
        });
        expect(accountCredentials.verified).toBe(false);
        expect(accountCredentials.token).toBeNull();
        expect(accountCredentials.customerId).toBeNull();
      });
    });
  });
});
