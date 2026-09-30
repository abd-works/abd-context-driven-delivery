from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Place Order
# Orders: 0.0.9

# Story: Create Billing Account
with story("Create Billing Account"):
        with scenario("Create billing account"):
            with given("the Customer has a configured cart and no billing account"):
                pass
            with when("the Customer creates a billing account"):
                pass
            with then("My Paradise sends the billing account request to Mavenir"):
                pass
            with when("Mavenir creates the billing account"):
                pass
            with then("the Customer has a billing account"):
                pass
            with and_("the Customer is on the Done step"):
                pass
        with scenario("Billing account already exists"):
            with given("the Customer already has a billing account"):
                pass
            with when("the Customer creates a billing account"):
                pass
            with then("the billing account is rejected"):
                pass
            with and_("Mavenir does not receive a billing account request"):
                pass
        with scenario("Billing account creation fails"):
            with given("Mavenir returns an error for the billing account request"):
                pass
            with when("the Customer creates a billing account"):
                pass
            with then("the billing account cannot be created"):
                pass
            with when("My Paradise reloads the customer"):
                pass
            with then("the Customer has no billing account"):
                pass

# Story: Create Product Order
with story("Create Product Order"):
        with scenario("Create product order"):
            with given("the Customer is verified and has a billing account, plan, number, and eSIM"):
                pass
            with when("the Customer places the product order"):
                pass
            with then("My Paradise sends the product order request to Mavenir"):
                pass
            with when("Mavenir creates the product order"):
                pass
            with then("the order succeeded with pay-up-front"):
                pass
            with and_("the Customer onboarding is done"):
                pass
        with scenario("Pay-up-front charge fails"):
            with given("the pay-up-front charge fails"):
                pass
            with when("the Customer places the product order"):
                pass
            with then("My Paradise does not send a product order to Mavenir"):
                pass
            with when("My Paradise reloads the cart"):
                pass
            with then("the order succeeded without pay-up-front"):
                pass
        with scenario("Product order fails"):
            with given("Mavenir returns an error for the product order"):
                pass
            with when("the Customer places the product order"):
                pass
            with then("My Paradise sends the product order request to Mavenir"):
                pass
            with when("My Paradise reloads the cart"):
                pass
            with then("the order did not succeed"):
                pass
        with scenario("Onboarding is already done"):
            with given("the Customer onboarding is already done"):
                pass
            with when("the Customer places the product order"):
                pass
            with then("the product order is rejected"):
                pass
            with and_("Mavenir does not receive a product order request"):
                pass
        with scenario("Unverified with no bypass and no portability"):
            with given("the Customer is not verified and the plan does not bypass verification"):
                pass
            with when("the Customer places the product order"):
                pass
            with then("My Paradise does not send a product order to Mavenir"):
                pass
            with and_("the cart is marked to submit the order later"):
                pass
            with when("My Paradise reloads the cart"):
                pass
            with then("the Customer onboarding is done"):
                pass
