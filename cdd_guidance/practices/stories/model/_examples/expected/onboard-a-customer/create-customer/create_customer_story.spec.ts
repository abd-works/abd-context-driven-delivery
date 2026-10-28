/**
 * Sub-epic: Create Customer
 */

import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { background, scenario, story } from 'stories/story-test';
import { AccountToken, CognitoUser } from '../../../domain/systems/Cognito/Cognito';
import { amplifyService } from '../../../domain/systems/amplify';
import {
  AccountCredentials,
  Customer,
  accountRepository,
  customerRepository,
} from '../../../domain/customer/Customer';
import { MavenirCreateCustomerRequest, portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { enteredValidAccountCredentials } from '../examples/account-credentials.examples';

afterEach(() => vi.restoreAllMocks());

function mavenirCreateRequest(email: string): MavenirCreateCustomerRequest {
  return expect.objectContaining({
    email,
    serviceProviderId: '100000000',
    source: 'on-boarding',
    contactMedium: expect.arrayContaining([
      expect.objectContaining({ characteristic: { emailAddress: email } }),
    ]),
  }) as unknown as MavenirCreateCustomerRequest;
}

story('Create Customer', () => {
  let createSpy: MockInstance<typeof portalGateway.create>;
  let updateAttributesSpy: MockInstance<typeof amplifyService.updateUserAttributes>;
  beforeEach(() => {
    createSpy = vi.spyOn(portalGateway, 'create');
    updateAttributesSpy = vi.spyOn(amplifyService, 'updateUserAttributes');
  });

  background('each', ({ given }) => {
    let accountCredentials: AccountCredentials;

    given('the User has a verified account with an account token', () => {
      const cognitoUser = amplifyService.seedCognitoUser(new CognitoUser(
        enteredValidAccountCredentials.email,
        true,
        null,
        new AccountToken(enteredValidAccountCredentials.email, null, `token:${enteredValidAccountCredentials.email}`),
      ));
      accountCredentials = accountRepository.newAccount(new AccountCredentials(
        enteredValidAccountCredentials.email,
        enteredValidAccountCredentials.password,
        enteredValidAccountCredentials.confirmPassword,
        enteredValidAccountCredentials.validationCode,
        cognitoUser.confirmed,
        cognitoUser,
      ));
    });

    scenario('Create customer', ({ when, then }) => {
      let result: Customer;

      when('the User creates their Paradise account', async () => {
        result = await customerRepository.create(accountCredentials);
      });
      then('My Paradise sends the correct create request to Mavenir', () => {
        expect(createSpy).toHaveBeenCalledWith(mavenirCreateRequest(enteredValidAccountCredentials.email));
      });
      when('Mavenir creates the customer', async () => {
        result = await customerRepository.load(accountCredentials);
      });
      then('the customer has a Mavenir customer id', () => {
        expect(result).toBeInstanceOf(Customer);
        expect(result.id).toBe('cus_1');
      })
        .and('My Paradise stores the customer id on the Cognito user', () => {
          expect(updateAttributesSpy).toHaveBeenCalledWith({ userAttributes: { 'custom:customerId': 'cus_1' } });
        });
    });

    scenario('Mavenir customer already exists', ({ given, when, then }) => {
      let caughtError: unknown;

      given('Mavenir already has a customer for that email', () => {
        portalGateway.seedCustomer(enteredValidAccountCredentials.email);
      });
      when('the User creates their Paradise account', async () => {
        try { await customerRepository.create(accountCredentials); } catch (e) { caughtError = e; }
      });
      then('My Paradise shows Could not create customer', () => {
        expect(caughtError).toHaveProperty('message', 'Could not create customer.');
      });
    });
  });
});
