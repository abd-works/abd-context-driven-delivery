from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Sign Up Plan
# Orders: 0.0.0

# Story: Open Plan Deep Link
# Actor: Customer
with story("Open Plan Deep Link"):
        with scenario("Open Plan Deep Link"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            # background-step: And | the Customer arrived at sign-up from the Paradise Mobile website
            with when("the Customer opens a plan deep link for ++plan++ ++{scenario}++"):
                pass
            with then("++{scenario}++ is selected"):
                pass
            with and_("the Customer continues to Enter Account Credentials"):
                pass
        with scenario("Unknown plan deep link"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            # background-step: And | the Customer arrived at sign-up from the Paradise Mobile website
            with given("the plan catalog contains purchasable plans"):
                pass
            with but_("the deep-link plan id is not in the catalog"):
                pass
            with when("the Customer opens a plan deep link"):
                pass
            with then("the plan is not found"):
                pass

# Story: Apply Catalog Voucher
# Actor: Customer
with story("Apply Catalog Voucher"):
        with scenario("Apply Catalog Voucher via deep link"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            with given("Vouchera has ++catalog voucher++ ++valid catalog voucher++"):
                pass
            with when("the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link"):
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                pass
            with when("Vouchera returns the voucher view"):
                pass
            with then("the catalog voucher is applied"):
                pass
            with and_("the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent"):
                pass
        with scenario("Apply Catalog Voucher manually"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            with given("the Customer is selecting a plan"):
                pass
            with and_("Vouchera has ++catalog voucher++ ++valid catalog voucher++"):
                pass
            with when("the Customer applies ++catalog voucher++ ++valid catalog voucher++"):
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                pass
            with when("Vouchera returns the voucher view"):
                pass
            with then("the catalog voucher is applied"):
                pass
            with and_("the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent"):
                pass
        with scenario("Short catalog voucher code is rejected"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            with given("the Customer is selecting a plan"):
                pass
            with when("the Customer applies a catalog voucher shorter than 4 characters"):
                pass
            with then("the catalog voucher is rejected"):
                pass
            with and_("Vouchera is not asked for the voucher"):
                pass
        with scenario("Remove Catalog Voucher"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            with given("the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied"):
                pass
            with when("the Customer removes ++catalog voucher++ ++valid catalog voucher++"):
                pass
            with then("the catalog has no catalog voucher"):
                pass
        with scenario("Apply unusable catalog voucher"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            with given("the Customer is selecting a plan"):
                pass
            with and_("Vouchera has ++catalog voucher++ ++{scenario}++"):
                pass
            with when("the Customer applies ++{scenario}++"):
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                pass
            with when("Vouchera returns"):
                pass
            with then("the catalog voucher is rejected"):
                pass
