/**
 * Epic: Get Sign Up Plan
 * Orders: 0.0.0
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Hand Off Sign Up To Onboarding
 * Actor: Website
 */

story('Hand Off Sign Up To Onboarding', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Open Plan Deep Link
 * Actor: Customer
 */

story('Open Plan Deep Link', () => {
  scenario('Open Plan Deep Link', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      })
        .and('the Customer arrived at sign-up from the Paradise Mobile website', () => {
          // TODO: implement step
        });
    });
    when('the Customer opens a plan deep link for ++plan++ ++{scenario}++', () => {
      // TODO: implement step
    });
    then('++{scenario}++ is selected', () => {
      // TODO: implement step
    })
      .and('the Customer continues to Enter Account Credentials', () => {
        // TODO: implement step
      });
  });

  scenario('Unknown plan deep link', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      })
        .and('the Customer arrived at sign-up from the Paradise Mobile website', () => {
          // TODO: implement step
        });
    });
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
 * Story: Load Plan Catalog
 * Actor: My Paradise
 */

story('Load Plan Catalog', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Apply Catalog Voucher
 * Actor: Customer
 */

story('Apply Catalog Voucher', () => {
  scenario('Apply Catalog Voucher via deep link', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      });
    });
    given('Vouchera has ++catalog voucher++ ++valid catalog voucher++', () => {
      // TODO: implement step
    });
    when('the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link', () => {
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
      .and('the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent', () => {
        // TODO: implement step
      });
  });

  scenario('Apply Catalog Voucher manually', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      });
    });
    given('the Customer is selecting a plan', () => {
      // TODO: implement step
    })
      .and('Vouchera has ++catalog voucher++ ++valid catalog voucher++', () => {
        // TODO: implement step
      });
    when('the Customer applies ++catalog voucher++ ++valid catalog voucher++', () => {
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
      .and('the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent', () => {
        // TODO: implement step
      });
  });

  scenario('Short catalog voucher code is rejected', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      });
    });
    given('the Customer is selecting a plan', () => {
      // TODO: implement step
    });
    when('the Customer applies a catalog voucher shorter than 4 characters', () => {
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
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      });
    });
    given('the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied', () => {
      // TODO: implement step
    });
    when('the Customer removes ++catalog voucher++ ++valid catalog voucher++', () => {
      // TODO: implement step
    });
    then('the catalog has no catalog voucher', () => {
      // TODO: implement step
    });
  });

  scenario('Apply unusable catalog voucher', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      });
    });
    given('the Customer is selecting a plan', () => {
      // TODO: implement step
    })
      .and('Vouchera has ++catalog voucher++ ++{scenario}++', () => {
        // TODO: implement step
      });
    when('the Customer applies ++{scenario}++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      // TODO: implement step
    });
    when('Vouchera returns', () => {
      // TODO: implement step
    });
    then('the catalog voucher is rejected', () => {
      // TODO: implement step
    });
  });

});
