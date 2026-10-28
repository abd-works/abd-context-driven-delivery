from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidAccountCredentials


# Epic: Verify Account
# Orders: 0.0.0.3

# Story: Enter Validation Code
# background-examples: {"storedUnconfirmedCognitoUser": {}, "enteredValidAccountCredentials": {}, "unusableValidationCodeExamples": {}, "enteredValidValidationCode": {}}
with story("Enter Validation Code"):
    # typescript body to translate:
    # afterEach(() => vi.useRealTimers());
    #
    # let confirmSignUpSpy: MockInstance<typeof amplifyService.confirmSignUp>;
    # let signInSpy: MockInstance<typeof amplifyService.signIn>;
    # beforeEach(() => {
    #   confirmSignUpSpy = vi.spyOn(amplifyService, 'confirmSignUp');
    #   signInSpy = vi.spyOn(amplifyService, 'signIn');
    # });
    with background.each:
        with given("the User has submitted valid account credentials"):
            pass
        with and_("Cognito has an unconfirmed Cognito user"):
            # typescript body to translate:
            # amplifyService.seedCognitoUser(storedUnconfirmedCognitoUser);
            pass
        with and_("Cognito has sent a validation code to the User"):
            # typescript body to translate:
            # amplifyService.seedValidationCode(enteredValidAccountCredentials.email, enteredValidValidationCode);
            # emailedValidationCode = enteredValidValidationCode;
            pass
        with and_("the User has account credentials with valid email and password"):
            # typescript body to translate:
            # const cognitoUser = amplifyService.getUser(enteredValidAccountCredentials.email)!;
            # accountCredentials = accountRepository.newAccount(
            #   new AccountCredentials(cognitoUser, enteredValidAccountCredentials.password),
            # );
            pass
        with scenario("Enter validation code"):
            # examples: enteredValidAccountCredentials
            with when("the User activates the account with the emailed validation code"):
                # typescript body to translate:
                # await accountCredentials.activate(emailedValidationCode);
                pass
            with then("My Paradise sends the correct confirmation request to Cognito"):
                # typescript body to translate:
                # expect(confirmSignUpSpy).toHaveBeenCalledWith({
                #   username: enteredValidAccountCredentials.email,
                #   confirmationCode: emailedValidationCode.code,
                # });
                pass
            with and_("the account is verified"):
                # typescript body to translate:
                # expect(accountCredentials.verified).toBe(true);
                pass
            with and_("Cognito issues an account token for the browser session"):
                # typescript body to translate:
                # expect(signInSpy).toHaveBeenCalledWith({
                #   username: enteredValidAccountCredentials.email,
                #   password: enteredValidAccountCredentials.password,
                # });
                # expect(accountCredentials.token).toMatchObject({
                #   email: enteredValidAccountCredentials.email,
                #   customerId: null,
                # });
                pass
            with but_("no Mavenir customer exists for those account credentials"):
                # typescript body to translate:
                # expect(accountCredentials.customerId).toBeNull();
                pass
        with scenario("Activate with unusable validation code: ${example}"):
            # typescript body to translate:
            # let caughtError: unknown;
            with when("the User activates with ${example}"):
                # typescript body to translate:
                # try { await accountCredentials.activate(validationCode); } catch (e) { caughtError = e; }
                pass
            with then("Enter Validation Code shows ${helper}"):
                # typescript body to translate:
                # expect(caughtError).toHaveProperty('validationCode', helper);
                pass
        with scenario("Resend validation code"):
            # typescript body to translate:
            # let caughtError: unknown;
            with when("more than 60 seconds has passed"):
                # typescript body to translate:
                # vi.useFakeTimers();
                # vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 60_000));
                pass
            with and_("the User resends the validation code"):
                # typescript body to translate:
                # await accountCredentials.resendValidationCode();
                pass
            with then("Cognito sends a new validation code"):
                # typescript body to translate:
                # expect(amplifyService.validationCodeSendsFor(accountCredentials.email).at(-1)?.kind)
                #   .toBe('resend');
                pass
            with and_("My Paradise shows the resend confirmation"):
                # typescript body to translate:
                # expect(accountCredentials.resendMessage)
                #   .toBe('We sent you a new code. Please check your email.');
                pass
            with when("less than 60 seconds has passed"):
                # typescript body to translate:
                # vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 119_999));
                pass
            with and_("the User resends the validation code"):
                # typescript body to translate:
                # try { await accountCredentials.resendValidationCode(); } catch (e) { caughtError = e; }
                pass
            with then("Resend waits 60 seconds before it can be used again"):
                # typescript body to translate:
                # expect(caughtError).toBeInstanceOf(ValidationCodeResendWaitException);
                # expect((caughtError as ValidationCodeResendWaitException).availableAt)
                #   .toEqual(new Date(emailedValidationCode.sentAt.getTime() + 120_000));
                pass
            with and_("Cognito does not send another validation code during the wait"):
                # typescript body to translate:
                # expect(amplifyService.validationCodeSendsFor(accountCredentials.email))
                #   .toHaveLength(2);
                pass
            with when("more than 60 seconds has passed"):
                # typescript body to translate:
                # vi.setSystemTime(new Date(emailedValidationCode.sentAt.getTime() + 120_000));
                pass
            with and_("the User resends the validation code"):
                # typescript body to translate:
                # await accountCredentials.resendValidationCode();
                pass
            with then("Cognito sends another validation code"):
                # typescript body to translate:
                # expect(amplifyService.validationCodeSendsFor(accountCredentials.email))
                #   .toHaveLength(3);
                pass
