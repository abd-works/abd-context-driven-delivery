from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidAccountCredentials, enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser, expectedValidAccountCredentials


# Epic: Create Unconfirmed User
# Orders: 0.0.0.1

# Story: Create Unconfirmed Cognito User
with story("Create Unconfirmed Cognito User"):
        with scenario("Display Create Account"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            with when("the User proceeds to create an account from the Paradise Mobile website"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount();
                pass
            with then("the User can enter account credentials"):
                # typescript body to translate:
                # expect(accountCredentials.isUpdatable).toBe(true);
                pass
            with and_("the email and password rules are unmet"):
                # typescript body to translate:
                # const missing = accountCredentials.missingRequirements();
                # expect(missing).toContain(accountCredentials.requirements.emailRequired);
                # expect(missing).toContain(accountCredentials.requirements.passwordRequired);
                # expect(missing).toContain(accountCredentials.requirements.confirmRequired);
                pass
            with and_("the customer cannot save the customer account"):
                # typescript body to translate:
                # expect(accountCredentials.isPersistable).toBe(false);
                pass
        with scenario("Enter Valid account credentials"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # examples: enteredValidAccountCredentials
            with when("the User enters valid account credentials"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(enteredValidAccountCredentials);
                pass
            with then("account credentials are validated continuously"):
                # typescript body to translate:
                # expect(accountCredentials.missingRequirements()).toHaveLength(0);
                pass
            with and_("the customer can save the customer account"):
                # typescript body to translate:
                # expect(accountCredentials.isPersistable).toBe(true);
                pass
        with scenario("Enter Invalid account credentials: ${example}"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            with when("the User validates ${example}"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(credentials);
                pass
            with then("the ${unmet} requirement is unmet"):
                # typescript body to translate:
                # const missing = accountCredentials.missingRequirements();
                # const expectedRequirement = (accountCredentials.requirements as any)[unmet];
                # expect(missing).toContain(expectedRequirement);
                pass
            with and_("the customer cannot save the customer account"):
                # typescript body to translate:
                # expect(accountCredentials.isPersistable).toBe(false);
                pass
        with scenario("Email already registered"):
            # typescript body to translate:
            # let caughtError: unknown;
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
            with given("already-registered account credentials are already registered"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
                pass
            with when("the User registers already-registered account credentials"):
                # typescript body to translate:
                # const accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
                # try { await accountCredentials.register(); } catch (e) { caughtError = e; }
                pass
            with then("Email shows the already-registered error"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
                pass
        with scenario("Create Unconfirmed User"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # let amplifySignUpSpy: MockInstance<typeof amplifyService.signUp>;
            # examples: enteredValidAccountCredentials, expectedValidAccountCredentials
            with given("the amplifyService.signUp spy is set up"):
                # typescript body to translate:
                # amplifySignUpSpy = vi.spyOn(amplifyService, 'signUp');
                pass
            with when("the User creates their account"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(enteredValidAccountCredentials);
                # await accountCredentials.register();
                pass
            with then("the system creates an unconfirmed Cognito user and emails a validation code"):
                # typescript body to translate:
                # expect(amplifySignUpSpy).toHaveBeenCalledWith({
                #   username: expectedValidAccountCredentials.email,
                #   password: expectedValidAccountCredentials.password,
                #   options: { userAttributes: {
                #     email: expectedValidAccountCredentials.email,
                #     'custom:language': 'en',
                #     'custom:role': 'customer',
                #     'custom:serviceproviderId': '100000000',
                #   }},
                # });
                # expect(accountCredentials.verified).toBe(false);
                # expect(accountCredentials.token).toBeNull();
                # expect(accountCredentials.customerId).toBeNull();
                # expect(amplifyService.sentValidationCodesFor(expectedValidAccountCredentials.email)).toContain('123456');
                pass
        with scenario("Email already registered in Cognito"):
            # typescript body to translate:
            # let caughtError: unknown;
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
            with given("an unconfirmed Cognito user exists for already-registered account credentials"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(storedAlreadyRegisteredUnconfirmedCognitoUser);
                pass
            with when("Cognito is asked to register already-registered account credentials"):
                # typescript body to translate:
                # const accountCredentials = accountRepository.newAccount(enteredAlreadyRegisteredAccountCredentials);
                # try { await accountCredentials.register(); } catch (e) { caughtError = e; }
                pass
            with then("Cognito returns UsernameExistsException"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('register', 'UsernameExistsException');
                pass
            with and_("Cognito does not create another Cognito user"):
                pass
