/**
 * Epic: Get Voucher Credit
 * Orders: 0.0.8
 */

import { background, scenario, story } from "../story-test.js";
import { anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials, ace, amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines } from "./examples";


/**
 * Story: Redeem Voucher and Apply Credit
 */

story('Redeem Voucher and Apply Credit', () => {
    scenario('Redeem an any-plan voucher', ({ given, when, then }) => {
      // examples: anyPlanVoucher, anyPlanVoucherCode, anyPlanVoucheraSeed, zeroRedemption, cartWithBilling, essentials
      given('the Customer is in Order Creation with any-plan voucher applied', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00', () => {});
      when('Vouchera records the voucher redemption', () => {});
      then('My Paradise stores the zero redemption', () => {}).and('My Paradise skips the apply credit request to Mavenir', () => {});
    });
    scenario('Skip redeem when the cart bundle is not in the voucher plan list', ({ given, when, then }) => {
      // examples: ace, amountOffVoucher, cartWithBilling
      given('the Customer is in Order Creation with amount-off voucher applied and Ace in the cart', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise skips the redeem request to Vouchera', () => {}).and('My Paradise skips the apply credit request to Mavenir', () => {});
    });
    scenario('Failed voucher redemption', ({ given, when, then }) => {
      // examples: amountOffVoucher, amountOffVoucherCode, amountOffVoucheraSeed, redeemMatchOutlines, cartWithBilling, essentials
      given('the Customer is in Order Creation with amount-off voucher applied', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise sends the redeem request to Vouchera', () => {});
      when('Vouchera returns an error', () => {});
      then('the voucher redemption is unsuccessful', () => {});
      when('the Customer applies the voucher credit', () => {});
      then('My Paradise skips the apply credit request to Mavenir', () => {});
    });
});
