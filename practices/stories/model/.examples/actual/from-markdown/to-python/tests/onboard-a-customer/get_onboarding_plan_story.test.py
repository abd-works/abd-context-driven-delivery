from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Onboarding Plan

# Story: Query Product Offerings And Map To Catalog
with story("Query Product Offerings And Map To Catalog"):
    with background.each:
        with scenario("Query Product Offerings And Map To Catalog"):
            with given("Mavenir has returned product offerings for service provider 100000000"):
                pass
            with when("Midtier is asked to query product offerings and map to catalog"):
                pass
            with then("Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++"):
                pass
            with and_("strips \"PROMO\" from ++plan++ ++Internal Test Plan PROMO++ name"):
                pass
            with and_("marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable"):
                pass
            with and_("marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable"):
                pass
            with and_("tags ++plan++ ++Ace++ as \"Best value\""):
                pass
            with and_("returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan"):
                pass

# Story: List Product Offerings
with story("List Product Offerings"):
    with background.each:
        with scenario("List Product Offerings"):
            with given("Mavenir catalog for service provider 100000000 is reachable"):
                pass
            with when("Mavenir is asked to list product offerings with channelName CRM"):
                pass
            with then("Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering"):
                pass

# Story: Choose Onboarding Plan
# Actor: Customer
with story("Choose Onboarding Plan"):
    with background.each:
        with scenario("Choose Onboarding Plan"):
            with then("no ++plan++ is in the ++Mavenir shopping cart++"):
                pass
            with and_("Keep current plan is not shown"):
                pass
            with when("the Prospect is forwarded to Plan Selection"):
                pass
            with then("the system retrieves the ++plan++ catalog from the Midtier"):
                pass
            with and_("the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++"):
                pass
            with and_("each ++plan++ has a Select operation"):
                pass
            with when("the Prospect clicks Select on ++plan++ ++{scenario}++"):
                pass
            with then("the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier"):
                pass
            with and_("the ++My Paradise customer++ cart is updated in session with ++{scenario}++"):
                pass
            with and_("the Prospect is forwarded to Time to pick your number"):
                pass
        with scenario("Choose a different ++plan++"):
            with given("++plan++ ++Essentials++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Prospect arrives at Plan Selection from Checkout"):
                pass
            with then("the Prospect sees \"Your current plan Essentials\""):
                pass
            with and_("Keep current plan is enabled"):
                pass
            with and_("the ++plan++ catalog is displayed"):
                pass
            with and_("each ++plan++ has a Select operation"):
                pass
            with when("the Prospect clicks Select on ++plan++ ++Data Freedom++"):
                pass
            with then("the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier"):
                pass
            with and_("the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++"):
                pass
            with and_("the Prospect is forwarded to Checkout"):
                pass
        with scenario("Select the ++plan++ already in the cart"):
            with given("++plan++ ++Essentials++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Prospect clicks Select on ++plan++ ++Essentials++"):
                pass
            with then("the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan"):
                pass
        with scenario("Failed to update plan"):
            with given("Midtier PATCH to ++Mavenir shopping cart++ returns a server error"):
                pass
            with when("the Prospect clicks Select on ++plan++ ++Data Freedom++"):
                pass
            with then("My Paradise shows \"Failed to update new plan choice.\""):
                pass
            with and_("the Prospect stays on Plan Selection"):
                pass

# Story: Patch Cart With Plan
with story("Patch Cart With Plan"):
    with background.each:
        with scenario("Patch Cart With Plan"):
            with given("a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir"):
                pass
            with when("Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++"):
                pass
            with then("Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir"):
                pass
            with and_("builds the cart item payload with the bundle product offering"):
                pass
            with and_("patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart"):
                pass
            with and_("returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan"):
                pass
        with scenario("Patch Cart With Plan — portability plan name updated"):
            with given("a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir"):
                pass
            with when("Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected \"Data Freedom\""):
                pass
            with then("Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to \"Data Freedom\""):
                pass
            with and_("patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart"):
                pass
            with and_("returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName"):
                pass

# Story: Patch Shopping Cart
with story("Patch Shopping Cart"):
    with background.each:
        with scenario("Patch shopping cart with portability"):
            with given("a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++"):
                pass
            with when("Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics"):
                pass
            with then("Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)"):
                pass
            with and_("Mavenir returns the updated ++Mavenir shopping cart++ to Midtier"):
                pass
        with scenario("Patch shopping cart with MSISDN"):
            with given("a ++Mavenir shopping cart++ with a plan bundle cart item"):
                pass
            with and_("no MSISDN characteristic on the cart item"):
                pass
            with when("Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic"):
                pass
            with then("Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic"):
                pass
            with and_("Mavenir returns the updated ++Mavenir shopping cart++ to Midtier"):
                pass
        with scenario("Patch Shopping Cart"):
            with given("a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir"):
                pass
            with when("Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++"):
                pass
            with then("Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item"):
                pass
            with and_("returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan"):
                pass

# Story: Keep Current Plan
with story("Keep Current Plan"):
    with background.each:
        with scenario("Keep Current Plan"):
            with when("the Prospect clicks Keep current plan"):
                pass
            with then("the Prospect is forwarded to Checkout"):
                pass
