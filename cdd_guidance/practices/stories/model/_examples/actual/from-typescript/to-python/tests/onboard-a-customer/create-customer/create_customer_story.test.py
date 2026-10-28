from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidAccountCredentials


# Epic: Create Customer
# Orders: 0.0.0

# Story: Create Customer
with story("Create Customer"):
    with background.each:
        with given("the User has a verified account with an account token"):
            pass
        with scenario("Create customer"):
            # examples: enteredValidAccountCredentials
            with when("the User creates their Paradise account"):
                pass
            with then("My Paradise sends the correct create request to Mavenir"):
                pass
            with when("Mavenir creates the customer"):
                pass
            with then("the customer has a Mavenir customer id"):
                pass
            with and_("My Paradise stores the customer id on the Cognito user"):
                pass
        with scenario("Mavenir customer already exists"):
            # examples: enteredValidAccountCredentials
            with given("Mavenir already has a customer for that email"):
                pass
            with when("the User creates their Paradise account"):
                pass
            with then("My Paradise shows Could not create customer"):
                pass
