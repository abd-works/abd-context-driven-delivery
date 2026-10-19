/**
 * Epic: Get Voucher Credit
 * Orders: 0.0.8
 */

import { scenario, story } from "tests/story-test";
import { anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials, ace, amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines } from "./examples";


/**
 * Story: Redeem Voucher and Apply Credit
 */

story('Redeem Voucher and Apply Credit', () => {
  scenario('Redeem an any-plan voucher', ({ given, when, then }) => {
    // examples: anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials
    given('the Customer is in Order Creation with any-plan voucher applied', () => {
      // TODO: implement step
    });
    when('the Customer redeems the voucher', () => {
      // TODO: implement step
    });
    then('My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00', () => {
      // TODO: implement step
    });
    when('Vouchera records the voucher redemption', () => {
      // TODO: implement step
    });
    then('My Paradise stores the zero redemption', () => {
      // TODO: implement step
    })
      .and('My Paradise skips the apply credit request to Mavenir', () => {
        // TODO: implement step
      });
  });

  scenario('Skip redeem when the cart bundle is not in the voucher plan list', ({ given, when, then }) => {
    // examples: ace, amountOffVoucher, cartWithBilling
    given('the Customer is in Order Creation with amount-off voucher applied and Ace in the cart', () => {
      // TODO: implement step
    });
    when('the Customer redeems the voucher', () => {
      // TODO: implement step
    });
    then('My Paradise skips the redeem request to Vouchera', () => {
      // TODO: implement step
    })
      .and('My Paradise skips the apply credit request to Mavenir', () => {
        // TODO: implement step
      });
  });

  scenario('Failed voucher redemption', ({ given, when, then }) => {
    // examples: amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines, cartWithBilling, essentials
    given('the Customer is in Order Creation with amount-off voucher applied', () => {
      // TODO: implement step
    });
    when('the Customer redeems the voucher', () => {
      // TODO: implement step
    });
    then('My Paradise sends the redeem request to Vouchera', () => {
      // TODO: implement step
    });
    when('Vouchera returns an error', () => {
      // TODO: implement step
    });
    then('the voucher redemption is unsuccessful', () => {
      // TODO: implement step
    });
    when('the Customer applies the voucher credit', () => {
      // TODO: implement step
    });
    then('My Paradise skips the apply credit request to Mavenir', () => {
      // TODO: implement step
    });
  });

});
