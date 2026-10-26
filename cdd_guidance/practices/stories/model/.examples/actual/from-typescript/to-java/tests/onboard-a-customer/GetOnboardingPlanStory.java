// Epic: Get Onboarding Plan
// Orders: 0.0.2

/** Story: Load Plan Catalog
 * SCENARIO: Load plan catalog
 * GIVEN: the plan catalog is available
 * WHEN: My Paradise loads the plan catalog
 * THEN: the catalog includes Essentials, Data Freedom, Ace, and Atlas
 * AND: Internal Test Plan PROMO is excluded from the catalog
 */

/** Story: Choose Onboarding Plan
 * SCENARIO: Select a plan
 * GIVEN: no plan is in the Mavenir shopping cart
 * WHEN: the Customer selects Essentials
 * THEN: My Paradise patches the Mavenir cart with the Essentials planId
 * AND: the Customer is forwarded to Pick Number
 * WHEN: Mavenir confirms the cart is patched with Essentials
 * THEN: the cart bundle is a snapshot of Essentials loaded from the gateway
 * SCENARIO: Change an existing plan
 * GIVEN: Essentials is in the Mavenir shopping cart
 * WHEN: the Customer selects Data Freedom
 * THEN: My Paradise patches the Mavenir cart with the Data Freedom planId
 * WHEN: Mavenir confirms the cart is patched with Data Freedom
 * THEN: the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway
 * SCENARIO: Failed to update plan
 * GIVEN: the Mavenir cart patch returns an error
 * WHEN: the Customer selects Essentials
 * THEN: the plan selection fails
 * WHEN: My Paradise reloads the shopping cart
 * THEN: the cart bundle remains empty
 */
