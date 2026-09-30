from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials, ace, amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines


# Epic: Get Voucher Credit
# Orders: 0.0.8

# Story: Redeem Voucher and Apply Credit
with story("Redeem Voucher and Apply Credit"):
        with scenario("Redeem an any-plan voucher"):
            # examples: anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials
            with given("the Customer is in Order Creation with any-plan voucher applied"):
                pass
            with when("the Customer redeems the voucher"):
                pass
            with then("My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00"):
                pass
            with when("Vouchera records the voucher redemption"):
                pass
            with then("My Paradise stores the zero redemption"):
                pass
            with and_("My Paradise skips the apply credit request to Mavenir"):
                pass
        with scenario("Skip redeem when the cart bundle is not in the voucher plan list"):
            # examples: ace, amountOffVoucher, cartWithBilling
            with given("the Customer is in Order Creation with amount-off voucher applied and Ace in the cart"):
                pass
            with when("the Customer redeems the voucher"):
                pass
            with then("My Paradise skips the redeem request to Vouchera"):
                pass
            with and_("My Paradise skips the apply credit request to Mavenir"):
                pass
        with scenario("Failed voucher redemption"):
            # examples: amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines, cartWithBilling, essentials
            with given("the Customer is in Order Creation with amount-off voucher applied"):
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
