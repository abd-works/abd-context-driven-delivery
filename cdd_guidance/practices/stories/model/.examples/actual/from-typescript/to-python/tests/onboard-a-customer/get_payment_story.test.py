from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Payment
# Orders: 0.0.4

# Story: Enter Payment
with story("Enter Payment"):
        with scenario("Enter Payment"):
            with given("the Customer is at Checkout with Essentials"):
                pass
            with and_("Mavenir CCS authorizes stub auth"):
                pass
            with when("the Customer proceeds to adding their payment"):
                pass
            with then("My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING"):
                pass
            with when("Mavenir authorizes the card and returns the hosted payment page"):
                pass
            with then("the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING"):
                pass
        with scenario("Payment authorization fails to load"):
            with given("the Customer is at Checkout with Essentials"):
                pass
            with but_("Mavenir CCS does not return a payment authorization"):
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
            with given("the Customer is at Checkout with Essentials"):
                pass
            with but_("Mavenir does not return a transaction id"):
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
with story("Authorize Card"):
        with scenario("Payment completed"):
            with given("the Customer has stub auth"):
                pass
            with and_("Mavenir CCS has completed auth"):
                pass
            with when("the Customer authorizes their card"):
                pass
            with then("My Paradise sends the tokenized card request to Mavenir for stub auth"):
                pass
            with when("Mavenir returns completed auth"):
                pass
            with then("the payment is authorized"):
                pass
            with and_("the payment step does not place the order"):
                pass
        with scenario("Card not verified"):
            with given("the Customer has stub auth"):
                pass
            with and_("Mavenir CCS has failed auth"):
                pass
            with and_("payment attempts are under the maximum"):
                pass
            with when("the Customer authorizes their card"):
                pass
            with then("My Paradise sends the tokenized card request to Mavenir"):
                pass
            with when("Mavenir returns failed auth"):
                pass
            with then("the card is not verified"):
                pass
            with and_("My Paradise requests a fresh payment authorization from Mavenir"):
                pass
        with scenario("Maximum payment attempts"):
            with given("the Customer has stub auth"):
                pass
            with and_("Mavenir CCS has failed auth"):
                pass
            with and_("payment attempts equal the maximum"):
                pass
            with when("the Customer authorizes their card"):
                pass
            with then("My Paradise sends the tokenized card request to Mavenir for stub auth"):
                pass
            with when("Mavenir returns failed auth"):
                pass
            with then("My Paradise records the failed card addition with Zendesk"):
                pass
            with and_("the payment step does not place the order"):
                pass

# Story: Provide Apple Pay Certificate
with story("Provide Apple Pay Certificate"):
        with scenario("Provide Apple Pay certificate"):
            with given("the Apple Pay merchant certificate is available"):
                pass
            with when("My Paradise provides the Apple Pay certificate"):
                pass
            with then("My Paradise sends the certificate request to Apple"):
                pass
            with when("Apple returns Bermuda Apple Pay cert"):
                pass
            with then("My Paradise returns Bermuda Apple Pay cert"):
                pass
