from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Sign Up Plan
# Orders: 0.0.5

# Story: Open Plan Deep Link
with story("Open Plan Deep Link"):
        with scenario("Unknown plan deep link"):
            with given("the plan catalog contains purchasable plans"):
                pass
            with but_("the deep-link plan id is not in the catalog"):
                pass
            with when("the Customer opens a plan deep link"):
                pass
            with then("the plan is not found"):
                pass

# Story: Apply Catalog Voucher
with story("Apply Catalog Voucher"):
        with scenario("Apply Catalog Voucher via deep link"):
            with given("the plan catalog contains purchasable plans"):
                pass
            with and_("Vouchera has valid catalog voucher"):
                pass
            with when("the Customer applies valid catalog voucher from a promotional voucher link"):
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                pass
            with when("Vouchera returns the voucher view"):
                pass
            with then("the catalog voucher is applied"):
                pass
            with and_("the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent"):
                pass
        with scenario("Apply Catalog Voucher manually"):
            with given("the Customer is selecting a plan"):
                pass
            with and_("Vouchera has valid catalog voucher"):
                pass
            with when("the Customer applies valid catalog voucher"):
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                pass
            with when("Vouchera returns the voucher view"):
                pass
            with then("the catalog voucher is applied"):
                pass
            with and_("the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent"):
                pass
        with scenario("Short catalog voucher code is rejected"):
            with given("the Customer is selecting a plan"):
                pass
            with then("the catalog voucher is rejected"):
                pass
            with and_("Vouchera is not asked for the voucher"):
                pass
        with scenario("Remove Catalog Voucher"):
            with given("the Customer is selecting a plan with valid catalog voucher applied"):
                pass
            with when("the Customer removes valid catalog voucher"):
                pass
            with then("the catalog has no catalog voucher"):
                pass
