/**
 * Epic: Get Sign Up Plan
 * Orders: 0.0.5
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Open Plan Deep Link
 */

story('Open Plan Deep Link', () => {
  scenario('Unknown plan deep link', ({ given, when, then }) => {
    given('the plan catalog contains purchasable plans', () => {
      // TODO: implement step
    })
      .but('the deep-link plan id is not in the catalog', () => {
        // TODO: implement step
      });
    when('the Customer opens a plan deep link', () => {
      // TODO: implement step
    });
    then('the plan is not found', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Apply Catalog Voucher
 */

story('Apply Catalog Voucher', () => {
  scenario('Apply Catalog Voucher via deep link', ({ given, when, then }) => {
    given('the plan catalog contains purchasable plans', () => {
      // TODO: implement step
    })
      .and('Vouchera has valid catalog voucher', () => {
        // TODO: implement step
      });
    when('the Customer applies valid catalog voucher from a promotional voucher link', () => {
      // TODO: implement step
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      // TODO: implement step
    });
    when('Vouchera returns the voucher view', () => {
      // TODO: implement step
    });
    then('the catalog voucher is applied', () => {
      // TODO: implement step
    })
      .and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {
        // TODO: implement step
      });
  });

  scenario('Apply Catalog Voucher manually', ({ given, when, then }) => {
    given('the Customer is selecting a plan', () => {
      // TODO: implement step
    })
      .and('Vouchera has valid catalog voucher', () => {
        // TODO: implement step
      });
    when('the Customer applies valid catalog voucher', () => {
      // TODO: implement step
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      // TODO: implement step
    });
    when('Vouchera returns the voucher view', () => {
      // TODO: implement step
    });
    then('the catalog voucher is applied', () => {
      // TODO: implement step
    })
      .and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {
        // TODO: implement step
      });
  });

  scenario('Short catalog voucher code is rejected', ({ given, when, then }) => {
    given('the Customer is selecting a plan', () => {
      // TODO: implement step
    });
    then('the catalog voucher is rejected', () => {
      // TODO: implement step
    })
      .and('Vouchera is not asked for the voucher', () => {
        // TODO: implement step
      });
  });

  scenario('Remove Catalog Voucher', ({ given, when, then }) => {
    given('the Customer is selecting a plan with valid catalog voucher applied', () => {
      // TODO: implement step
    });
    when('the Customer removes valid catalog voucher', () => {
      // TODO: implement step
    });
    then('the catalog has no catalog voucher', () => {
      // TODO: implement step
    });
  });

});
