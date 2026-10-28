from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidAccountCredentials, storedAccountCredentialsWithToken


# Epic: Load Customer
# Orders: 0.0.0.2

# Story: Load My Paradise Customer From Midtier And Store In Session
# background-examples: {"enteredValidAccountCredentials": {}, "storedAccountCredentialsWithToken": {}}
with story("Load My Paradise Customer From Midtier And Store In Session"):
    # typescript body to translate:
    # let readSpy: MockInstance<typeof portalGateway.read>;
    #
    # beforeEach(() => {
    #   readSpy = vi.spyOn(portalGateway, 'read');
    # });
    with background.each:
        with given("Mavenir has a customer and the Cognito user holds its id"):
            # typescript body to translate:
            # const mavenirCustomer = portalGateway.seedCustomer(enteredValidAccountCredentials.email);
            # accountCredentials = storedAccountCredentialsWithToken(mavenirCustomer.id);
            pass
        with scenario("Load My Paradise Customer From Midtier And Store In Session"):
            # typescript body to translate:
            # let customer: Customer;
            # examples: enteredValidAccountCredentials
            with when("My Paradise loads the customer through Midtier"):
                # typescript body to translate:
                # customer = await customerRepository.load(accountCredentials);
                pass
            with then("My Paradise calls Midtier with the correct customer id"):
                # typescript body to translate:
                # expect(readSpy).toHaveBeenCalledWith(accountCredentials.customerId);
                pass
            with and_("Midtier maps the Mavenir contact medium to Paradise identity and address"):
                # typescript body to translate:
                # expect(customer).toBeInstanceOf(Customer);
                # expect(customer).toHaveProperty('id', accountCredentials.customerId);
                # expect(customer).toHaveProperty('identity.email', enteredValidAccountCredentials.email);
                # expect(customer).toHaveProperty('address.street', '');
                pass
        with scenario("Load customer fails"):
            # typescript body to translate:
            # let exception!: CustomerException;
            with given("Mavenir no longer has that customer"):
                # typescript body to translate:
                # portalGateway.mavenirCustomers.splice(0);
                pass
            with when("My Paradise loads the customer"):
                # typescript body to translate:
                # try {
                #   await customerRepository.load(accountCredentials);
                # } catch (error) {
                #   if (!(error instanceof CustomerException)) throw error;
                #   exception = error;
                # }
                pass
            with then("My Paradise signs the User out"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeNull();
                pass
            with and_("My Paradise shows Something went wrong when loading your account"):
                # typescript body to translate:
                # expect(exception).toMatchObject({
                #   operation: 'load',
                #   message: 'Something went wrong when loading your account',
                #   cause: new Error('Mavenir customer not found'),
                # });
                pass
        with scenario("Terminated account"):
            # typescript body to translate:
            # let accountCredentials = storedAccountCredentialsWithToken('cus_1');
            # let exception!: CustomerException;
            # examples: storedAccountCredentialsWithToken
            with given("the Customer has an account token"):
                # typescript body to translate:
                # accountCredentials = storedAccountCredentialsWithToken('cus_1');
                # portalGateway.seedCustomerById('cus_1', accountCredentials.email ?? '');
                pass
            with and_("the Mavenir customer billing state is terminated"):
                # typescript body to translate:
                # portalGateway.seedBilling('cus_1', 'bill_cus_1', BillingState.Terminated);
                pass
            with when("My Paradise loads the customer"):
                # typescript body to translate:
                # try {
                #   await customerRepository.load(accountCredentials);
                # } catch (error) {
                #   if (!(error instanceof CustomerException)) throw error;
                #   exception = error;
                # }
                pass
            with then("My Paradise signs the Customer out"):
                # typescript body to translate:
                # expect(readSpy).toHaveBeenCalledWith('cus_1');
                # expect(accountCredentials.token).toBeNull();
                pass
            with and_("the Customer account is terminated"):
                # typescript body to translate:
                # expect(exception).toMatchObject({
                #   operation: 'load',
                #   message: 'Your account has been terminated.',
                #   cause: new Error('Billing account is terminated'),
                # });
                pass
