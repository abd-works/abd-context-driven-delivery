from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Sim

# Story: Choose Esim
# Actor: Customer
with story("Choose Esim"):
    with background.each:
        with scenario("Choose eSIM"):
            with given("no ++SIM type++ is on the line"):
                pass
            with when("the Customer selects eSIM"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM"):
                pass
            with when("Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM"):
                pass
            with then("My Paradise stores eSIM on the line"):
                pass
            with and_("the Customer is forwarded to Verify ID"):
                pass
        with scenario("Choose eSIM — already on the line"):
            with given("the line already has ++SIM type++ eSIM"):
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
            with and_("the line has no ++SIM type++"):
                pass

# Story: Request a Paradise Sim Card
# Actor: Customer
with story("Request a Paradise Sim Card"):
    with background.each:
        with scenario("Request a Paradise SIM card"):
            with given("no ++SIM type++ is on the line"):
                pass
            with and_("no ++ICCID++ is on the line"):
                pass
            with when("the Customer requests a Paradise SIM card"):
                pass
            with then("My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM"):
                pass
            with when("Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM"):
                pass
            with then("My Paradise stores pSIM on the line"):
                pass
            with and_("the line has no ++ICCID++"):
                pass
            with and_("the Customer is forwarded to Verify ID"):
                pass
        with scenario("Request a Paradise SIM card — already on the line"):
            with given("the line already has ++SIM type++ pSIM"):
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
            with and_("the line has no ++SIM type++"):
                pass

# Story: Enter Existing Sim
# Actor: Customer
with story("Enter Existing Sim"):
    with background.each:
        with scenario("Enter existing SIM"):
            with given("Mavenir has ++ICCID++ ++valid ICCID++ available in inventory"):
                pass
            with when("the Customer attaches ++ICCID++ ++valid ICCID++"):
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++"):
                pass
            with and_("My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++"):
                pass
            with when("Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++"):
                pass
            with then("My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line"):
                pass
            with and_("the Customer is forwarded to Verify ID"):
                pass
        with scenario("ICCID contains spaces"):
            with given("the Customer has ++ICCID++ ++ICCID with spaces++"):
                pass
            with when("the Customer attaches ++ICCID++ ++ICCID with spaces++"):
                pass
            with then("the ICCID format is rejected"):
                pass
            with and_("My Paradise does not query inventory or patch the cart"):
                pass
        with scenario("Inventory rejects ICCID"):
            with given("Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory"):
                pass
            with when("the Customer attaches ++ICCID++ ++invalid ICCID++"):
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++"):
                pass
            with and_("My Paradise does not patch the cart"):
                pass
            with and_("the ICCID is rejected"):
                pass

# Story: Activate Sim
# Actor: Customer
with story("Activate Sim"):
    with background.each:
        with scenario("Activate Sim"):
            with given("Mavenir has ++ICCID++ ++valid ICCID++ available in inventory"):
                pass
            with when("the Customer activates the SIM with ++ICCID++ ++valid ICCID++"):
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++"):
                pass
            with and_("My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++"):
                pass
            with and_("My Paradise sends the pSIM delivered order to Mavenir"):
                pass
            with when("Mavenir creates the product order and clears ++waiting pSIM++"):
                pass
            with then("My Paradise stores ++ICCID++ ++valid ICCID++ on the line"):
                pass
        with scenario("waiting pSIM is absent"):
            with given("Mavenir has ++ICCID++ ++valid ICCID++ available in inventory"):
                pass
            with and_("the ++Mavenir customer++ has no ++waiting pSIM++ characteristic"):
                pass
            with when("the Customer activates the SIM with ++ICCID++ ++valid ICCID++"):
                pass
            with then("the pSIM delivered order is rejected"):
                pass
        with scenario("waiting pSIM already completed"):
            with given("Mavenir has ++ICCID++ ++valid ICCID++ available in inventory"):
                pass
            with and_("the ++Mavenir customer++ has ++waiting pSIM++ Cleared"):
                pass
            with when("the Customer activates the SIM with ++ICCID++ ++valid ICCID++"):
                pass
            with then("the pSIM delivered order is rejected"):
                pass

# Story: Complete Draft Sim Order
with story("Complete Draft Sim Order"):
    with background.each:
        with scenario("Complete Draft Sim Order"):
            with given("Care opens the ++Mavenir customer++ record in Mavenir DEP"):
                pass
            with and_("Care sees the draft order in the orders grid (`22-dep-orders-grid.png`)"):
                pass
            with when("Care attaches the ++ICCID++ to the draft order and completes it"):
                pass
            with then("the order status in DEP Order History changes from draft to active (`23-dep-order-history.png`)"):
                pass
            with and_("the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared"):
                pass
