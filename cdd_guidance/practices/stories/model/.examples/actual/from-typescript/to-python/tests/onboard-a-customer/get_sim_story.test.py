from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Sim
# Orders: 0.0.6

# Story: Choose Esim
with story("Choose Esim"):
        with scenario("Choose eSIM"):
            with given("no SIM type is on the line"):
                pass
            with when("the Customer selects eSIM"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with SIM type eSIM"):
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with SIM type eSIM"):
                pass
            with then("My Paradise stores eSIM on the line"):
                pass
            with but_("the line has no ICCID"):
                pass
            with and_("the Customer is forwarded to Verify ID"):
                pass
        with scenario("Choose eSIM — already on the line"):
            with given("the line already has SIM type eSIM"):
                pass
            with when("the Customer selects eSIM"):
                pass
            with then("My Paradise skips the cart patch"):
                pass
        with scenario("Choose eSIM — cart patch fails"):
            with given("Mavenir returns an error on cart patch"):
                pass
            with when("the Customer selects eSIM"):
                pass
            with then("the SIM selection fails"):
                pass
            with when("My Paradise reloads the shopping cart"):
                pass
            with then("the line has no SIM type"):
                pass
            with and_("the line has no ICCID"):
                pass

# Story: Request a Paradise Sim Card
with story("Request a Paradise Sim Card"):
        with scenario("Request a Paradise SIM card"):
            with given("no SIM type is on the line and no ICCID is on the line"):
                pass
            with when("the Customer requests a Paradise SIM card"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with SIM type pSIM"):
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with SIM type pSIM"):
                pass
            with then("My Paradise stores pSIM on the line"):
                pass
            with but_("the line has no ICCID"):
                pass
            with and_("the Customer is forwarded to Verify ID"):
                pass
        with scenario("Request a Paradise SIM card — already on the line"):
            with given("the line already has SIM type pSIM"):
                pass
            with when("the Customer requests a Paradise SIM card"):
                pass
            with then("My Paradise skips the cart patch"):
                pass
        with scenario("Request a Paradise SIM card — cart patch fails"):
            with given("Mavenir returns an error on cart patch"):
                pass
            with when("the Customer requests a Paradise SIM card"):
                pass
            with then("the SIM selection fails"):
                pass
            with when("My Paradise reloads the shopping cart"):
                pass
            with then("the line has no SIM type"):
                pass
            with and_("the line has no ICCID"):
                pass

# Story: Enter Existing Sim
with story("Enter Existing Sim"):
        with scenario("Enter existing SIM"):
            with given("Mavenir has valid ICCID available in inventory"):
                pass
            with when("the Customer attaches valid ICCID"):
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with valid ICCID"):
                pass
            with and_("My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID"):
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID"):
                pass
            with then("My Paradise stores pSIM and valid ICCID on the line"):
                pass
            with and_("the line has valid ICCID"):
                pass
            with and_("the Customer is forwarded to Verify ID"):
                pass
        with scenario("ICCID contains spaces"):
            with given("the Customer has ICCID with spaces"):
                pass
            with when("the Customer attaches ICCID with spaces"):
                pass
            with then("the ICCID format is rejected"):
                pass
            with and_("My Paradise does not query inventory or patch the cart"):
                pass
        with scenario("Inventory rejects ICCID"):
            with given("Mavenir does not have invalid ICCID available in inventory"):
                pass
            with when("the Customer attaches invalid ICCID"):
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID"):
                pass
            with and_("My Paradise does not patch the cart"):
                pass
            with and_("the ICCID is rejected"):
                pass

# Story: Activate Sim
with story("Activate Sim"):
        with scenario("Activate Sim"):
            with given("Mavenir has valid ICCID available in inventory"):
                pass
            with when("the Customer activates the SIM with valid ICCID"):
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with valid ICCID"):
                pass
            with and_("My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID"):
                pass
            with and_("My Paradise sends the pSIM delivered order to Mavenir"):
                pass
            with when("Mavenir creates the product order and clears waiting pSIM"):
                pass
            with then("My Paradise stores valid ICCID on the line"):
                pass
        with scenario("waiting pSIM is absent"):
            with given("Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic"):
                pass
            with when("the Customer activates the SIM with valid ICCID"):
                pass
            with then("the pSIM delivered order is rejected"):
                pass
        with scenario("waiting pSIM already completed"):
            with given("Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false"):
                pass
            with when("the Customer activates the SIM with valid ICCID"):
                pass
            with then("the pSIM delivered order is rejected"):
                pass
