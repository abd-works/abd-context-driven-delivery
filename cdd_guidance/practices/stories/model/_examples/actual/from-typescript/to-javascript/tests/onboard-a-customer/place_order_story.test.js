/**
 * Epic: Place Order
 * Orders: 0.0.9
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Create Billing Account
 */

story('Create Billing Account', () => {
    scenario('Create billing account', ({ given, when, then }) => {
      given('the Customer has a configured cart and no billing account', () => {});
      when('the Customer creates a billing account', () => {});
      then('My Paradise sends the billing account request to Mavenir', () => {});
      when('Mavenir creates the billing account', () => {});
      then('the Customer has a billing account', () => {}).and('the Customer is on the Done step', () => {});
    });
    scenario('Billing account already exists', ({ given, when, then }) => {
      given('the Customer already has a billing account', () => {});
      when('the Customer creates a billing account', () => {});
      then('the billing account is rejected', () => {}).and('Mavenir does not receive a billing account request', () => {});
    });
    scenario('Billing account creation fails', ({ given, when, then }) => {
      given('Mavenir returns an error for the billing account request', () => {});
      when('the Customer creates a billing account', () => {});
      then('the billing account cannot be created', () => {});
      when('My Paradise reloads the customer', () => {});
      then('the Customer has no billing account', () => {});
    });
});

/**
 * Story: Create Product Order
 */

story('Create Product Order', () => {
    scenario('Create product order', ({ given, when, then }) => {
      given('the Customer is verified and has a billing account, plan, number, and eSIM', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise sends the product order request to Mavenir', () => {});
      when('Mavenir creates the product order', () => {});
      then('the order succeeded with pay-up-front', () => {}).and('the Customer onboarding is done', () => {});
    });
    scenario('Pay-up-front charge fails', ({ given, when, then }) => {
      given('the pay-up-front charge fails', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise does not send a product order to Mavenir', () => {});
      when('My Paradise reloads the cart', () => {});
      then('the order succeeded without pay-up-front', () => {});
    });
    scenario('Product order fails', ({ given, when, then }) => {
      given('Mavenir returns an error for the product order', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise sends the product order request to Mavenir', () => {});
      when('My Paradise reloads the cart', () => {});
      then('the order did not succeed', () => {});
    });
    scenario('Onboarding is already done', ({ given, when, then }) => {
      given('the Customer onboarding is already done', () => {});
      when('the Customer places the product order', () => {});
      then('the product order is rejected', () => {}).and('Mavenir does not receive a product order request', () => {});
    });
    scenario('Unverified with no bypass and no portability', ({ given, when, then }) => {
      given('the Customer is not verified and the plan does not bypass verification', () => {});
      when('the Customer places the product order', () => {});
      then('My Paradise does not send a product order to Mavenir', () => {}).and('the cart is marked to submit the order later', () => {});
      when('My Paradise reloads the cart', () => {});
      then('the Customer onboarding is done', () => {});
    });
});
