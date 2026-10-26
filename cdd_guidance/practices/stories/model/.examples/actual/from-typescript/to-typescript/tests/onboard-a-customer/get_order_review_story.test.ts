/**
 * Epic: Get Order Review
 * Orders: 0.0.3
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Check The Order
 */

story('Check The Order', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Upgrade To Data Freedom
 */

story('Upgrade To Data Freedom', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Change Plan From Review
 */

story('Change Plan From Review', () => {
  scenario('Select a different plan from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review with Essentials in the cart', () => {
      // TODO: implement step
    });
    when('My Paradise patches the Mavenir shopping cart with Data Freedom', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with Data Freedom', () => {
      // TODO: implement step
    });
    then('My Paradise stores Data Freedom as the cart bundle loaded from the gateway', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // TODO: implement step
      });
  });

  scenario('Keep current plan from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review with Essentials in the cart', () => {
      // TODO: implement step
    });
    when('the Customer keeps their current plan', () => {
      // TODO: implement step
    });
    then('the cart bundle remains Essentials', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // TODO: implement step
      });
  });

  scenario('Plan update fails from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review with Essentials in the cart', () => {
      // TODO: implement step
    });
    when('My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error', () => {
      // TODO: implement step
    });
    then('My Paradise shows Failed to update new plan choice.', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', () => {
      // TODO: implement step
    });
    then('the cart bundle remains Essentials', () => {
      // TODO: implement step
    });
  });

});
