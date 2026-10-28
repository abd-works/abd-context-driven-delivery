from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import reloadCart, billingAccountId, cartWithBilling, essentials, anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, ace, amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines


# Epic: Get Voucher Credit
# Orders: 0.0.8

# Story: Redeem Voucher and Apply Credit
with story("Redeem Voucher and Apply Credit"):
    # typescript body to translate:
    # let redeemSpy: MockInstance<typeof voucheraGateway.redeem>;
    # let applyCreditSpy: MockInstance<typeof portalGateway.applyCredit>;
    #
    # beforeEach(() => {
    #   redeemSpy = vi.spyOn(voucheraGateway, 'redeem');
    #   applyCreditSpy = vi.spyOn(portalGateway, 'applyCredit');
    # });
    #
    # redeemMatchOutlines.forEach(({
    #   example, makeVoucher, seed, voucherCode, orderAmount, discountAmount, totalAmount,
    #   creditExample, creditAmount, remarks,
    # }) => {
    # });
        with scenario("Redeem a plan-restricted voucher that matches the cart bundle: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # let redemption: VoucherRedemption | null;
            # let result: Billing;
            # examples: reloadCart, billingAccountId, cartWithBilling, essentials
            with given("the Customer is in Order Creation with ${example} applied"):
                # typescript body to translate:
                # cart = await cartWithBilling(essentials.id);
                # cart.voucher = makeVoucher(cart);
                # voucheraGateway.seedVoucher(seed.code, seed);
                pass
            with when("the Customer redeems the voucher"):
                # typescript body to translate:
                # redemption = cart.voucher!.redeem();
                pass
            with then("My Paradise sends the redeem request to Vouchera with ${example} orderAmount ${orderAmount}"):
                # typescript body to translate:
                # expect(redeemSpy).toHaveBeenCalledWith(
                #   voucherCode,
                #   new VoucheraRedeemRequest(cart.customer.identity.email, orderAmount),
                # );
                pass
            with when("Vouchera records the voucher redemption"):
                pass
            with then("My Paradise stores the ${example} redemption"):
                # typescript body to translate:
                # expect(redemption).toBeInstanceOf(VoucherRedemption);
                # expect(redemption?.success).toBe(true);
                # expect(redemption?.discountAmount).toBe(discountAmount);
                # expect(redemption?.totalAmount).toBe(totalAmount);
                pass
            with when("the Customer applies the voucher credit"):
                # typescript body to translate:
                # result = cart.customer.billing!.applyCredit();
                pass
            with then("My Paradise sends the ${creditExample} to Mavenir"):
                # typescript body to translate:
                # expect(applyCreditSpy).toHaveBeenCalledWith(
                #   expect.objectContaining({ id: cart.customer.id }),
                #   expect.objectContaining({
                #     customerId: cart.customer.id,
                #     amount: { unit: CreditUnit.Bmd, value: creditAmount },
                #     glCode: CreditGlCode.Voucher,
                #     transactionType: CreditTransactionType.CreditAdjustment,
                #     transactionSubType: CreditTransactionSubType.Credit,
                #     serviceProviderId: CreditServiceProviderId.Paradise,
                #     remarks,
                #     totalAmount: { unit: CreditUnit.Bmd, value: creditAmount },
                #     channel: { ...CreditChannel.Selfcare },
                #     account: expect.objectContaining({
                #       id: billingAccountId,
                #       '@referredType': CreditAccountReferredType.Individual,
                #     }),
                #   }),
                # );
                pass
            with when("Mavenir records the credit adjustment on the billing account"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores the credit on the Customer billing account"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Billing);
                # expect(cart.customer.billing?.id).toBe(billingAccountId);
                pass
        with scenario("Redeem an any-plan voucher"):
            # typescript body to translate:
            # let cart: Cart;
            # let redemption: VoucherRedemption | null;
            # examples: anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials
            with given("the Customer is in Order Creation with any-plan voucher applied"):
                # typescript body to translate:
                # cart = await cartWithBilling(essentials.id);
                # cart.voucher = anyPlanVoucher(cart);
                # voucheraGateway.seedVoucher(anyPlanVoucheraSeed.code, anyPlanVoucheraSeed);
                pass
            with when("the Customer redeems the voucher"):
                # typescript body to translate:
                # redemption = cart.voucher!.redeem();
                pass
            with then("My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00"):
                # typescript body to translate:
                # expect(redeemSpy).toHaveBeenCalledWith(
                #   anyPlanVoucherCode,
                #   new VoucheraRedeemRequest(cart.customer.identity.email, '0.00'),
                # );
                pass
            with when("Vouchera records the voucher redemption"):
                pass
            with then("My Paradise stores the zero redemption"):
                # typescript body to translate:
                # expect(redemption).toBeInstanceOf(VoucherRedemption);
                # expect(redemption).toEqual(zeroRedemption);
                pass
            with and_("My Paradise skips the apply credit request to Mavenir"):
                # typescript body to translate:
                # expect(applyCreditSpy).not.toHaveBeenCalled();
                pass
        with scenario("Skip redeem when the cart bundle is not in the voucher plan list"):
            # typescript body to translate:
            # let cart: Cart;
            # let redemption: VoucherRedemption | null;
            # examples: ace, amountOffVoucher, cartWithBilling
            with given("the Customer is in Order Creation with amount-off voucher applied and Ace in the cart"):
                # typescript body to translate:
                # cart = await cartWithBilling(ace.id);
                # cart.voucher = amountOffVoucher(cart);
                pass
            with when("the Customer redeems the voucher"):
                # typescript body to translate:
                # redemption = cart.voucher!.redeem();
                pass
            with then("My Paradise skips the redeem request to Vouchera"):
                # typescript body to translate:
                # expect(redeemSpy).not.toHaveBeenCalled();
                # expect(redemption).toBeNull();
                pass
            with and_("My Paradise skips the apply credit request to Mavenir"):
                # typescript body to translate:
                # expect(applyCreditSpy).not.toHaveBeenCalled();
                pass
        with scenario("Failed voucher redemption"):
            # typescript body to translate:
            # let cart: Cart;
            # let redemption: VoucherRedemption | null;
            # let result: Billing;
            # examples: amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines, cartWithBilling, essentials
            with given("the Customer is in Order Creation with amount-off voucher applied"):
                # typescript body to translate:
                # cart = await cartWithBilling(essentials.id);
                # cart.voucher = amountOffVoucher(cart);
                # voucheraGateway.seedVoucher(amountOffVoucheraSeed.code, amountOffVoucheraSeed);
                # voucheraGateway.seedRedeemError(new Error('Vouchera unavailable'));
                pass
            with when("the Customer redeems the voucher"):
                # typescript body to translate:
                # redemption = cart.voucher!.redeem();
                pass
            with then("My Paradise sends the redeem request to Vouchera"):
                # typescript body to translate:
                # expect(redeemSpy).toHaveBeenCalledWith(
                #   amountOffVoucherCode,
                #   new VoucheraRedeemRequest(cart.customer.identity.email, redeemMatchOutlines[0].orderAmount),
                # );
                pass
            with when("Vouchera returns an error"):
                pass
            with then("the voucher redemption is unsuccessful"):
                # typescript body to translate:
                # expect(redemption).toBeInstanceOf(VoucherRedemption);
                # expect(redemption?.success).toBe(false);
                pass
            with when("the Customer applies the voucher credit"):
                # typescript body to translate:
                # result = cart.customer.billing!.applyCredit();
                pass
            with then("My Paradise skips the apply credit request to Mavenir"):
                # typescript body to translate:
                # expect(applyCreditSpy).not.toHaveBeenCalled();
                # expect(result).toBe(cart.customer.billing);
                pass
