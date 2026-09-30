from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Place Order

# Story: Create Billing Account
# Actor: My Paradise
with story("Create Billing Account"):
    with background.each:
        with scenario("Create billing account"):
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
            with and_("the Customer has no billing account"):
                pass

# Story: Create Product Order
# Actor: My Paradise
with story("Create Product Order"):
    with background.each:
        with scenario("Create product order"):
            with given("the Customer is verified"):
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
            with and_("the order succeeded without pay-up-front"):
                pass
        with scenario("Product order fails"):
            with given("Mavenir returns an error for the product order"):
                pass
            with when("the Customer places the product order"):
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
            with given("the Customer is not verified"):
                pass
            with and_("the plan does not bypass verification"):
                pass
            with and_("the cart has no portability"):
                pass
            with when("the Customer places the product order"):
                pass
            with then("My Paradise does not send a product order to Mavenir"):
                pass
            with and_("the cart is marked to submit the order later"):
                pass
            with and_("the Customer onboarding is done"):
                pass

# Story: View Order Result
# Actor: Customer
with story("View Order Result"):
    with background.each:
        with scenario("View order result"):
            with given("the order result is {example}"):
                pass
            with when("the Customer views their order result"):
                pass
            with then("the order is {outcome}"):
                pass

# Story: Create Order Ticket
# Actor: My Paradise
with story("Create Order Ticket"):
    with background.each:
        with scenario("Create order ticket"):
            with given("the Customer {example}"):
                pass
            with when("the Customer creates the order ticket"):
                pass
            with then("My Paradise sends the {subject} ticket to Zendesk"):
                pass
            with when("Zendesk creates the ticket"):
                pass
            with then("the ticket is created for the Customer"):
                pass

# Story: View Order History
# Actor: Care
with story("View Order History"):
    with background.each:
        with scenario("View Order History"):
            with when("Care views Order History for the Customer"):
                pass
            with then("Care sees the product order with status badges"):
                pass
