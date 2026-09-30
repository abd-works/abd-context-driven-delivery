from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser, enteredInvalidEmailFormat, enteredValidAccountCredentials, storedUnconfirmedCognitoUser


# Epic: Sign In With Existing Account
# Orders: 0.0.10

# Story: Sign In With Existing Account
with story("Sign In With Existing Account"):
        with scenario("Sign in with already-registered account credentials"):
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                pass
            with and_("the Customer is not signed in"):
                pass
            with and_("the Customer has already-registered account credentials"):
                pass
            with when("the Customer authenticates already-registered account credentials"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito authenticates the account and issues an account token"):
                pass
            with then("My Paradise stores the signed-in Cognito user"):
                pass
            with and_("the Cognito user has the Mavenir customer id"):
                pass
        with scenario("Email format is unmet"):
            # examples: enteredInvalidEmailFormat
            with given("the Customer has invalid email format account credentials"):
                pass
            with when("the Customer authenticates invalid email format"):
                pass
            with then("My Paradise does not send a sign-in request to Cognito"):
                pass
            with and_("the authentication is rejected"):
                pass
            with and_("Cognito does not issue an account token"):
                pass
        with scenario("Authenticate with unconfirmed account"):
            # examples: enteredValidAccountCredentials, storedUnconfirmedCognitoUser
            with given("Cognito has an unconfirmed Cognito user"):
                pass
            with and_("the Customer is not signed in"):
                pass
            with and_("the Customer has unconfirmed sign-in account credentials"):
                pass
            with when("the Customer authenticates unconfirmed sign-in"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns CONFIRM_SIGN_UP"):
                pass
            with then("the authentication is rejected as unconfirmed"):
                pass
            with and_("Cognito does not issue an account token"):
                pass
        with scenario("Password reset required"):
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                pass
            with and_("Cognito requires a password reset for already-registered account credentials"):
                pass
            with and_("the Customer is not signed in"):
                pass
            with and_("the Customer has already-registered account credentials"):
                pass
            with when("the Customer authenticates already-registered account credentials"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns PasswordResetRequiredException"):
                pass
            with then("the authentication requires a password reset"):
                pass
            with and_("Cognito does not issue an account token"):
                pass
        with scenario("New password required"):
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredCognitoUser
            with given("Cognito has an already-registered Cognito user"):
                pass
            with and_("Cognito requires a new password for already-registered account credentials"):
                pass
            with and_("the Customer is not signed in"):
                pass
            with and_("the Customer has already-registered account credentials"):
                pass
            with when("the Customer authenticates already-registered account credentials"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED"):
                pass
            with then("the authentication requires a new password"):
                pass
            with and_("Cognito does not issue an account token"):
                pass
