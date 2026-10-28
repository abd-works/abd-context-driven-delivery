from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Order Review
# Orders: 0.0.6

# Story: Check The Order
# Actor: Customer
with story("Check The Order"):
        with scenario("Check the order"):
            # background: background
            # background-step: Given | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
            # background-step: And | ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
            # background-step: And | the Customer has chosen eSIM
            with given("the Customer has completed account setup, number, SIM, and profile"):
                pass
            with when("the Customer proceeds to reviewing their order"):
                pass
            with then("the Customer is forwarded to Checkout"):
                pass
            with and_("the Checkout step is the next onboarding step"):
                pass
        with scenario("Check the order with port-in number"):
            # background: background
            # background-step: Given | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
            # background-step: And | ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
            # background-step: And | the Customer has chosen eSIM
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
# background-examples: {"upgrade to Data Freedom": {"plan upgrade": "plan upgrade", "example": "upgrade to Data Freedom", "currentPlan": "Essentials", "newPlan": "Data Freedom"}, "upgrade to Ace": {"plan upgrade": "plan upgrade", "example": "upgrade to Ace", "currentPlan": "Data Freedom", "newPlan": "Ace"}, "upgrade to Atlas": {"plan upgrade": "plan upgrade", "example": "upgrade to Atlas", "currentPlan": "Ace", "newPlan": "Atlas"}}
with story("Upgrade To Data Freedom"):
    with background.background:
        with scenario("Upgrade plan from review"):
            # background: background
            # background-step: Given | the Customer is reviewing their order
            # background-step: And | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++
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
            # background: background
            # background-step: Given | the Customer is reviewing their order
            # background-step: And | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++
            with given("++plan++ ++Atlas++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Customer proceeds to reviewing their order"):
                pass
            with then("no upgrade option is available"):
                pass

# Story: Change Plan From Review
# Actor: Customer
with story("Change Plan From Review"):
        with scenario("Select a different plan from review"):
            # background: background
            # background-step: Given | the Customer is reviewing their order
            # background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
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
            # background: background
            # background-step: Given | the Customer is reviewing their order
            # background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
            with given("the Customer has opened plan selection from review"):
                pass
            with when("the Customer keeps their current plan"):
                pass
            with then("the Customer is forwarded to Checkout"):
                pass
        with scenario("Select the plan already in the cart from review"):
            # background: background
            # background-step: Given | the Customer is reviewing their order
            # background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
            with given("the Customer has opened plan selection from review"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++"):
                pass
            with then("the cart bundle remains ++plan++ ++Essentials++"):
                pass
        with scenario("Plan update fails from review"):
            # background: background
            # background-step: Given | the Customer is reviewing their order
            # background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
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
