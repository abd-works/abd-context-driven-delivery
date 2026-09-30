from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Number

# Story: Determine Number
# Actor: Customer
with story("Determine Number"):
    with background.each:
        with scenario("View available numbers"):
            with then("no ++MSISDN++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Prospect proceeds to selecting their number"):
                pass
            with then("My Paradise loads ++available number++ inventory through the Midtier"):
                pass
            with and_("the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list"):
                pass
            with and_("the Prospect can Bring your mobile number"):
                pass
            with and_("the Prospect can search for numbers (up to 5 characters: letters or numbers)"):
                pass
            with and_("the Prospect can Refresh"):
                pass
            with and_("the Continue operation is disabled"):
                pass
            with when("the Prospect selects ++available number++ ++chosen available number++"):
                pass
            with then("the Continue operation is enabled"):
                pass
        with scenario("View available numbers — MSISDN in cart"):
            with given("++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Prospect proceeds to selecting their number"):
                pass
            with then("the Prospect sees their number is ++available number++ ++held available number++"):
                pass
            with and_("the Pick new number operation is disabled"):
                pass
            with and_("the Keep current number operation is enabled"):
                pass
            with when("the Prospect selects ++available number++ ++chosen available number++"):
                pass
            with then("the Pick new number operation is enabled"):
                pass
        with scenario("Refresh available numbers"):
            with when("the Prospect clicks Refresh"):
                pass
            with then("My Paradise loads a fresh set of ++available number++ through the Midtier"):
                pass
            with and_("the Prospect sees a new Available Number list"):
                pass
            with and_("the Continue operation is disabled"):
                pass
        with scenario("Search for a number"):
            with when("the Prospect enters ++search term++ ++James search++ in the search field"):
                pass
            with then("the search field helper shows *Your number: JAMES (52637)*"):
                pass
            with when("the Prospect triggers the search"):
                pass
            with then("My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier"):
                pass

# Story: Query Msisdn Inventory
with story("Query Msisdn Inventory"):
    with background.each:
        with scenario("Query MSISDN inventory for porting"):
            with given("a ++PML customer++ is authenticated in Midtier"):
                pass
            with and_("++portability++ is in the portability request"):
                pass
            with when("Midtier queries ++MSISDN++ inventory for a temporary port-in number (`count: 1`)"):
                pass
            with then("Midtier queries Mavenir for 1 available ++MSISDN++ resource"):
                pass
            with and_("Midtier receives ++available number++ ++held available number++ as the temporary number"):
                pass
        with scenario("Query MSISDN inventory"):
            with given("a ++PML customer++ is authenticated in Midtier"):
                pass
            with when("Midtier is asked to query ++MSISDN++ inventory"):
                pass
            with then("Midtier queries Mavenir for 5 available ++MSISDN++ resources"):
                pass
            with and_("Midtier returns a list of ++available number++ values to My Paradise"):
                pass

# Story: List Msisdn Resources
with story("List Msisdn Resources"):
    with background.each:
        with scenario("List MSISDN resources for porting"):
            with given("++MSISDN++ resources with available status are in the Mavenir inventory"):
                pass
            with when("Mavenir is asked to list 1 ++MSISDN++ resource (`/updateAndGetAvailableResources`, `size: 1`)"):
                pass
            with then("Mavenir transitions 1 ++MSISDN++ resource from available to locked"):
                pass
            with and_("Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier"):
                pass
        with scenario("List MSISDN resources"):
            with given("++MSISDN++ resources with available status are in the Mavenir inventory"):
                pass
            with when("Mavenir is asked to list ++MSISDN++ resources (`/updateAndGetAvailableResources`, `size: 5`)"):
                pass
            with then("Mavenir transitions 5 ++MSISDN++ resources from available to locked"):
                pass
            with and_("Mavenir returns the list of locked ++available number++ values to Midtier"):
                pass

# Story: Search Msisdn Inventory
with story("Search Msisdn Inventory"):
    with background.each:
        with scenario("Search MSISDN inventory"):
            with given("a ++PML customer++ is authenticated in Midtier"):
                pass
            with when("Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (`52637`)"):
                pass
            with then("Midtier queries Mavenir for available ++MSISDN++ resources matching `52637`"):
                pass
            with and_("Midtier returns matching ++available number++ values to My Paradise"):
                pass

# Story: Search Msisdn Resources
with story("Search Msisdn Resources"):
    with background.each:
        with scenario("Search MSISDN resources by pattern"):
            with given("++MSISDN++ resources with available status are in the Mavenir inventory"):
                pass
            with when("Mavenir is asked to search ++MSISDN++ resources with `pattern_search: 52637` (`/updateAndGetAvailableResources`)"):
                pass
            with then("Mavenir transitions matching ++MSISDN++ resources from available to locked"):
                pass
            with and_("Mavenir returns the matching ++available number++ values to Midtier"):
                pass

# Story: Choose a Number
# Actor: Customer
with story("Choose a Number"):
    with background.each:
        with scenario("Pick new number"):
            with given("the Prospect has selected ++available number++ ++chosen available number++"):
                pass
            with and_("no ++MSISDN++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Prospect clicks Continue"):
                pass
            with then("My Paradise reserves ++available number++ ++chosen available number++ through the Midtier"):
                pass
            with and_("My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Pick new number — replace existing"):
            with given("++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++"):
                pass
            with and_("the Prospect has selected ++available number++ ++chosen available number++"):
                pass
            with when("the Prospect clicks Pick new number"):
                pass
            with then("My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier"):
                pass
            with and_("My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Keep current number"):
            with given("++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++"):
                pass
            with when("the Prospect clicks Keep current number"):
                pass
            with then("the Prospect is forwarded to Select Sim"):
                pass

# Story: Submit Reserve Number Request to Mid-Tier
with story("Submit Reserve Number Request to Mid-Tier"):
    with background.each:
        with scenario("Reserve number"):
            with given("++available number++ ++chosen available number++ is selected"):
                pass
            with and_("no ++MSISDN++ is in the ++Mavenir shopping cart++"):
                pass
            with when("My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++"):
                pass
            with then("Midtier returns 204"):
                pass
            with and_("My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier"):
                pass
        with scenario("Reserve number — replace existing"):
            with given("++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++"):
                pass
            with and_("++available number++ ++chosen available number++ is selected"):
                pass
            with when("My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++"):
                pass
            with then("Midtier returns 204"):
                pass
            with and_("My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier"):
                pass
        with scenario("Reserve number request fails"):
            with given("++available number++ ++chosen available number++ is selected"):
                pass
            with when("My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++"):
                pass
            with and_("Midtier returns an error"):
                pass
            with then("My Paradise shows *Failed to reserve your number.*"):
                pass

# Story: Submit Reserve Msisdn
with story("Submit Reserve Msisdn"):
    with background.each:
        with scenario("Reserve temporary MSISDN for porting"):
            with given("++MSISDN++ ++available number++ ++held available number++ is locked"):
                pass
            with when("Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (`portin: true`)"):
                pass
            with then("Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag"):
                pass
            with and_("Midtier returns 204"):
                pass
        with scenario("Reserve MSISDN"):
            with given("++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory"):
                pass
            with when("Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++"):
                pass
            with then("Midtier reserves ++available number++ ++chosen available number++ in Mavenir"):
                pass
            with and_("Midtier returns 204 to My Paradise"):
                pass
        with scenario("Reserve MSISDN — release previous"):
            with given("++MSISDN++ ++available number++ ++chosen available number++ is locked"):
                pass
            with and_("++MSISDN++ ++available number++ ++held available number++ is reserved"):
                pass
            with when("Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++"):
                pass
            with then("Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir"):
                pass
            with and_("Midtier returns 204 to My Paradise"):
                pass

# Story: Reserve Msisdn Resource
with story("Reserve Msisdn Resource"):
    with background.each:
        with scenario("Reserve MSISDN resource as temporary port-in number"):
            with given("++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory"):
                pass
            with when("Mavenir is asked to reserve ++available number++ ++held available number++ with `kv_tempNumber: true` (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)"):
                pass
            with then("Mavenir transitions ++available number++ ++held available number++ from locked to reserved"):
                pass
            with and_("Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (`kv_tempNumber`)"):
                pass
        with scenario("Reserve MSISDN resource"):
            with given("++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory"):
                pass
            with when("Mavenir is asked to reserve ++available number++ ++chosen available number++ (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)"):
                pass
            with then("Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved"):
                pass
            with and_("Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++"):
                pass
        with scenario("Reserve MSISDN resource — release previous"):
            with given("++MSISDN++ ++available number++ ++chosen available number++ is locked"):
                pass
            with and_("++MSISDN++ ++available number++ ++held available number++ is reserved"):
                pass
            with when("Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++"):
                pass
            with then("Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved"):
                pass
            with and_("Mavenir transitions ++available number++ ++held available number++ from reserved to available"):
                pass

# Story: Submit Patch Cart With Number Request to Mid-Tier
with story("Submit Patch Cart With Number Request to Mid-Tier"):
    with background.each:
        with scenario("Patch cart with number"):
            with given("++MSISDN++ ++available number++ ++chosen available number++ has been reserved"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier"):
                pass
            with then("Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Patch cart with number fails"):
            with given("++MSISDN++ ++available number++ ++chosen available number++ has been reserved"):
                pass
            with when("My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier"):
                pass
            with and_("Midtier returns an error"):
                pass
            with then("My Paradise shows *Failed to update your cart.*"):
                pass

# Story: Patch Cart With Number
with story("Patch Cart With Number"):
    with background.each:
        with scenario("Patch cart with MSISDN"):
            with given("a ++PML customer++ with a ++Mavenir shopping cart++"):
                pass
            with and_("++MSISDN++ ++available number++ ++chosen available number++ has been reserved"):
                pass
            with when("Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++"):
                pass
            with then("Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic"):
                pass
            with and_("Midtier returns the updated ++PML customer++ to My Paradise"):
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

# Story: Bring a Number
with story("Bring a Number"):
    with background.each:
        with scenario("Bring a number"):
            with then("no Transfer Code is on Bring your mobile number"):
                pass
            with when("the Prospect clicks Get started on Bring your mobile number"):
                pass
            with then("the Prospect can enter ++portability++"):
                pass
            with and_("the Prospect can confirm the information is accurate"):
                pass
            with and_("the Prospect can grant permission to Paradise Mobile to bring the number"):
                pass
            with and_("the Continue operation is disabled"):
                pass
            with and_("the Prospect can go Back"):
                pass
            with when("the Prospect enters ++portability++ ++valid portability++ and checks both permissions"):
                pass
            with then("the Continue operation is enabled"):
                pass
            with when("the Prospect clicks Continue"):
                pass
            with then("My Paradise submits ++portability++ ++valid portability++ to the Midtier"):
                pass
            with and_("Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Number to be ported is incomplete"):
            with when("the Prospect leaves Number to be ported as the Bermuda prefix only"):
                pass
            with then("Number to be ported shows *Please enter the full Bermuda number.*"):
                pass
            with and_("the Continue operation stays disabled"):
                pass
        with scenario("Provider not selected"):
            with when("the Prospect blurs Your current provider without selecting a provider"):
                pass
            with then("Your current provider shows *Please select a provider.*"):
                pass
            with and_("the Continue operation stays disabled"):
                pass

# Story: Confirm Number Already With Paradise
with story("Confirm Number Already With Paradise"):
    with background.each:
        with scenario("Confirm the number is not already with Paradise"):
            with when("the Prospect proceeds to confirming whether their number is already with Paradise"):
                pass
            with then("the Prospect can confirm whether the ++MSISDN++ is already with Paradise"):
                pass
            with when("the Prospect confirms the ++MSISDN++ is not already with Paradise"):
                pass
            with then("My Paradise submits ++portability++ ++valid portability++ to the Midtier"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Confirm the number is already with Paradise"):
            with when("the Prospect proceeds to confirming whether their number is already with Paradise"):
                pass
            with then("the Prospect can confirm whether the ++MSISDN++ is already with Paradise"):
                pass
            with when("the Prospect confirms the ++MSISDN++ is already with Paradise"):
                pass
            with then("++portability++ is not submitted to the Midtier"):
                pass
            with and_("the Prospect is returned to selecting their number"):
                pass

# Story: Evaluate Porting Two Factor Flag
with story("Evaluate Porting Two Factor Flag"):
    with background.each:
        with scenario("Porting two factor flag enabled (Intended)"):
            with given("`porting-2fa` is enabled in GrowthBook"):
                pass
            with and_("the Prospect is in Account Setup"):
                pass
            with when("GrowthBook evaluates the `porting-2fa` flag"):
                pass
            with then("My Paradise mounts the SMS verification step in the porting wizard"):
                pass
            with and_("My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified"):
                pass
        with scenario("Porting two factor flag disabled (live)"):
            with given("`porting-2fa` is disabled in GrowthBook"):
                pass
            with and_("the Prospect is in Account Setup"):
                pass
            with when("GrowthBook evaluates the `porting-2fa` flag"):
                pass
            with then("My Paradise omits the SMS verification step from the porting wizard"):
                pass

# Story: Submit Portability Request to Mid-Tier
with story("Submit Portability Request to Mid-Tier"):
    with background.each:
        with scenario("Submit portability request — porting-2fa off (live)"):
            with given("the Prospect has entered ++portability++ ++valid portability++"):
                pass
            with when("My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++"):
                pass
            with then("Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++"):
                pass
            with and_("My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Submit portability request — porting-2fa on, SMS sent (Intended)"):
            with given("the Prospect has entered ++portability++ ++valid portability++"):
                pass
            with and_("`porting-2fa` is enabled"):
                pass
            with when("My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++"):
                pass
            with then("Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`"):
                pass
            with and_("My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++"):
                pass
            with and_("My Paradise presents the Confirm your number for porting step"):
                pass
        with scenario("Submit portability request — rate limited, bypass (Intended)"):
            with given("`porting-2fa` is enabled"):
                pass
            with when("My Paradise posts a ++portability request++"):
                pass
            with and_("Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`"):
                pass
            with then("My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Submit portability request — invalid number (Intended)"):
            with given("`porting-2fa` is enabled"):
                pass
            with when("My Paradise posts a ++portability request++"):
                pass
            with and_("Midtier returns `{ status: invalid_number }`"):
                pass
            with then("My Paradise shows *This number is invalid.* on Number to be ported"):
                pass
        with scenario("Submit portability request fails"):
            with when("My Paradise posts a ++portability request++"):
                pass
            with and_("Midtier returns an error"):
                pass
            with then("My Paradise shows *Failed to save your portability.*"):
                pass

# Story: Patch Cart With Portability
with story("Patch Cart With Portability"):
    with background.each:
        with scenario("Patch cart with portability"):
            with given("a ++PML customer++ with a ++Mavenir shopping cart++"):
                pass
            with and_("++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number"):
                pass
            with and_("++portability++ ++valid portability++ is in the request"):
                pass
            with when("Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++"):
                pass
            with then("Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)"):
                pass
            with and_("Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++"):
                pass

# Story: Send Port Verification
with story("Send Port Verification"):
    with background.each:
        with scenario("Send port verification SMS"):
            with given("`porting-2fa` is enabled"):
                pass
            with and_("++portability++ ++valid portability++ is in the ++Mavenir shopping cart++"):
                pass
            with when("Midtier sends port verification to ++portability++ ++valid portability++ portNumber"):
                pass
            with then("Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber"):
                pass
            with and_("Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise"):
                pass
        with scenario("Send port verification — rate limited"):
            with given("`porting-2fa` is enabled"):
                pass
            with when("Midtier sends port verification"):
                pass
            with and_("Twilio rate limits the request"):
                pass
            with then("Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise"):
                pass
        with scenario("Send port verification — invalid number"):
            with given("`porting-2fa` is enabled"):
                pass
            with when("Midtier sends port verification"):
                pass
            with and_("Twilio rejects the number as invalid"):
                pass
            with then("Midtier returns `{ status: invalid_number }` to My Paradise"):
                pass

# Story: Send Verification Sms
with story("Send Verification Sms"):
    with background.each:
        with scenario("Send verification SMS"):
            with given("`porting-2fa` is enabled"):
                pass
            with and_("++portability++ ++valid portability++ portNumber is a valid Bermuda number"):
                pass
            with when("Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber"):
                pass
            with then("Twilio creates a verification for ++portability++ ++valid portability++ portNumber (`channel: sms`)"):
                pass
            with and_("Twilio returns `sent` to Midtier"):
                pass
        with scenario("Send verification SMS — rate limited"):
            with given("`porting-2fa` is enabled"):
                pass
            with when("Twilio is asked to send a verification SMS"):
                pass
            with and_("the rate limit for ++portability++ ++valid portability++ portNumber is exceeded"):
                pass
            with then("Twilio returns `rate_limited` to Midtier"):
                pass

# Story: Enter Porting Sms Code
with story("Enter Porting Sms Code"):
    with background.each:
        with scenario("Enter ++porting SMS code++"):
            with when("the Prospect proceeds to confirming their number for porting"):
                pass
            with then("the Prospect sees the code was sent to the ++portability++ number"):
                pass
            with and_("the Prospect can enter ++porting SMS code++ in Enter SMS code"):
                pass
            with and_("the Prospect can Resend"):
                pass
            with and_("Resend is disabled for 30 seconds"):
                pass
            with and_("the Prospect can Change"):
                pass
            with and_("the Prospect can go Back"):
                pass
            with and_("the Verify code operation is disabled"):
                pass
            with when("the Prospect enters ++porting SMS code++ ++valid porting SMS code++"):
                pass
            with then("the Verify code operation is enabled"):
                pass
            with when("the Prospect clicks Verify code"):
                pass
            with then("My Paradise checks the ++porting SMS code++ through the Midtier"):
                pass
            with and_("the Prospect is forwarded to Select Sim"):
                pass
        with scenario("Verify with unusable ++porting SMS code++"):
            with when("the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++"):
                pass
            with then("Enter SMS code shows helper text *Invalid verification code.*"):
                pass
        with scenario("Resend ++porting SMS code++"):
            with when("the Prospect clicks Resend"):
                pass
            with then("My Paradise SMSes a ++porting SMS code++ through the Midtier"):
                pass
            with and_("the Prospect sees *A new code was sent to* the ++portability++ number"):
                pass
            with and_("Resend is disabled for 30 seconds before it can be used again"):
                pass

# Story: Check Port Verification
with story("Check Port Verification"):
    with background.each:
        with scenario("Check port verification — code valid"):
            with when("Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber"):
                pass
            with then("Midtier checks the ++porting SMS code++ with Twilio"):
                pass
            with and_("Twilio returns `approved`"):
                pass
            with and_("Midtier marks the ++PML customer++ phone as verified"):
                pass
            with and_("Midtier returns `{ verified: true }` to My Paradise"):
                pass
        with scenario("Check port verification — code mismatch"):
            with when("Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber"):
                pass
            with then("Midtier checks the ++porting SMS code++ with Twilio"):
                pass
            with and_("Twilio returns a non-approved status"):
                pass
            with and_("Midtier returns `{ verified: false }` to My Paradise"):
                pass

# Story: Check Verification
with story("Check Verification"):
    with background.each:
        with scenario("Check verification — code valid"):
            with when("Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber"):
                pass
            with then("Twilio creates a verification check (`verificationChecks.create`)"):
                pass
            with and_("Twilio returns `approved` to Midtier"):
                pass
        with scenario("Check verification — code mismatch"):
            with when("Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber"):
                pass
            with then("Twilio creates a verification check"):
                pass
            with and_("Twilio returns a non-approved status to Midtier"):
                pass

# Story: Sweep Stale Number Reservations
# Actor: Care
with story("Sweep Stale Number Reservations"):
    with background.each:
        with scenario("Sweep stale number reservations"):
            with given("++MSISDN++ resources have been reserved but have no active order"):
                pass
            with and_("Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory"):
                pass
            with when("Care sweeps stale ++MSISDN++ reservations"):
                pass
            with then("Mavenir transitions the stale ++MSISDN++ resources from reserved to available"):
                pass
            with and_("the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory"):
                pass
