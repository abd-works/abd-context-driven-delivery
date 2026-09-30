import { beforeEach, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { background, scenario, story } from 'stories/story-test';
import {
  AccountCredentials,
  Customer,
  CustomerException,
  customerRepository,
} from '../../../domain/customer/Customer';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { BillingState } from '../../../domain/billing/Billing';
import { enteredValidAccountCredentials, storedAccountCredentialsWithToken } from '../examples/account-credentials.examples';

story('Load My Paradise Customer From Midtier And Store In Session', () => {
  let readSpy: MockInstance<typeof portalGateway.read>;

  beforeEach(() => {
    readSpy = vi.spyOn(portalGateway, 'read');
  });

  background('each', ({ given }) => {
    let accountCredentials: AccountCredentials;

    given('Mavenir has a customer and the Cognito user holds its id', () => {
      const mavenirCustomer = portalGateway.seedCustomer(enteredValidAccountCredentials.email);
      accountCredentials = storedAccountCredentialsWithToken(mavenirCustomer.id);
    });

    scenario('Load My Paradise Customer From Midtier And Store In Session', ({ when, then }) => {
      let customer: Customer;

      when('My Paradise loads the customer through Midtier', async () => {
        customer = await customerRepository.load(accountCredentials);
      });
      then('My Paradise calls Midtier with the correct customer id', () => {
        expect(readSpy).toHaveBeenCalledWith(accountCredentials.customerId);
      })
        .and('Midtier maps the Mavenir contact medium to Paradise identity and address', () => {
          expect(customer).toBeInstanceOf(Customer);
          expect(customer).toHaveProperty('id', accountCredentials.customerId);
          expect(customer).toHaveProperty('identity.email', enteredValidAccountCredentials.email);
          expect(customer).toHaveProperty('address.street', '');
        });
    });

    scenario('Load customer fails', ({ given, when, then }) => {
      let exception!: CustomerException;

      given('Mavenir no longer has that customer', () => {
        portalGateway.mavenirCustomers.splice(0);
      });
      when('My Paradise loads the customer', async () => {
        try {
          await customerRepository.load(accountCredentials);
        } catch (error) {
          if (!(error instanceof CustomerException)) throw error;
          exception = error;
        }
      });
      then('My Paradise signs the User out', () => {
        expect(accountCredentials.token).toBeNull();
      })
        .and('My Paradise shows Something went wrong when loading your account', () => {
          expect(exception).toMatchObject({
            operation: 'load',
            message: 'Something went wrong when loading your account',
            cause: new Error('Mavenir customer not found'),
          });
        });
    });
  });

  scenario('Terminated account', ({ given, when, then }) => {
    let accountCredentials = storedAccountCredentialsWithToken('cus_1');
    let exception!: CustomerException;

    given('the Customer has an account token', () => {
      accountCredentials = storedAccountCredentialsWithToken('cus_1');
      portalGateway.seedCustomerById('cus_1', accountCredentials.email ?? '');
    }).and('the Mavenir customer billing state is terminated', () => {
      portalGateway.seedBilling('cus_1', 'bill_cus_1', BillingState.Terminated);
    });
    when('My Paradise loads the customer', async () => {
      try {
        await customerRepository.load(accountCredentials);
      } catch (error) {
        if (!(error instanceof CustomerException)) throw error;
        exception = error;
      }
    });
    then('My Paradise signs the Customer out', () => {
      expect(readSpy).toHaveBeenCalledWith('cus_1');
      expect(accountCredentials.token).toBeNull();
    }).and('the Customer account is terminated', () => {
      expect(exception).toMatchObject({
        operation: 'load',
        message: 'Your account has been terminated.',
        cause: new Error('Billing account is terminated'),
      });
    });
  });
});
