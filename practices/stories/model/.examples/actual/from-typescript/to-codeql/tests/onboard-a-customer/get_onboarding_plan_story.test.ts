/**
 * Epic: Get Onboarding Plan
 * Orders: 0.0.2
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Load Plan Catalog
 */

story('Load Plan Catalog', () => {
  scenario('Load plan catalog', ({ given, when, then }) => {
    given('the plan catalog is available', () => {
      // TODO: implement step
    });
    when('My Paradise loads the plan catalog', () => {
      // TODO: implement step
    });
    then('the catalog includes Essentials, Data Freedom, Ace, and Atlas', () => {
      // TODO: implement step
    })
      .and('Internal Test Plan PROMO is excluded from the catalog', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Choose Onboarding Plan
 */

story('Choose Onboarding Plan', () => {
  scenario('Select a plan', ({ given, when, then }) => {
    given('no plan is in the Mavenir shopping cart', () => {
      // TODO: implement step
    });
    when('the Customer selects Essentials', () => {
      // TODO: implement step
    });
    then('My Paradise patches the Mavenir cart with the Essentials planId', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Pick Number', () => {
        // TODO: implement step
      });
    when('Mavenir confirms the cart is patched with Essentials', () => {
      // TODO: implement step
    });
    then('the cart bundle is a snapshot of Essentials loaded from the gateway', () => {
      // TODO: implement step
    });
  });

  scenario('Change an existing plan', ({ given, when, then }) => {
    given('Essentials is in the Mavenir shopping cart', () => {
      // TODO: implement step
    });
    when('the Customer selects Data Freedom', () => {
      // TODO: implement step
    });
    then('My Paradise patches the Mavenir cart with the Data Freedom planId', () => {
      // TODO: implement step
    });
    when('Mavenir confirms the cart is patched with Data Freedom', () => {
      // TODO: implement step
    });
    then('the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway', () => {
      // TODO: implement step
    });
  });

  scenario('Failed to update plan', ({ given, when, then }) => {
    given('the Mavenir cart patch returns an error', () => {
      // TODO: implement step
    });
    when('the Customer selects Essentials', () => {
      // TODO: implement step
    });
    then('the plan selection fails', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', () => {
      // TODO: implement step
    });
    then('the cart bundle remains empty', () => {
      // TODO: implement step
    });
  });

});
