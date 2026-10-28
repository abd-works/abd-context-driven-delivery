/**
 * Epic: Load Customer
 * Orders: 0.0.0.2
 */

import { background, scenario, story } from "../../story-test.js";
import { enteredValidAccountCredentials, storedAccountCredentialsWithToken } from "./examples";

/**
 * Story: Load My Paradise Customer From Midtier And Store In Session
 */

// background-examples: {"enteredValidAccountCredentials": {}, "storedAccountCredentialsWithToken": {}}
story('Load My Paradise Customer From Midtier And Store In Session', () => {
  // typescript body to translate:
  // let readSpy: MockInstance<typeof portalGateway.read>;
  //
  // beforeEach(() => {
  //   readSpy = vi.spyOn(portalGateway, 'read');
  // });
  background('each', ({ given }) => {
    given('Mavenir has a customer and the Cognito user holds its id', () => {
      // typescript body to translate:
      // const mavenirCustomer = portalGateway.seedCustomer(enteredValidAccountCredentials.email);
      // accountCredentials = storedAccountCredentialsWithToken(mavenirCustomer.id);
      // TODO: implement step
    });
  });
  scenario('Load My Paradise Customer From Midtier And Store In Session', ({ given, when, then }) => {
    // typescript body to translate:
    // let customer: Customer;
    // examples: enteredValidAccountCredentials
    when('My Paradise loads the customer through Midtier', async () => {
      // typescript body to translate:
      // customer = await customerRepository.load(accountCredentials);
      // TODO: implement step
    });
    then('My Paradise calls Midtier with the correct customer id', () => {
      // typescript body to translate:
      // expect(readSpy).toHaveBeenCalledWith(accountCredentials.customerId);
      // TODO: implement step
    })
      .and('Midtier maps the Mavenir contact medium to Paradise identity and address', () => {
        // typescript body to translate:
        // expect(customer).toBeInstanceOf(Customer);
        // expect(customer).toHaveProperty('id', accountCredentials.customerId);
        // expect(customer).toHaveProperty('identity.email', enteredValidAccountCredentials.email);
        // expect(customer).toHaveProperty('address.street', '');
        // TODO: implement step
      });
  });

  scenario('Load customer fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let exception!: CustomerException;
    given('Mavenir no longer has that customer', () => {
      // typescript body to translate:
      // portalGateway.mavenirCustomers.splice(0);
      // TODO: implement step
    });
    when('My Paradise loads the customer', async () => {
      // typescript body to translate:
      // try {
      //   await customerRepository.load(accountCredentials);
      // } catch (error) {
      //   if (!(error instanceof CustomerException)) throw error;
      //   exception = error;
      // }
      // TODO: implement step
    });
    then('My Paradise signs the User out', () => {
      // typescript body to translate:
      // expect(accountCredentials.token).toBeNull();
      // TODO: implement step
    })
      .and('My Paradise shows Something went wrong when loading your account', () => {
        // typescript body to translate:
        // expect(exception).toMatchObject({
        //   operation: 'load',
        //   message: 'Something went wrong when loading your account',
        //   cause: new Error('Mavenir customer not found'),
        // });
        // TODO: implement step
      });
  });

  scenario('Terminated account', ({ given, when, then }) => {
    // typescript body to translate:
    // let accountCredentials = storedAccountCredentialsWithToken('cus_1');
    // let exception!: CustomerException;
    // examples: storedAccountCredentialsWithToken
    given('the Customer has an account token', () => {
      // typescript body to translate:
      // accountCredentials = storedAccountCredentialsWithToken('cus_1');
      // portalGateway.seedCustomerById('cus_1', accountCredentials.email ?? '');
      // TODO: implement step
    })
      .and('the Mavenir customer billing state is terminated', () => {
        // typescript body to translate:
        // portalGateway.seedBilling('cus_1', 'bill_cus_1', BillingState.Terminated);
        // TODO: implement step
      });
    when('My Paradise loads the customer', async () => {
      // typescript body to translate:
      // try {
      //   await customerRepository.load(accountCredentials);
      // } catch (error) {
      //   if (!(error instanceof CustomerException)) throw error;
      //   exception = error;
      // }
      // TODO: implement step
    });
    then('My Paradise signs the Customer out', () => {
      // typescript body to translate:
      // expect(readSpy).toHaveBeenCalledWith('cus_1');
      // expect(accountCredentials.token).toBeNull();
      // TODO: implement step
    })
      .and('the Customer account is terminated', () => {
        // typescript body to translate:
        // expect(exception).toMatchObject({
        //   operation: 'load',
        //   message: 'Your account has been terminated.',
        //   cause: new Error('Billing account is terminated'),
        // });
        // TODO: implement step
      });
  });
});
