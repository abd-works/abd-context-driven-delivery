/**
 * Epic: Get Onboarding Plan
 * Orders: 0.0.2
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Load Plan Catalog
 */

story('Load Plan Catalog', () => {
    scenario('Load plan catalog', ({ given, when, then }) => {
      given('the plan catalog is available', () => {});
      when('My Paradise loads the plan catalog', () => {});
      then('the catalog includes Essentials, Data Freedom, Ace, and Atlas', () => {}).and('Internal Test Plan PROMO is excluded from the catalog', () => {});
    });
});

/**
 * Story: Choose Onboarding Plan
 */

story('Choose Onboarding Plan', () => {
    scenario('Select a plan', ({ given, when, then }) => {
      given('no plan is in the Mavenir shopping cart', () => {});
      when('the Customer selects Essentials', () => {});
      then('My Paradise patches the Mavenir cart with the Essentials planId', () => {}).and('the Customer is forwarded to Pick Number', () => {});
      when('Mavenir confirms the cart is patched with Essentials', () => {});
      then('the cart bundle is a snapshot of Essentials loaded from the gateway', () => {});
    });
    scenario('Change an existing plan', ({ given, when, then }) => {
      given('Essentials is in the Mavenir shopping cart', () => {});
      when('the Customer selects Data Freedom', () => {});
      then('My Paradise patches the Mavenir cart with the Data Freedom planId', () => {});
      when('Mavenir confirms the cart is patched with Data Freedom', () => {});
      then('the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway', () => {});
    });
    scenario('Failed to update plan', ({ given, when, then }) => {
      given('the Mavenir cart patch returns an error', () => {});
      when('the Customer selects Essentials', () => {});
      then('the plan selection fails', () => {});
      when('My Paradise reloads the shopping cart', () => {});
      then('the cart bundle remains empty', () => {});
    });
});
