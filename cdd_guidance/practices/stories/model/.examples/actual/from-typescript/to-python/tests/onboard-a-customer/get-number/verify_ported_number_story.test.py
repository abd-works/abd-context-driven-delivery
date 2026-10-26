from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidPortability, validPortingSmscode, customerWithCartAndPortability, mismatchPortingSmscode


# Epic: Verify Ported Number
# Orders: 0.0.1.2

# Story: Check Port Verification
with story("Check Port Verification"):
        with scenario("Enter porting SMS code"):
            # examples: enteredValidPortability, validPortingSmscode, customerWithCartAndPortability
            with given("the Customer submitted portability and Twilio sent an SMS to the port number"):
                pass
            with and_("Twilio is ready to confirm the SMS code as valid"):
                pass
            with then("My Paradise sends the verification check to Twilio with the port number and code"):
                pass
            with when("Twilio creates a verification check (verificationChecks.create)"):
                pass
            with then("Twilio returns approved and the Customer is forwarded to Select Sim"):
                pass
        with scenario("Verify with unusable porting SMS code"):
            # examples: enteredValidPortability, mismatchPortingSmscode, customerWithCartAndPortability
            with given("the Customer submitted portability and has an incorrect verification code"):
                pass
            with then("My Paradise sends the verification check to Twilio"):
                pass
            with when("Twilio creates a verification check and returns a non-approved status"):
                pass
            with then("the verification is rejected"):
                pass
        with scenario("Resend porting SMS code"):
            # examples: enteredValidPortability, customerWithCartAndPortability
            with given("the Customer submitted portability and Twilio sent an SMS to the port number"):
                pass
            with when("the Customer requests a new verification code"):
                pass
            with then("My Paradise SMSes a porting verification code via Twilio"):
                pass
            with when("Twilio sends the SMS verification"):
                pass
            with then("the resend is confirmed"):
                pass
