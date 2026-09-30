from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Verified Profile

# Story: Customer Complete Persona Kyc
# Actor: Customer
with story("Customer Complete Persona Kyc"):
    with background.each:
        with scenario("Persona verification required"):
            with then("no idNumber on ++identity++"):
                pass
            with when("the Customer validates whether a Persona inquiry is required"):
                pass
            with then("a Persona inquiry is required"):
                pass
            with and_("the Customer is on the Profile KYC step"):
                pass
        with scenario("Persona verification already complete"):
            with given("the Customer has ++identity++ with an idNumber"):
                pass
            with when("the Customer validates whether a Persona inquiry is required"):
                pass
            with then("the Persona inquiry is already complete"):
                pass
            with and_("the Customer is forwarded to Checkout"):
                pass
        with scenario("Create a completed Persona inquiry"):
            with given("the Customer has no idNumber on ++identity++"):
                pass
            with when("the Customer creates a Persona inquiry"):
                pass
            with then("My Paradise sends the inquiry request to Persona with the Customer email"):
                pass
            with and_("My Paradise retrieves the Persona document"):
                pass
            with when("Persona returns ++Persona inquiry++ ++completed Persona inquiry++"):
                pass
            with then("the Customer has a verified ++Persona inquiry++"):
                pass
            with and_("My Paradise maps the inquiry onto ++identity++ ++valid identity++ and ++address++ ++valid address++"):
                pass
            with and_("Customer verified stays false until the Customer confirms their identity"):
                pass
            with when("Persona returns ++Persona document++ ++valid Persona document++"):
                pass
            with then("++identity++ expiry date is the ++Persona document++ expiration date"):
                pass
        with scenario("Persona inquiry not completed"):
            with when("the Customer creates a Persona inquiry"):
                pass
            with then("My Paradise sends the inquiry request to Persona with the Customer email"):
                pass
            with when("Persona returns ++Persona inquiry++ ++failed Persona inquiry++"):
                pass
            with then("the Customer has an unverified ++Persona inquiry++"):
                pass
            with and_("++identity++ and ++address++ stay empty"):
                pass
        with scenario("No government ID document on inquiry"):
            with given("the completed ++Persona inquiry++ has no government ID document"):
                pass
            with when("the Customer creates a Persona inquiry"):
                pass
            with then("My Paradise sends the inquiry request to Persona"):
                pass
            with and_("My Paradise does not retrieve a Persona document"):
                pass
            with when("Persona returns the completed inquiry without a government ID"):
                pass
            with then("++identity++ expiry date is empty"):
                pass
        with scenario("Persona errors on inquiry load"):
            with when("the Customer creates a Persona inquiry"):
                pass
            with then("My Paradise sends the inquiry request to Persona"):
                pass
            with when("Persona returns an error"):
                pass
            with then("the Customer has an unverified ++Persona inquiry++"):
                pass
            with and_("++identity++ stays empty"):
                pass
        with scenario("Document not found"):
            with given("Persona has no ++Persona document++ for that document ID"):
                pass
            with when("the Customer creates a Persona inquiry"):
                pass
            with then("My Paradise retrieves the Persona document"):
                pass
            with when("Persona returns that the document is not found"):
                pass
            with then("++identity++ expiry date is empty"):
                pass
        with scenario("Document email mismatch"):
            with given("the ++Persona document++ email does not match the Customer email"):
                pass
            with when("the Customer creates a Persona inquiry"):
                pass
            with then("My Paradise retrieves the Persona document"):
                pass
            with when("Persona returns unauthorized"):
                pass
            with then("++identity++ expiry date is empty"):
                pass
        with scenario("Verify later"):
            with given("the Customer has a ++My Paradise customer++ with no idNumber on ++identity++"):
                pass
            with when("the Customer proceeds without a Persona inquiry"):
                pass
            with then("My Paradise does not send an inquiry request to Persona"):
                pass
            with and_("no ++Persona inquiry++ is stored"):
                pass
            with and_("the Customer is still on the Profile KYC step"):
                pass
        with scenario("Enter valid identity and address"):
            with given("the Customer has a ++My Paradise customer++ in session"):
                pass
            with when("the Customer enters ++identity++ ++valid identity++ and ++address++ ++valid address++"):
                pass
            with then("all profile requirements are met"):
                pass
            with and_("the Customer can confirm their identity"):
                pass
        with scenario("Enter identity after a verified Persona inquiry"):
            with given("the Customer has a verified ++Persona inquiry++ mapped onto ++identity++ ++valid identity++"):
                pass
            with when("the Customer enters the mapped ++identity++ and ++address++"):
                pass
            with then("all profile requirements are met"):
                pass
            with and_("the ID fields are present on ++identity++"):
                pass
        with scenario("Re-enter a verified identity"):
            with given("the Customer has ++identity++ ++valid identity++ already verified"):
                pass
            with when("the Customer re-enters ++identity++ ++valid identity++"):
                pass
            with then("the identity is no longer verified"):
                pass
            with and_("the Customer can confirm their identity again"):
                pass
        with scenario("Enter incomplete identity or address"):
            with when("the Customer enters ++identity++ and ++address++ with {field} empty"):
                pass
            with then("{field} is missing"):
                pass
            with and_("the Customer cannot confirm their identity"):
                pass
        with scenario("Confirm identity with a verified Persona inquiry"):
            with given("the Customer has entered ++identity++ ++valid identity++ and ++address++ ++valid address++"):
                pass
            with and_("the Customer has a verified ++Persona inquiry++"):
                pass
            with when("the Customer confirms their identity"):
                pass
            with then("My Paradise maps ++identity++ and ++address++ onto the Mavenir engaged party and contact medium"):
                pass
            with and_("My Paradise sends the profile patch to Mavenir"):
                pass
            with when("Mavenir patches the customer"):
                pass
            with then("the Customer identity is persisted"):
                pass
            with and_("the Customer is verified"):
                pass
            with and_("the ++Persona inquiry++ is cleared"):
                pass
        with scenario("Profile requirements unmet"):
            with given("the Customer has not entered ++identity++ or ++address++"):
                pass
            with when("the Customer confirms their identity"):
                pass
            with then("the identity cannot be confirmed"):
                pass
            with and_("My Paradise does not send a profile patch to Mavenir"):
                pass
        with scenario("Customer already exists"):
            with given("another Mavenir customer already has ++identity++ idNumber I1234562"):
                pass
            with when("the Customer confirms their identity"):
                pass
            with then("My Paradise sends the profile patch to Mavenir"):
                pass
            with and_("the identity cannot be confirmed because a customer with that information already exists"):
                pass
        with scenario("Mavenir profile patch error"):
            with given("Mavenir returns a profile patch error"):
                pass
            with when("the Customer confirms their identity"):
                pass
            with then("My Paradise sends the profile patch to Mavenir"):
                pass
            with and_("the identity cannot be confirmed"):
                pass

# Story: Collect Identity With Brand Amassador
# Actor: Ambassador
with story("Collect Identity With Brand Amassador"):
    with background.each:
        with scenario("Collect identity with Brand Ambassador"):
            with given("the Customer is choosing how to verify their ID"):
                pass
            with when("the Customer asks a Brand Ambassador to verify their ID"):
                pass
            with then("the Ambassador will be in touch to proceed with verification"):
                pass
            with and_("the Ambassador collects the Customer's ++identity++ documents over WhatsApp"):
                pass
            with and_("the Customer proceeds to enter identity in My Paradise"):
                pass
