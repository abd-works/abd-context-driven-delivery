// Epic: Get Onboarding Plan
// Orders: 0.0.3

/** Story: Query Product Offerings And Map To Catalog
 * SCENARIO: Query Product Offerings And Map To Catalog
 * GIVEN: Mavenir has returned product offerings for service provider 100000000
 * WHEN: Midtier is asked to query product offerings and map to catalog
 * THEN: Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++
 * AND: strips "PROMO" from ++plan++ ++Internal Test Plan PROMO++ name
 * AND: marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable
 * AND: marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable
 * AND: tags ++plan++ ++Ace++ as "Best value"
 * AND: returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan
 */

/** Story: List Product Offerings
 * SCENARIO: List Product Offerings
 * GIVEN: Mavenir catalog for service provider 100000000 is reachable
 * WHEN: Mavenir is asked to list product offerings with channelName CRM
 * THEN: Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering
 */

/** Story: Choose Onboarding Plan
 * Actor: Customer
 * SCENARIO: Choose Onboarding Plan
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * BUT: no ++plan++ is in the ++Mavenir shopping cart++
 * AND: Keep current plan is not shown
 * WHEN: the Prospect is forwarded to Plan Selection
 * THEN: the system retrieves the ++plan++ catalog from the Midtier
 * AND: the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++
 * AND: each ++plan++ has a Select operation
 * WHEN: the Prospect clicks Select on ++plan++ ++{scenario}++
 * THEN: the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier
 * AND: the ++My Paradise customer++ cart is updated in session with ++{scenario}++
 * AND: the Prospect is forwarded to Time to pick your number
 * SCENARIO: Choose a different ++plan++
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect arrives at Plan Selection from Checkout
 * THEN: the Prospect sees "Your current plan Essentials"
 * AND: Keep current plan is enabled
 * AND: the ++plan++ catalog is displayed
 * AND: each ++plan++ has a Select operation
 * WHEN: the Prospect clicks Select on ++plan++ ++Data Freedom++
 * THEN: the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier
 * AND: the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++
 * AND: the Prospect is forwarded to Checkout
 * SCENARIO: Select the ++plan++ already in the cart
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect clicks Select on ++plan++ ++Essentials++
 * THEN: the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan
 * SCENARIO: Failed to update plan
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: Midtier PATCH to ++Mavenir shopping cart++ returns a server error
 * WHEN: the Prospect clicks Select on ++plan++ ++Data Freedom++
 * THEN: My Paradise shows "Failed to update new plan choice."
 * AND: the Prospect stays on Plan Selection
 */

/** Story: Patch Cart With Plan
 * SCENARIO: Patch Cart With Plan
 * GIVEN: a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
 * WHEN: Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++
 * THEN: Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir
 * AND: builds the cart item payload with the bundle product offering
 * AND: patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart
 * AND: returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan
 * SCENARIO: Patch Cart With Plan — portability plan name updated
 * GIVEN: a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir
 * WHEN: Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected "Data Freedom"
 * THEN: Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to "Data Freedom"
 * AND: patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart
 * AND: returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName
 */

/** Story: Patch Shopping Cart
 * SCENARIO: Patch shopping cart with portability
 * GIVEN: a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++
 * WHEN: Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics
 * THEN: Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)
 * AND: Mavenir returns the updated ++Mavenir shopping cart++ to Midtier
 * SCENARIO: Patch shopping cart with MSISDN
 * GIVEN: a ++Mavenir shopping cart++ with a plan bundle cart item
 * BUT: no MSISDN characteristic on the cart item
 * WHEN: Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic
 * THEN: Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic
 * AND: Mavenir returns the updated ++Mavenir shopping cart++ to Midtier
 * SCENARIO: Patch Shopping Cart
 * GIVEN: a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
 * WHEN: Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++
 * THEN: Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item
 * AND: returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan
 */

/** Story: Keep Current Plan
 * SCENARIO: Keep Current Plan
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: And | ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect clicks Keep current plan
 * THEN: the Prospect is forwarded to Checkout
 */
