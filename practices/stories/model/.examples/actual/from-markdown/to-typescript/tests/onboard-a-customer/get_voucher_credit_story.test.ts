/**
 * Epic: Get Voucher Credit
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Redeem Voucher and Apply Credit
 * Actor: My Paradise
 */

story('Redeem Voucher and Apply Credit', () => {
  scenario('Redeem a plan-restricted voucher that matches the cart bundle', ({ given, when, then }) => {
    given('the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied', () => {
      // TODO: implement step
    })
      .and('the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id 100000000014, totalPrice 70.00)', () => {
        // TODO: implement step
      })
      .and('Vouchera has ++voucher++ ++{voucher}++', () => {
        // TODO: implement step
      })
      .and('the Customer has a billing account', () => {
        // TODO: implement step
      });
    when('the Customer redeems the voucher', () => {
      // TODO: implement step
    });
    then('My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount 70.00)', () => {
      // TODO: implement step
    });
    when('Vouchera records the ++voucher redemption++', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++voucher redemption++ ++{redemption}++', () => {
      // TODO: implement step
    });
    when('the Customer applies the voucher credit', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (transactionType creditAdjustment, glCode 100004, unit BMD, channel @type)', () => {
      // TODO: implement step
    });
    when('Mavenir records the ++credit adjustment++ on the billing account', () => {
      // TODO: implement step
    });
    then('My Paradise stores the credit on the Customer billing account', () => {
      // TODO: implement step
    })
      .and('continues to Create Product Order', () => {
        // TODO: implement step
      });
  });

  scenario('Redeem an any-plan voucher', ({ given, when, then }) => {
    given('the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied', () => {
      // TODO: implement step
    })
      .and('the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id 100000000014, totalPrice 70.00)', () => {
        // TODO: implement step
      })
      .and('Vouchera has ++voucher++ ++any-plan voucher++', () => {
        // TODO: implement step
      });
    when('the Customer redeems the voucher', () => {
      // TODO: implement step
    });
    then('My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount 0.00)', () => {
      // TODO: implement step
    });
    when('Vouchera records the ++voucher redemption++', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++voucher redemption++ ++zero redemption++', () => {
      // TODO: implement step
    })
      .and('My Paradise skips the apply credit request to Mavenir', () => {
        // TODO: implement step
      })
      .and('continues to Create Product Order', () => {
        // TODO: implement step
      });
  });

  scenario('Skip redeem when the cart bundle is not in the voucher plan list', ({ given, when, then }) => {
    given('the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied', () => {
      // TODO: implement step
    })
      .but('the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id 100000000042) which is not in ++voucher++ ++amount-off voucher++ planIds', () => {
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
      })
      .and('continues to Create Product Order', () => {
        // TODO: implement step
      });
  });

  scenario('Failed voucher redemption', ({ given, when, then }) => {
    given('the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied', () => {
      // TODO: implement step
    })
      .and('the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++', () => {
        // TODO: implement step
      })
      .and('Vouchera returns an error for the redeem request', () => {
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
    })
      .and('continues to Create Product Order', () => {
        // TODO: implement step
      });
  });

});
