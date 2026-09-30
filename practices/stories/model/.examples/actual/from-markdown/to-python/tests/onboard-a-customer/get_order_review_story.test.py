from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Order Review

# Story: Check The Order
# Actor: Customer
with story("Check The Order"):
    with background.each:
        with scenario("Check the order"):
            with given("the Customer has completed account setup, number, SIM, and profile"):
                pass
            with when("the Customer proceeds to reviewing their order"):
                pass
            with then("the Customer is forwarded to Checkout"):
                pass
            with and_("the Checkout step is the next onboarding step"):
                pass
        with scenario("Check the order with port-in number"):
            with given("the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN"):
                pass
            with when("the Customer proceeds to reviewing their order"):
                pass
            with then("the Customer is forwarded to Checkout"):
                pass
            with and_("the Checkout step is the next onboarding step"):
                pass

# Story: Upgrade To Data Freedom
# Actor: Customer
with story("Upgrade To Data Freedom"):
    with background.each:
        with scenario("Upgrade plan from review"):
            with given("++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId"):
                pass
            with when("Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++"):
                pass
            with then("My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle"):
                pass
            with and_("the Customer sees *You have been upgraded!*"):
                pass
        with scenario("No upsell shown on top-tier plan"):
            with given("++plan++ ++Atlas++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Customer proceeds to reviewing their order"):
                pass
            with then("no upgrade option is available"):
                pass

# Story: Change Plan From Review
# Actor: Customer
with story("Change Plan From Review"):
    with background.each:
        with scenario("Select a different plan from review"):
            with given("the Customer has opened plan selection from review"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId"):
                pass
            with when("Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++"):
                pass
            with then("My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle"):
                pass
            with and_("the Customer is forwarded to Checkout"):
                pass
        with scenario("Keep current plan from review"):
            with given("the Customer has opened plan selection from review"):
                pass
            with when("the Customer keeps their current plan"):
                pass
            with then("the Customer is forwarded to Checkout"):
                pass
        with scenario("Select the plan already in the cart from review"):
            with given("the Customer has opened plan selection from review"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++"):
                pass
            with then("the cart bundle remains ++plan++ ++Essentials++"):
                pass
        with scenario("Plan update fails from review"):
            with given("the Customer has opened plan selection from review"):
                pass
            with and_("Mavenir returns an error on cart patch"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++"):
                pass
            with then("My Paradise shows *Failed to update new plan choice.*"):
                pass
            with and_("the cart bundle remains ++plan++ ++Essentials++"):
                pass
