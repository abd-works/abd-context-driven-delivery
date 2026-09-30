/**
 * Epic: Place Order
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Create Billing Account
 * Actor: My Paradise
 */

story('Create Billing Account', () => {
  scenario('Create billing account', ({ given, when, then }) => {
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
    })
      .and('the Customer has no billing account', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Create Product Order
 * Actor: My Paradise
 */

story('Create Product Order', () => {
  scenario('Create product order', ({ given, when, then }) => {
    given('the Customer is verified', () => {
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
    })
      .and('the order succeeded without pay-up-front', () => {
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
    given('the Customer is not verified', () => {
      // TODO: implement step
    })
      .and('the plan does not bypass verification', () => {
        // TODO: implement step
      })
      .and('the cart has no portability', () => {
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
      })
      .and('the Customer onboarding is done', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: View Order Result
 * Actor: Customer
 */

story('View Order Result', () => {
  scenario('View order result', ({ given, when, then }) => {
    given('the order result is {example}', () => {
      // TODO: implement step
    });
    when('the Customer views their order result', () => {
      // TODO: implement step
    });
    then('the order is {outcome}', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Create Order Ticket
 * Actor: My Paradise
 */

story('Create Order Ticket', () => {
  scenario('Create order ticket', ({ given, when, then }) => {
    given('the Customer {example}', () => {
      // TODO: implement step
    });
    when('the Customer creates the order ticket', () => {
      // TODO: implement step
    });
    then('My Paradise sends the {subject} ticket to Zendesk', () => {
      // TODO: implement step
    });
    when('Zendesk creates the ticket', () => {
      // TODO: implement step
    });
    then('the ticket is created for the Customer', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: View Order History
 * Actor: Care
 */

story('View Order History', () => {
  scenario('View Order History', ({ given, when, then }) => {
    when('Care views Order History for the Customer', () => {
      // TODO: implement step
    });
    then('Care sees the product order with status badges', () => {
      // TODO: implement step
    });
  });

});
