from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get New Number

# Story: Determine Number
with story("Determine Number"):
    with background.each:
        with scenario("View available numbers"):
            with given("a My Paradise customer with a Mavenir shopping cart and no MSISDN"):
                pass
            with when("the Customer loads available numbers"):
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                pass
            with when("Mavenir locks 20 MSISDN resources and returns the available number values"):
                pass
            with then("My Paradise returns the available numbers"):
                pass
        with scenario("View available numbers — MSISDN in cart"):
            with when("the Customer loads available numbers"):
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                pass
            with when("Mavenir locks 20 MSISDN resources and returns the available number values"):
                pass
            with and_("My Paradise returns the available numbers"):
                pass
        with scenario("Refresh available numbers"):
            with given("a My Paradise customer with a Mavenir shopping cart"):
                pass
            with when("the Customer refreshes the number list"):
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                pass
            with when("Mavenir locks 20 MSISDN resources and returns the available numbers"):
                pass
            with then("My Paradise returns a fresh set of available numbers"):
                pass
        with scenario("Search for a number"):
            with given("a My Paradise customer with a Mavenir shopping cart"):
                pass
            with when("the Customer searches for numbers matching JAMES (52637)"):
                pass
            with then("My Paradise sends the search request to Mavenir with pattern 52637"):
                pass
            with when("Mavenir locks MSISDN resources matching 52637 and returns matching values"):
                pass
            with then("My Paradise returns Available Numbers matching 52637"):
                pass
            with and_("the matching numbers are stored on the line for selection"):
                pass
        with scenario("Numbers locked by another customer are excluded from results"):
            with given("another customer has already locked the standard available numbers in Mavenir"):
                pass
            with when("the Customer loads available numbers"):
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                pass
            with when("Mavenir returns only available numbers, excluding the locked ones"):
                pass
            with then("the locked numbers are not in the available numbers list"):
                pass
            with and_("only the currently available numbers are returned"):
                pass
        with scenario("Pick number"):
            with when("Mavenir confirms the reservation and patches the cart"):
                pass
            with and_("the Customer is forwarded to Select Sim"):
                pass
        with scenario("Pick number — replace existing"):
            pass
        with scenario("Reserve number request fails"):
            with then("My Paradise shows Failed to reserve your number."):
                pass
        with scenario("Patch cart with number fails"):
            with then("My Paradise shows Failed to update your cart."):
                pass
