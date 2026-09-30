from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Create Empty Cart

# Story: Ensure Cart on Customer
with story("Ensure Cart on Customer"):
    with background.each:
        with scenario("Load Cart — no cart"):
            with given("the Customer enters the onboarding journey with a valid account token and no cart"):
                pass
            with when("My Paradise loads the cart for the customer"):
                pass
            with then("My Paradise finds no cart on the customer"):
                pass
        with scenario("Create Cart"):
            with given("the Customer enters the onboarding journey with a valid account token and no cart"):
                pass
            with when("My Paradise creates a cart for the customer"):
                pass
            with then("My Paradise sends the create request to Midtier with the customer id"):
                pass
            with when("Mavenir creates the shopping cart"):
                pass
            with then("My Paradise stores the cart on the customer"):
                pass
            with and_("the Customer proceeds to Get Number"):
                pass
        with scenario("customer already has a Mavenir shopping cart"):
            with given("the Customer enters the onboarding journey with a valid account token"):
                pass
            with and_("the customer has a Mavenir shopping cart"):
                pass
            with when("My Paradise loads the cart for the customer"):
                pass
            with then("My Paradise finds the cart on the customer"):
                pass
            with and_("the Customer proceeds to Get Number"):
                pass
        with scenario("cart already exists"):
            with given("the Customer enters the onboarding journey and already has a cart loaded"):
                pass
            with when("My Paradise creates a cart for the customer"):
                pass
            with then("My Paradise reports a cart creation error"):
                pass
