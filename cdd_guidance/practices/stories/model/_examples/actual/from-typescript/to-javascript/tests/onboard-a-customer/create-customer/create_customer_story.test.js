/**
 * Epic: Create Customer
 * Orders: 0.0.0
 */

import { background, scenario, story } from "../../story-test.js";
import { enteredValidAccountCredentials } from "./examples";

/**
 * Story: Create Customer
 */

// background-examples: {"enteredValidAccountCredentials": {}}
story('Create Customer', () => {
  // typescript body to translate:
  // let createSpy: MockInstance<typeof portalGateway.create>;
  // let updateAttributesSpy: MockInstance<typeof amplifyService.updateUserAttributes>;
  // beforeEach(() => {
  //   createSpy = vi.spyOn(portalGateway, 'create');
  //   updateAttributesSpy = vi.spyOn(amplifyService, 'updateUserAttributes');
  // });
  background('each', ({ given }) => {
    given('the User has a verified account with an account token', () => {
      // typescript body to translate:
      // const cognitoUser = amplifyService.seedCognitoUser(new CognitoUser(
      //   enteredValidAccountCredentials.email,
      //   true,
      //   null,
      //   new AccountToken(enteredValidAccountCredentials.email, null, `token:${enteredValidAccountCredentials.email}`),
      // ));
      // accountCredentials = accountRepository.newAccount(new AccountCredentials(
      //   enteredValidAccountCredentials.email,
      //   enteredValidAccountCredentials.password,
      //   enteredValidAccountCredentials.confirmPassword,
      //   enteredValidAccountCredentials.validationCode,
      //   cognitoUser.confirmed,
      //   cognitoUser,
      // ));
      // TODO: implement step
    });
  });
  scenario('Create customer', ({ given, when, then }) => {
    // typescript body to translate:
    // let result: Customer;
    // examples: enteredValidAccountCredentials
    when('the User creates their Paradise account', async () => {
      // typescript body to translate:
      // result = await customerRepository.create(accountCredentials);
      // TODO: implement step
    });
    then('My Paradise sends the correct create request to Mavenir', () => {
      // typescript body to translate:
      // expect(createSpy).toHaveBeenCalledWith(mavenirCreateRequest(enteredValidAccountCredentials.email));
      // TODO: implement step
    });
    when('Mavenir creates the customer', async () => {
      // typescript body to translate:
      // result = await customerRepository.load(accountCredentials);
      // TODO: implement step
    });
    then('the customer has a Mavenir customer id', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Customer);
      // expect(result.id).toBe('cus_1');
      // TODO: implement step
    })
      .and('My Paradise stores the customer id on the Cognito user', () => {
        // typescript body to translate:
        // expect(updateAttributesSpy).toHaveBeenCalledWith({ userAttributes: { 'custom:customerId': 'cus_1' } });
        // TODO: implement step
      });
  });

  scenario('Mavenir customer already exists', ({ given, when, then }) => {
    // typescript body to translate:
    // let caughtError: unknown;
    // examples: enteredValidAccountCredentials
    given('Mavenir already has a customer for that email', () => {
      // typescript body to translate:
      // portalGateway.seedCustomer(enteredValidAccountCredentials.email);
      // TODO: implement step
    });
    when('the User creates their Paradise account', async () => {
      // typescript body to translate:
      // try { await customerRepository.create(accountCredentials); } catch (e) { caughtError = e; }
      // TODO: implement step
    });
    then('My Paradise shows Could not create customer', () => {
      // typescript body to translate:
      // expect(caughtError).toHaveProperty('message', 'Could not create customer.');
      // TODO: implement step
    });
  });
});
