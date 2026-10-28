/**
 * Epic: Place Order
 * Orders: 0.0.8
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Create Billing Account
 * Actor: My Paradise
 */

story('Create Billing Account', () => {
    scenario('Create billing account', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a configured cart
      // background-step: But | the Customer has no billing account
      when('the Customer creates a billing account', () => {});
      then('My Paradise sends the billing account request to Mavenir', () => {});
      when('Mavenir creates the billing account', () => {});
      then('the Customer has a billing account', () => {}).and('the Customer is on the Done step', () => {});
    });
    scenario('Billing account already exists', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a configured cart
      // background-step: But | the Customer has no billing account
      given('the Customer already has a billing account', () => {});
      when('the Customer creates a billing account', () => {});
      then('the billing account is rejected', () => {}).and('Mavenir does not receive a billing account request', () => {});
    });
    scenario('Billing account creation fails', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a configured cart
      // background-step: But | the Customer has no billing account
      given('Mavenir returns an error for the billing account request', () => {});
      when('the Customer creates a billing account', () => {});
      then('the billing account cannot be created', () => {}).and('the Customer has no billing account', () => {});
    });
});

/**
 * Story: Create Product Order
 * Actor: My Paradise
 */

story('Create Product Order', () => {
    scenario('Create product order', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a billing account
      // background-step: And | the cart has plan, number, and SIM
      given('the Customer is verified', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise sends the product order request to Mavenir', () => {});
      when('Mavenir creates the product order', () => {});
      then('the order succeeded with pay-up-front', () => {}).and('the Customer onboarding is done', () => {});
    });
    scenario('Pay-up-front charge fails', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a billing account
      // background-step: And | the cart has plan, number, and SIM
      given('the pay-up-front charge fails', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise does not send a product order to Mavenir', () => {}).and('the order succeeded without pay-up-front', () => {});
    });
    scenario('Product order fails', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a billing account
      // background-step: And | the cart has plan, number, and SIM
      given('Mavenir returns an error for the product order', () => {});
      when('the Customer places the product order', () => {});
      then('the order did not succeed', () => {});
    });
    scenario('Onboarding is already done', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a billing account
      // background-step: And | the cart has plan, number, and SIM
      given('the Customer onboarding is already done', () => {});
      when('the Customer places the product order', () => {});
      then('the product order is rejected', () => {}).and('Mavenir does not receive a product order request', () => {});
    });
    scenario('Unverified with no bypass and no portability', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a billing account
      // background-step: And | the cart has plan, number, and SIM
      given('the Customer is not verified', () => {}).and('the plan does not bypass verification', () => {}).and('the cart has no portability', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise does not send a product order to Mavenir', () => {}).and('the cart is marked to submit the order later', () => {}).and('the Customer onboarding is done', () => {});
    });
});

/**
 * Story: View Order Result
 * Actor: Customer
 */

story('View Order Result', () => {
    scenario('View order result', ({ given, when, then }) => {
      given('the order result is {example}', () => {});
      when('the Customer views their order result', () => {});
      then('the order is {outcome}', () => {});
    });
});

/**
 * Story: Create Order Ticket
 * Actor: My Paradise
 */

story('Create Order Ticket', () => {
    scenario('Create order ticket', ({ given, when, then }) => {
      given('the Customer {example}', () => {});
      when('the Customer creates the order ticket', () => {});
      then('My Paradise sends the {subject} ticket to Zendesk', () => {});
      when('Zendesk creates the ticket', () => {});
      then('the ticket is created for the Customer', () => {});
    });
});

/**
 * Story: View Order History
 * Actor: Care
 */

story('View Order History', () => {
    scenario('View Order History', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a product order in Mavenir
      // background-step: And | Care is in Customer Management → Order History
      when('Care views Order History for the Customer', () => {});
      then('Care sees the product order with status badges', () => {});
    });
});
