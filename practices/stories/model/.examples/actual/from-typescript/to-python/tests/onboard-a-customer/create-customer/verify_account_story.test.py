from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Verify Account

# Story: Enter Validation Code
with story("Enter Validation Code"):
    with background.each:
        with given("the User has submitted valid account credentials"):
            pass
        with and_("Cognito has an unconfirmed Cognito user"):
            pass
        with and_("Cognito has sent a validation code to the User"):
            pass
        with and_("the User has account credentials with valid email and password"):
            pass
        with scenario("Enter validation code"):
            with when("the User activates the account with the emailed validation code"):
                pass
            with then("My Paradise sends the correct confirmation request to Cognito"):
                pass
            with and_("the account is verified"):
                pass
            with and_("Cognito issues an account token for the browser session"):
                pass
            with and_("no Mavenir customer exists for those account credentials"):
                pass
        with scenario("Resend validation code"):
            with when("more than 60 seconds has passed"):
                pass
            with and_("the User resends the validation code"):
                pass
            with then("Cognito sends a new validation code"):
                pass
            with and_("My Paradise shows the resend confirmation"):
                pass
            with when("less than 60 seconds has passed"):
                pass
            with and_("the User resends the validation code"):
                pass
            with then("Resend waits 60 seconds before it can be used again"):
                pass
            with and_("Cognito does not send another validation code during the wait"):
                pass
            with when("more than 60 seconds has passed"):
                pass
            with and_("the User resends the validation code"):
                pass
            with then("Cognito sends another validation code"):
                pass
