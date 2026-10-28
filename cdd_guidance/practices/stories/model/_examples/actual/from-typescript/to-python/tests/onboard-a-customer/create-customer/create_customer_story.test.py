from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidAccountCredentials


# Epic: Create Customer
# Orders: 0.0.0

# Story: Create Customer
# background-examples: {"enteredValidAccountCredentials": {}}
with story("Create Customer"):
    # typescript body to translate:
    # let createSpy: MockInstance<typeof portalGateway.create>;
    # let updateAttributesSpy: MockInstance<typeof amplifyService.updateUserAttributes>;
    # beforeEach(() => {
    #   createSpy = vi.spyOn(portalGateway, 'create');
    #   updateAttributesSpy = vi.spyOn(amplifyService, 'updateUserAttributes');
    # });
    with background.each:
        with given("the User has a verified account with an account token"):
            # typescript body to translate:
            # const cognitoUser = amplifyService.seedCognitoUser(new CognitoUser(
            #   enteredValidAccountCredentials.email,
            #   true,
            #   null,
            #   new AccountToken(enteredValidAccountCredentials.email, null, `token:${enteredValidAccountCredentials.email}`),
            # ));
            # accountCredentials = accountRepository.newAccount(new AccountCredentials(
            #   enteredValidAccountCredentials.email,
            #   enteredValidAccountCredentials.password,
            #   enteredValidAccountCredentials.confirmPassword,
            #   enteredValidAccountCredentials.validationCode,
            #   cognitoUser.confirmed,
            #   cognitoUser,
            # ));
            pass
        with scenario("Create customer"):
            # typescript body to translate:
            # let result: Customer;
            # examples: enteredValidAccountCredentials
            with when("the User creates their Paradise account"):
                # typescript body to translate:
                # result = await customerRepository.create(accountCredentials);
                pass
            with then("My Paradise sends the correct create request to Mavenir"):
                # typescript body to translate:
                # expect(createSpy).toHaveBeenCalledWith(mavenirCreateRequest(enteredValidAccountCredentials.email));
                pass
            with when("Mavenir creates the customer"):
                # typescript body to translate:
                # result = await customerRepository.load(accountCredentials);
                pass
            with then("the customer has a Mavenir customer id"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Customer);
                # expect(result.id).toBe('cus_1');
                pass
            with and_("My Paradise stores the customer id on the Cognito user"):
                # typescript body to translate:
                # expect(updateAttributesSpy).toHaveBeenCalledWith({ userAttributes: { 'custom:customerId': 'cus_1' } });
                pass
        with scenario("Mavenir customer already exists"):
            # typescript body to translate:
            # let caughtError: unknown;
            # examples: enteredValidAccountCredentials
            with given("Mavenir already has a customer for that email"):
                # typescript body to translate:
                # portalGateway.seedCustomer(enteredValidAccountCredentials.email);
                pass
            with when("the User creates their Paradise account"):
                # typescript body to translate:
                # try { await customerRepository.create(accountCredentials); } catch (e) { caughtError = e; }
                pass
            with then("My Paradise shows Could not create customer"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('message', 'Could not create customer.');
                pass
