from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Enter Porting Number

# Story: Submit Portability Request
with story("Submit Portability Request"):
    with background.each:
        with scenario("Port the number"):
            with given("a My Paradise customer with a Mavenir shopping cart"):
                pass
            with when("the Customer enters valid portability and ports their number"):
                pass
            with and_("Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number"):
                pass
            with then("the Customer is forwarded to Verify Ported Number"):
                pass
        with scenario("Port the number — SMS verification skipped"):
            with given("a My Paradise customer with a Mavenir shopping cart"):
                pass
            with and_("Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send"):
                pass
            with when("the Customer enters valid portability and ports their number"):
                pass
            with and_("Mavenir processes the portability request and Twilio rate-limits the SMS send"):
                pass
            with then("portability is stored on the line with verification skipped"):
                pass
            with and_("the Customer is forwarded to Select Sim — no verification step required"):
                pass
