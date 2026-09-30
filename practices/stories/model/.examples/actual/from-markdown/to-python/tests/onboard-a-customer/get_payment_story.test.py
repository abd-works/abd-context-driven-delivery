from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Payment

# Story: Enter Payment
# Actor: Customer
with story("Enter Payment"):
    with background.each:
        with scenario("Enter Payment"):
            with given("`payUpFront` is off"):
                pass
            with and_("Mavenir CCS authorizes ++payment authorization++ ++stub auth++"):
                pass
            with when("the Customer proceeds to adding their payment"):
                pass
            with then("My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING"):
                pass
            with when("Mavenir authorizes the card and returns the hosted payment page"):
                pass
            with then("My Paradise stores ++payment authorization++ ++stub auth++"):
                pass
        with scenario("Pay upfront"):
            with given("`payUpFront` is on"):
                pass
            with and_("the cart has ++plan++ ++Essentials++"):
                pass
            with and_("Mavenir CCS authorizes ++payment authorization++ ++stub auth++"):
                pass
            with when("the Customer proceeds to adding their payment"):
                pass
            with then("My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING"):
                pass
            with when("Mavenir authorizes the card and returns the hosted payment page"):
                pass
            with then("My Paradise stores ++payment authorization++ ++stub auth++"):
                pass
        with scenario("Payment authorization fails to load"):
            with given("`payUpFront` is off"):
                pass
            with and_("Mavenir CCS does not return a payment authorization"):
                pass
            with when("the Customer proceeds to adding their payment"):
                pass
            with then("My Paradise sends the card authorization request to Mavenir"):
                pass
            with when("Mavenir does not return a payment authorization"):
                pass
            with then("the payment authorization cannot be loaded"):
                pass
        with scenario("FAC authorization timeout"):
            with given("`payUpFront` is off"):
                pass
            with and_("Mavenir does not return a transaction id"):
                pass
            with when("the Customer proceeds to adding their payment"):
                pass
            with then("My Paradise sends the card authorization request to Mavenir"):
                pass
            with when("Mavenir does not return a transaction id"):
                pass
            with then("the payment authorization cannot be loaded"):
                pass

# Story: Authorize Card
# Actor: My Paradise
with story("Authorize Card"):
    with background.each:
        with scenario("Payment completed"):
            with given("the Customer has ++payment authorization++ ++stub auth++"):
                pass
            with and_("Mavenir CCS has ++payment status++ ++completed auth++"):
                pass
            with when("the Customer authorizes their card"):
                pass
            with then("My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++"):
                pass
            with when("Mavenir returns ++payment status++ ++completed auth++"):
                pass
            with then("the payment is authorized"):
                pass
            with and_("the payment step does not place the order"):
                pass
        with scenario("Card not verified"):
            with given("the Customer has ++payment authorization++ ++stub auth++"):
                pass
            with and_("Mavenir CCS has ++payment status++ ++failed auth++"):
                pass
            with and_("payment attempts are under the maximum"):
                pass
            with when("the Customer authorizes their card"):
                pass
            with then("My Paradise sends the tokenized card request to Mavenir"):
                pass
            with when("Mavenir returns ++payment status++ ++failed auth++"):
                pass
            with then("the card is not verified"):
                pass
            with and_("My Paradise requests a fresh payment authorization from Mavenir"):
                pass
        with scenario("Maximum payment attempts"):
            with given("the Customer has ++payment authorization++ ++stub auth++"):
                pass
            with and_("Mavenir CCS has ++payment status++ ++failed auth++"):
                pass
            with and_("payment attempts equal the maximum"):
                pass
            with when("the Customer authorizes their card"):
                pass
            with then("My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++"):
                pass
            with when("Mavenir returns ++payment status++ ++failed auth++"):
                pass
            with then("My Paradise records the failed card addition with Zendesk"):
                pass
            with and_("the payment step does not place the order"):
                pass

# Story: Provide Apple Pay Certificate
# Actor: My Paradise
with story("Provide Apple Pay Certificate"):
    with background.each:
        with scenario("Provide Apple Pay certificate"):
            with given("the Apple Pay merchant certificate is available"):
                pass
            with when("My Paradise provides the Apple Pay certificate"):
                pass
            with then("My Paradise sends the certificate request to Apple"):
                pass
            with when("Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++"):
                pass
            with then("My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++"):
                pass

# Story: Adjust Credit Manually
# Actor: Care
with story("Adjust Credit Manually"):
    with background.each:
        with scenario("Adjust credit for pay-upfront or voucher"):
            with given("the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++"):
                pass
            with and_("the ++Mavenir customer++ has completed onboarding in My Paradise"):
                pass
            with and_("the credit adjustment was not applied after checkout"):
                pass
            with when("the Care agent manually adjusts the credit amount in Mavenir DEP"):
                pass
            with then("the ++Mavenir customer++ billing account is credited the adjustment amount"):
                pass
