/**
 * Epic: Get Order Review
 * Orders: 0.0.3
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Change Plan From Review
 */

story('Change Plan From Review', () => {
    scenario('Select a different plan from review', ({ given, when, then }) => {
      given('the Customer has opened plan selection from review with Essentials in the cart', () => {});
      when('My Paradise patches the Mavenir shopping cart with Data Freedom', () => {});
      then('My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId', () => {});
      when('Mavenir returns the updated Mavenir shopping cart with Data Freedom', () => {});
      then('My Paradise stores Data Freedom as the cart bundle loaded from the gateway', () => {}).and('the Customer is forwarded to Checkout', () => {});
    });
    scenario('Keep current plan from review', ({ given, when, then }) => {
      given('the Customer has opened plan selection from review with Essentials in the cart', () => {});
      when('the Customer keeps their current plan', () => {});
      then('the cart bundle remains Essentials', () => {}).and('the Customer is forwarded to Checkout', () => {});
    });
    scenario('Plan update fails from review', ({ given, when, then }) => {
      given('the Customer has opened plan selection from review with Essentials in the cart', () => {});
      when('My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error', () => {});
      then('My Paradise shows Failed to update new plan choice.', () => {});
      when('My Paradise reloads the shopping cart', () => {});
      then('the cart bundle remains Essentials', () => {});
    });
});
