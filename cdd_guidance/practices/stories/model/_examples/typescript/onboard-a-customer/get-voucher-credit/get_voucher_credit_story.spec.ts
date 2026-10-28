import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { type Cart } from '../../../domain/cart/Cart';
import { Billing } from '../../../domain/billing/Billing';
import { VoucherRedemption } from '../../../domain/cart/Voucher';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { reloadCart } from '../get-number/examples/cart.examples';
import {
  CreditAccountReferredType,
  CreditChannel,
  CreditGlCode,
  CreditServiceProviderId,
  CreditTransactionSubType,
  CreditTransactionType,
  CreditUnit,
} from '../../../domain/systems/mavenir/billing';
import {
  VoucheraRedeemRequest,
  voucheraGateway,
} from '../../../domain/systems/vouchera';
import {
  ace,
  amountOffVoucher,
  amountOffVoucherCode,
  amountOffVoucheraSeed,
  anyPlanVoucher,
  anyPlanVoucherCode,
  anyPlanVoucheraSeed,
} from './examples/voucher.examples';
import {
  redeemMatchOutlines,
  zeroRedemption,
} from './examples/voucher-redemption.examples';
import { billingAccountId, cartWithBilling } from './examples/credit-adjustment.examples';
import { essentials } from '../examples/purchasable-plans.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  portalGateway.reset();
  voucheraGateway.reset();
  vi.restoreAllMocks();
});

story('Redeem Voucher and Apply Credit', () => {
  let redeemSpy: MockInstance<typeof voucheraGateway.redeem>;
  let applyCreditSpy: MockInstance<typeof portalGateway.applyCredit>;

  beforeEach(() => {
    redeemSpy = vi.spyOn(voucheraGateway, 'redeem');
    applyCreditSpy = vi.spyOn(portalGateway, 'applyCredit');
  });

  redeemMatchOutlines.forEach(({
    example, makeVoucher, seed, voucherCode, orderAmount, discountAmount, totalAmount,
    creditExample, creditAmount, remarks,
  }) => {
    scenario(`Redeem a plan-restricted voucher that matches the cart bundle: ${example}`, ({ given, when, then }) => {
      let cart: Cart;
      let redemption: VoucherRedemption | null;
      let result: Billing;

      given(`the Customer is in Order Creation with ${example} applied`, async () => {
        cart = await cartWithBilling(essentials.id);
        cart.voucher = makeVoucher(cart);
        voucheraGateway.seedVoucher(seed.code, seed);
      });
      when('the Customer redeems the voucher', () => {
        redemption = cart.voucher!.redeem();
      });
      then(`My Paradise sends the redeem request to Vouchera with ${example} orderAmount ${orderAmount}`, () => {
        expect(redeemSpy).toHaveBeenCalledWith(
          voucherCode,
          new VoucheraRedeemRequest(cart.customer.identity.email, orderAmount),
        );
      });
      when('Vouchera records the voucher redemption', () => {});
      then(`My Paradise stores the ${example} redemption`, () => {
        expect(redemption).toBeInstanceOf(VoucherRedemption);
        expect(redemption?.success).toBe(true);
        expect(redemption?.discountAmount).toBe(discountAmount);
        expect(redemption?.totalAmount).toBe(totalAmount);
      });
      when('the Customer applies the voucher credit', () => {
        result = cart.customer.billing!.applyCredit();
      });
      then(`My Paradise sends the ${creditExample} to Mavenir`, () => {
        expect(applyCreditSpy).toHaveBeenCalledWith(
          expect.objectContaining({ id: cart.customer.id }),
          expect.objectContaining({
            customerId: cart.customer.id,
            amount: { unit: CreditUnit.Bmd, value: creditAmount },
            glCode: CreditGlCode.Voucher,
            transactionType: CreditTransactionType.CreditAdjustment,
            transactionSubType: CreditTransactionSubType.Credit,
            serviceProviderId: CreditServiceProviderId.Paradise,
            remarks,
            totalAmount: { unit: CreditUnit.Bmd, value: creditAmount },
            channel: { ...CreditChannel.Selfcare },
            account: expect.objectContaining({
              id: billingAccountId,
              '@referredType': CreditAccountReferredType.Individual,
            }),
          }),
        );
      });
      when('Mavenir records the credit adjustment on the billing account', async () => {
        cart = await reloadCart(cart);
      });
      then('My Paradise stores the credit on the Customer billing account', () => {
        expect(result).toBeInstanceOf(Billing);
        expect(cart.customer.billing?.id).toBe(billingAccountId);
      });
    });
  });

  scenario('Redeem an any-plan voucher', ({ given, when, then }) => {
    let cart: Cart;
    let redemption: VoucherRedemption | null;

    given('the Customer is in Order Creation with any-plan voucher applied', async () => {
      cart = await cartWithBilling(essentials.id);
      cart.voucher = anyPlanVoucher(cart);
      voucheraGateway.seedVoucher(anyPlanVoucheraSeed.code, anyPlanVoucheraSeed);
    });
    when('the Customer redeems the voucher', () => {
      redemption = cart.voucher!.redeem();
    });
    then('My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00', () => {
      expect(redeemSpy).toHaveBeenCalledWith(
        anyPlanVoucherCode,
        new VoucheraRedeemRequest(cart.customer.identity.email, '0.00'),
      );
    });
    when('Vouchera records the voucher redemption', () => {});
    then('My Paradise stores the zero redemption', () => {
      expect(redemption).toBeInstanceOf(VoucherRedemption);
      expect(redemption).toEqual(zeroRedemption);
    }).and('My Paradise skips the apply credit request to Mavenir', () => {
      expect(applyCreditSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Skip redeem when the cart bundle is not in the voucher plan list', ({ given, when, then }) => {
    let cart: Cart;
    let redemption: VoucherRedemption | null;

    given('the Customer is in Order Creation with amount-off voucher applied and Ace in the cart', async () => {
      cart = await cartWithBilling(ace.id);
      cart.voucher = amountOffVoucher(cart);
    });
    when('the Customer redeems the voucher', () => {
      redemption = cart.voucher!.redeem();
    });
    then('My Paradise skips the redeem request to Vouchera', () => {
      expect(redeemSpy).not.toHaveBeenCalled();
      expect(redemption).toBeNull();
    }).and('My Paradise skips the apply credit request to Mavenir', () => {
      expect(applyCreditSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Failed voucher redemption', ({ given, when, then }) => {
    let cart: Cart;
    let redemption: VoucherRedemption | null;
    let result: Billing;

    given('the Customer is in Order Creation with amount-off voucher applied', async () => {
      cart = await cartWithBilling(essentials.id);
      cart.voucher = amountOffVoucher(cart);
      voucheraGateway.seedVoucher(amountOffVoucheraSeed.code, amountOffVoucheraSeed);
      voucheraGateway.seedRedeemError(new Error('Vouchera unavailable'));
    });
    when('the Customer redeems the voucher', () => {
      redemption = cart.voucher!.redeem();
    });
    then('My Paradise sends the redeem request to Vouchera', () => {
      expect(redeemSpy).toHaveBeenCalledWith(
        amountOffVoucherCode,
        new VoucheraRedeemRequest(cart.customer.identity.email, redeemMatchOutlines[0].orderAmount),
      );
    });
    when('Vouchera returns an error', () => {});
    then('the voucher redemption is unsuccessful', () => {
      expect(redemption).toBeInstanceOf(VoucherRedemption);
      expect(redemption?.success).toBe(false);
    });
    when('the Customer applies the voucher credit', () => {
      result = cart.customer.billing!.applyCredit();
    });
    then('My Paradise skips the apply credit request to Mavenir', () => {
      expect(applyCreditSpy).not.toHaveBeenCalled();
      expect(result).toBe(cart.customer.billing);
    });
  });
});
