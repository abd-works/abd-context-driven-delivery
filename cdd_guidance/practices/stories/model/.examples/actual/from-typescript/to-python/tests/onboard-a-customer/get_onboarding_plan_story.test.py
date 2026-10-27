from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Onboarding Plan
# Orders: 0.0.2

# Story: Load Plan Catalog
with story("Load Plan Catalog"):
        with scenario("Load plan catalog"):
            with given("the plan catalog is available"):
                pass
            with when("My Paradise loads the plan catalog"):
                pass
            with then("the catalog includes Essentials, Data Freedom, Ace, and Atlas"):
                pass
            with and_("Internal Test Plan PROMO is excluded from the catalog"):
                pass

# Story: Choose Onboarding Plan
with story("Choose Onboarding Plan"):
        with scenario("Select a plan"):
            with given("no plan is in the Mavenir shopping cart"):
                pass
            with when("the Customer selects Essentials"):
                pass
            with then("My Paradise patches the Mavenir cart with the Essentials planId"):
                pass
            with and_("the Customer is forwarded to Pick Number"):
                pass
            with when("Mavenir confirms the cart is patched with Essentials"):
                pass
            with then("the cart bundle is a snapshot of Essentials loaded from the gateway"):
                pass
        with scenario("Change an existing plan"):
            with given("Essentials is in the Mavenir shopping cart"):
                pass
            with when("the Customer selects Data Freedom"):
                pass
            with then("My Paradise patches the Mavenir cart with the Data Freedom planId"):
                pass
            with when("Mavenir confirms the cart is patched with Data Freedom"):
                pass
            with then("the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway"):
                pass
        with scenario("Failed to update plan"):
            with given("the Mavenir cart patch returns an error"):
                pass
            with when("the Customer selects Essentials"):
                pass
            with then("the plan selection fails"):
                pass
            with when("My Paradise reloads the shopping cart"):
                pass
            with then("the cart bundle remains empty"):
                pass
