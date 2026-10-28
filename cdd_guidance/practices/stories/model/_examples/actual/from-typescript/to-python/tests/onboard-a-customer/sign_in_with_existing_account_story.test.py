from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser, enteredInvalidEmailFormat, enteredValidAccountCredentials, storedUnconfirmedCognitoUser


# Epic: Sign In With Existing Account
# Orders: 0.0.10

# Story: Sign In With Existing Account
with story("Sign In With Existing Account"):
    # typescript body to translate:
    # let signInSpy: MockInstance<typeof amplifyService.signIn>;
    #
    # beforeEach(() => {
    #   signInSpy = vi.spyOn(amplifyService, 'signIn');
    # });
    #
    # incorrectCredentialOutlines.forEach(({ example, credentials }) => {
    # });
        with scenario("Sign in with already-registered account credentials"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(
                #   storedAlreadyRegisteredCognitoUser,
                #   enteredAlreadyRegisteredAccountCredentials.password,
                # );
                pass
            with and_("the Customer is not signed in"):
                # typescript body to translate:
                # await amplifyService.signOut();
                pass
            with and_("the Customer has already-registered account credentials"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(
                #   new AccountCredentials(
                #     storedAlreadyRegisteredCognitoUser,
                #     enteredAlreadyRegisteredAccountCredentials.password,
                #   ),
                # );
                pass
            with when("the Customer authenticates already-registered account credentials"):
                # typescript body to translate:
                # await accountCredentials.authenticateAccount();
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                # typescript body to translate:
                # expect(signInSpy).toHaveBeenCalledWith({
                #   username: enteredAlreadyRegisteredAccountCredentials.email,
                #   password: enteredAlreadyRegisteredAccountCredentials.password,
                # });
                pass
            with when("Cognito authenticates the account and issues an account token"):
                pass
            with then("My Paradise stores the signed-in Cognito user"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeInstanceOf(AccountToken);
                # expect(accountCredentials.token).toMatchObject({
                #   email: enteredAlreadyRegisteredAccountCredentials.email,
                #   customerId: storedAlreadyRegisteredCognitoUser.customerId,
                # });
                pass
            with and_("the Cognito user has the Mavenir customer id"):
                # typescript body to translate:
                # expect(accountCredentials.customerId).toBe(storedAlreadyRegisteredCognitoUser.customerId);
                pass
        with scenario("Email format is unmet"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # let caughtError: unknown;
            # examples: enteredInvalidEmailFormat
            with given("the Customer has invalid email format account credentials"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(enteredInvalidEmailFormat);
                pass
            with when("the Customer authenticates invalid email format"):
                # typescript body to translate:
                # try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
                pass
            with then("My Paradise does not send a sign-in request to Cognito"):
                # typescript body to translate:
                # expect(signInSpy).not.toHaveBeenCalled();
                pass
            with and_("the authentication is rejected"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('signIn', 'Account credential requirements are unmet');
                pass
            with and_("Cognito does not issue an account token"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeNull();
                pass
        with scenario("Authenticate with incorrect account credentials: ${example}"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # let caughtError: unknown;
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(
                #   storedAlreadyRegisteredCognitoUser,
                #   enteredAlreadyRegisteredAccountCredentials.password,
                # );
                pass
            with and_("the Customer is not signed in"):
                # typescript body to translate:
                # await amplifyService.signOut();
                pass
            with and_("the Customer has ${example}"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(credentials);
                pass
            with when("the Customer authenticates ${example}"):
                # typescript body to translate:
                # try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                # typescript body to translate:
                # expect(signInSpy).toHaveBeenCalledWith({
                #   username: credentials.email,
                #   password: credentials.password,
                # });
                pass
            with when("Cognito returns NotAuthorizedException"):
                pass
            with then("the authentication is rejected"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('signIn', SignInFailure.NotAuthorized);
                pass
            with and_("Cognito does not issue an account token"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeNull();
                pass
        with scenario("Authenticate with unconfirmed account"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # let caughtError: unknown;
            # examples: enteredValidAccountCredentials, storedUnconfirmedCognitoUser
            with given("Cognito has an unconfirmed Cognito user"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(
                #   storedUnconfirmedCognitoUser,
                #   enteredValidAccountCredentials.password,
                # );
                pass
            with and_("the Customer is not signed in"):
                # typescript body to translate:
                # await amplifyService.signOut();
                pass
            with and_("the Customer has unconfirmed sign-in account credentials"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(
                #   new AccountCredentials(storedUnconfirmedCognitoUser, enteredValidAccountCredentials.password),
                # );
                pass
            with when("the Customer authenticates unconfirmed sign-in"):
                # typescript body to translate:
                # try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                # typescript body to translate:
                # expect(signInSpy).toHaveBeenCalledWith({
                #   username: enteredValidAccountCredentials.email,
                #   password: enteredValidAccountCredentials.password,
                # });
                pass
            with when("Cognito returns CONFIRM_SIGN_UP"):
                pass
            with then("the authentication is rejected as unconfirmed"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('signIn', SignInStep.ConfirmSignUp);
                pass
            with and_("Cognito does not issue an account token"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeNull();
                pass
        with scenario("Password reset required"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # let caughtError: unknown;
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(
                #   storedAlreadyRegisteredCognitoUser,
                #   enteredAlreadyRegisteredAccountCredentials.password,
                # );
                pass
            with and_("Cognito requires a password reset for already-registered account credentials"):
                # typescript body to translate:
                # amplifyService.seedSignInError(
                #   enteredAlreadyRegisteredAccountCredentials.email,
                #   namedError(SignInFailure.PasswordResetRequired),
                # );
                pass
            with and_("the Customer is not signed in"):
                # typescript body to translate:
                # await amplifyService.signOut();
                pass
            with and_("the Customer has already-registered account credentials"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(
                #   new AccountCredentials(
                #     storedAlreadyRegisteredCognitoUser,
                #     enteredAlreadyRegisteredAccountCredentials.password,
                #   ),
                # );
                pass
            with when("the Customer authenticates already-registered account credentials"):
                # typescript body to translate:
                # try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                # typescript body to translate:
                # expect(signInSpy).toHaveBeenCalledWith({
                #   username: enteredAlreadyRegisteredAccountCredentials.email,
                #   password: enteredAlreadyRegisteredAccountCredentials.password,
                # });
                pass
            with when("Cognito returns PasswordResetRequiredException"):
                pass
            with then("the authentication requires a password reset"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('signIn', SignInFailure.PasswordResetRequired);
                pass
            with and_("Cognito does not issue an account token"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeNull();
                pass
        with scenario("New password required"):
            # typescript body to translate:
            # let accountCredentials: AccountCredentials;
            # let caughtError: unknown;
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                # typescript body to translate:
                # amplifyService.seedCognitoUser(
                #   storedAlreadyRegisteredCognitoUser,
                #   enteredAlreadyRegisteredAccountCredentials.password,
                # );
                pass
            with and_("Cognito requires a new password for already-registered account credentials"):
                # typescript body to translate:
                # amplifyService.seedSignInNextStep(
                #   enteredAlreadyRegisteredAccountCredentials.email,
                #   SignInStep.NewPasswordRequired,
                # );
                pass
            with and_("the Customer is not signed in"):
                # typescript body to translate:
                # await amplifyService.signOut();
                pass
            with and_("the Customer has already-registered account credentials"):
                # typescript body to translate:
                # accountCredentials = accountRepository.newAccount(
                #   new AccountCredentials(
                #     storedAlreadyRegisteredCognitoUser,
                #     enteredAlreadyRegisteredAccountCredentials.password,
                #   ),
                # );
                pass
            with when("the Customer authenticates already-registered account credentials"):
                # typescript body to translate:
                # try { await accountCredentials.authenticateAccount(); } catch (e) { caughtError = e; }
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                # typescript body to translate:
                # expect(signInSpy).toHaveBeenCalledWith({
                #   username: enteredAlreadyRegisteredAccountCredentials.email,
                #   password: enteredAlreadyRegisteredAccountCredentials.password,
                # });
                pass
            with when("Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED"):
                pass
            with then("the authentication requires a new password"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('signIn', SignInStep.NewPasswordRequired);
                pass
            with and_("Cognito does not issue an account token"):
                # typescript body to translate:
                # expect(accountCredentials.token).toBeNull();
                pass
