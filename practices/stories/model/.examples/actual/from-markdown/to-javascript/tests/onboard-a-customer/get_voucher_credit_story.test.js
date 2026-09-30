/**
 * Epic: Get Voucher Credit
 * Orders: 0.0.9
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Redeem Voucher and Apply Credit
 * Actor: My Paradise
 */

story('Redeem Voucher and Apply Credit', () => {
    scenario('Redeem a plan-restricted voucher that matches the cart bundle', ({ given, when, then }) => {
      given('the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied', () => {}).and('the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)', () => {}).and('Vouchera has ++voucher++ ++{voucher}++', () => {}).and('the Customer has a billing account', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount `70.00`)', () => {});
      when('Vouchera records the ++voucher redemption++', () => {});
      then('My Paradise stores ++voucher redemption++ ++{redemption}++', () => {});
      when('the Customer applies the voucher credit', () => {});
      then('My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (`transactionType` creditAdjustment, glCode `100004`, unit BMD, channel `@type`)', () => {});
      when('Mavenir records the ++credit adjustment++ on the billing account', () => {});
      then('My Paradise stores the credit on the Customer billing account', () => {}).and('continues to Create Product Order', () => {});
    });
    scenario('Redeem an any-plan voucher', ({ given, when, then }) => {
      given('the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied', () => {}).and('the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)', () => {}).and('Vouchera has ++voucher++ ++any-plan voucher++', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount `0.00`)', () => {});
      when('Vouchera records the ++voucher redemption++', () => {});
      then('My Paradise stores ++voucher redemption++ ++zero redemption++', () => {}).and('My Paradise skips the apply credit request to Mavenir', () => {}).and('continues to Create Product Order', () => {});
    });
    scenario('Skip redeem when the cart bundle is not in the voucher plan list', ({ given, when, then }) => {
      given('the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied', () => {}).but('the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id `100000000042`) which is not in ++voucher++ ++amount-off voucher++ planIds', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise skips the redeem request to Vouchera', () => {}).and('My Paradise skips the apply credit request to Mavenir', () => {}).and('continues to Create Product Order', () => {});
    });
    scenario('Failed voucher redemption', ({ given, when, then }) => {
      given('the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied', () => {}).and('the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++', () => {}).and('Vouchera returns an error for the redeem request', () => {});
      when('the Customer redeems the voucher', () => {});
      then('My Paradise sends the redeem request to Vouchera', () => {});
      when('Vouchera returns an error', () => {});
      then('the voucher redemption is unsuccessful', () => {});
      when('the Customer applies the voucher credit', () => {});
      then('My Paradise skips the apply credit request to Mavenir', () => {}).and('continues to Create Product Order', () => {});
    });
});
