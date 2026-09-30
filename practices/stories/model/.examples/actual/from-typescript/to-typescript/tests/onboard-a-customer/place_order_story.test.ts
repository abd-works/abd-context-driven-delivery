/**
 * Epic: Place Order
 * Orders: 0.0.9
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Create Billing Account
 */

story('Create Billing Account', () => {
  scenario('Create billing account', ({ given, when, then }) => {
    given('the Customer has a configured cart and no billing account', () => {
      // TODO: implement step
    });
    when('the Customer creates a billing account', () => {
      // TODO: implement step
    });
    then('My Paradise sends the billing account request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir creates the billing account', () => {
      // TODO: implement step
    });
    then('the Customer has a billing account', () => {
      // TODO: implement step
    })
      .and('the Customer is on the Done step', () => {
        // TODO: implement step
      });
  });

  scenario('Billing account already exists', ({ given, when, then }) => {
    given('the Customer already has a billing account', () => {
      // TODO: implement step
    });
    when('the Customer creates a billing account', () => {
      // TODO: implement step
    });
    then('the billing account is rejected', () => {
      // TODO: implement step
    })
      .and('Mavenir does not receive a billing account request', () => {
        // TODO: implement step
      });
  });

  scenario('Billing account creation fails', ({ given, when, then }) => {
    given('Mavenir returns an error for the billing account request', () => {
      // TODO: implement step
    });
    when('the Customer creates a billing account', () => {
      // TODO: implement step
    });
    then('the billing account cannot be created', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the customer', () => {
      // TODO: implement step
    });
    then('the Customer has no billing account', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Create Product Order
 */

story('Create Product Order', () => {
  scenario('Create product order', ({ given, when, then }) => {
    given('the Customer is verified and has a billing account, plan, number, and eSIM', () => {
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // TODO: implement step
    });
    then('My Paradise sends the product order request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir creates the product order', () => {
      // TODO: implement step
    });
    then('the order succeeded with pay-up-front', () => {
      // TODO: implement step
    })
      .and('the Customer onboarding is done', () => {
        // TODO: implement step
      });
  });

  scenario('Pay-up-front charge fails', ({ given, when, then }) => {
    given('the pay-up-front charge fails', () => {
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // TODO: implement step
    });
    then('My Paradise does not send a product order to Mavenir', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the cart', () => {
      // TODO: implement step
    });
    then('the order succeeded without pay-up-front', () => {
      // TODO: implement step
    });
  });

  scenario('Product order fails', ({ given, when, then }) => {
    given('Mavenir returns an error for the product order', () => {
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // TODO: implement step
    });
    then('My Paradise sends the product order request to Mavenir', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the cart', () => {
      // TODO: implement step
    });
    then('the order did not succeed', () => {
      // TODO: implement step
    });
  });

  scenario('Onboarding is already done', ({ given, when, then }) => {
    given('the Customer onboarding is already done', () => {
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // TODO: implement step
    });
    then('the product order is rejected', () => {
      // TODO: implement step
    })
      .and('Mavenir does not receive a product order request', () => {
        // TODO: implement step
      });
  });

  scenario('Unverified with no bypass and no portability', ({ given, when, then }) => {
    given('the Customer is not verified and the plan does not bypass verification', () => {
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // TODO: implement step
    });
    then('My Paradise does not send a product order to Mavenir', () => {
      // TODO: implement step
    })
      .and('the cart is marked to submit the order later', () => {
        // TODO: implement step
      });
    when('My Paradise reloads the cart', () => {
      // TODO: implement step
    });
    then('the Customer onboarding is done', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: View Order Result
 */

story('View Order Result', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Create Order Ticket
 */

story('Create Order Ticket', () => {
  // TODO: add main-flow scenario
});
