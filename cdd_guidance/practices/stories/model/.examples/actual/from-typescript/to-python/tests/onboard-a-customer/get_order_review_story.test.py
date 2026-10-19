from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Order Review
# Orders: 0.0.3

# Story: Change Plan From Review
with story("Change Plan From Review"):
        with scenario("Select a different plan from review"):
            with given("the Customer has opened plan selection from review with Essentials in the cart"):
                pass
            with when("My Paradise patches the Mavenir shopping cart with Data Freedom"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId"):
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with Data Freedom"):
                pass
            with then("My Paradise stores Data Freedom as the cart bundle loaded from the gateway"):
                pass
            with and_("the Customer is forwarded to Checkout"):
                pass
        with scenario("Keep current plan from review"):
            with given("the Customer has opened plan selection from review with Essentials in the cart"):
                pass
            with when("the Customer keeps their current plan"):
                pass
            with then("the cart bundle remains Essentials"):
                pass
            with and_("the Customer is forwarded to Checkout"):
                pass
        with scenario("Plan update fails from review"):
            with given("the Customer has opened plan selection from review with Essentials in the cart"):
                pass
            with when("My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error"):
                pass
            with then("My Paradise shows Failed to update new plan choice."):
                pass
            with when("My Paradise reloads the shopping cart"):
                pass
            with then("the cart bundle remains Essentials"):
                pass
