from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Load Customer

# Story: Load My Paradise Customer From Midtier And Store In Session
with story("Load My Paradise Customer From Midtier And Store In Session"):
    with background.each:
        with given("Mavenir has a customer and the Cognito user holds its id"):
            pass
        with scenario("Load My Paradise Customer From Midtier And Store In Session"):
            with when("My Paradise loads the customer through Midtier"):
                pass
            with then("My Paradise calls Midtier with the correct customer id"):
                pass
            with and_("Midtier maps the Mavenir contact medium to Paradise identity and address"):
                pass
        with scenario("Load customer fails"):
            with given("Mavenir no longer has that customer"):
                pass
            with when("My Paradise loads the customer"):
                pass
            with then("My Paradise signs the User out"):
                pass
            with and_("My Paradise shows Something went wrong when loading your account"):
                pass
        with scenario("Terminated account"):
            with given("the Customer has an account token"):
                pass
            with and_("the Mavenir customer billing state is terminated"):
                pass
            with when("My Paradise loads the customer"):
                pass
            with then("My Paradise signs the Customer out"):
                pass
            with and_("the Customer account is terminated"):
                pass
