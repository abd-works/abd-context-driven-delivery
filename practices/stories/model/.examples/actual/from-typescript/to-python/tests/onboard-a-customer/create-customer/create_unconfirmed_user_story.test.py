from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidAccountCredentials, enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser, expectedValidAccountCredentials


# Epic: Create Unconfirmed User
# Orders: 0.0.0.1

# Story: Create Unconfirmed Cognito User
with story("Create Unconfirmed Cognito User"):
        with scenario("Display Create Account"):
            with when("the User proceeds to create an account from the Paradise Mobile website"):
                pass
            with then("the User can enter account credentials"):
                pass
            with and_("the email and password rules are unmet"):
                pass
            with and_("the customer cannot save the customer account"):
                pass
        with scenario("Enter Valid account credentials"):
            # examples: enteredValidAccountCredentials
            with when("the User enters valid account credentials"):
                pass
            with then("account credentials are validated continuously"):
                pass
            with and_("the customer can save the customer account"):
                pass
        with scenario("Email already registered"):
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
            with given("already-registered account credentials are already registered"):
                pass
            with when("the User registers already-registered account credentials"):
                pass
            with then("Email shows the already-registered error"):
                pass
        with scenario("Create Unconfirmed User"):
            # examples: enteredValidAccountCredentials, expectedValidAccountCredentials
            with given("the amplifyService.signUp spy is set up"):
                pass
            with when("the User creates their account"):
                pass
            with then("the system creates an unconfirmed Cognito user and emails a validation code"):
                pass
        with scenario("Email already registered in Cognito"):
            # examples: enteredAlreadyRegisteredAccountCredentials, storedAlreadyRegisteredUnconfirmedCognitoUser
            with given("an unconfirmed Cognito user exists for already-registered account credentials"):
                pass
            with when("Cognito is asked to register already-registered account credentials"):
                pass
            with then("Cognito returns UsernameExistsException"):
                pass
            with and_("Cognito does not create another Cognito user"):
                pass
