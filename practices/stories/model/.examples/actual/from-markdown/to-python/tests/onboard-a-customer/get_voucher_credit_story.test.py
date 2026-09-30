from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Get Voucher Credit
# Orders: 0.0.9

# Story: Redeem Voucher and Apply Credit
# Actor: My Paradise
with story("Redeem Voucher and Apply Credit"):
        with scenario("Redeem a plan-restricted voucher that matches the cart bundle"):
            with given("the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied"):
                pass
            with and_("the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)"):
                pass
            with and_("Vouchera has ++voucher++ ++{voucher}++"):
                pass
            with and_("the Customer has a billing account"):
                pass
            with when("the Customer redeems the voucher"):
                pass
            with then("My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount `70.00`)"):
                pass
            with when("Vouchera records the ++voucher redemption++"):
                pass
            with then("My Paradise stores ++voucher redemption++ ++{redemption}++"):
                pass
            with when("the Customer applies the voucher credit"):
                pass
            with then("My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (`transactionType` creditAdjustment, glCode `100004`, unit BMD, channel `@type`)"):
                pass
            with when("Mavenir records the ++credit adjustment++ on the billing account"):
                pass
            with then("My Paradise stores the credit on the Customer billing account"):
                pass
            with and_("continues to Create Product Order"):
                pass
        with scenario("Redeem an any-plan voucher"):
            with given("the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied"):
                pass
            with and_("the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)"):
                pass
            with and_("Vouchera has ++voucher++ ++any-plan voucher++"):
                pass
            with when("the Customer redeems the voucher"):
                pass
            with then("My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount `0.00`)"):
                pass
            with when("Vouchera records the ++voucher redemption++"):
                pass
            with then("My Paradise stores ++voucher redemption++ ++zero redemption++"):
                pass
            with and_("My Paradise skips the apply credit request to Mavenir"):
                pass
            with and_("continues to Create Product Order"):
                pass
        with scenario("Skip redeem when the cart bundle is not in the voucher plan list"):
            with given("the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied"):
                pass
            with but_("the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id `100000000042`) which is not in ++voucher++ ++amount-off voucher++ planIds"):
                pass
            with when("the Customer redeems the voucher"):
                pass
            with then("My Paradise skips the redeem request to Vouchera"):
                pass
            with and_("My Paradise skips the apply credit request to Mavenir"):
                pass
            with and_("continues to Create Product Order"):
                pass
        with scenario("Failed voucher redemption"):
            with given("the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied"):
                pass
            with and_("the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++"):
                pass
            with and_("Vouchera returns an error for the redeem request"):
                pass
            with when("the Customer redeems the voucher"):
                pass
            with then("My Paradise sends the redeem request to Vouchera"):
                pass
            with when("Vouchera returns an error"):
                pass
            with then("the voucher redemption is unsuccessful"):
                pass
            with when("the Customer applies the voucher credit"):
                pass
            with then("My Paradise skips the apply credit request to Mavenir"):
                pass
            with and_("continues to Create Product Order"):
                pass
