/**
 * Epic: Get Onboarding Plan
 * Orders: 0.0.3
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Query Product Offerings And Map To Catalog
 */

story('Query Product Offerings And Map To Catalog', () => {
    scenario('Query Product Offerings And Map To Catalog', ({ given, when, then }) => {
      given('Mavenir has returned product offerings for service provider 100000000', () => {});
      when('Midtier is asked to query product offerings and map to catalog', () => {});
      then('Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++', () => {}).and('strips "PROMO" from ++plan++ ++Internal Test Plan PROMO++ name', () => {}).and('marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable', () => {}).and('marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable', () => {}).and('tags ++plan++ ++Ace++ as "Best value"', () => {}).and('returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan', () => {});
    });
});

/**
 * Story: List Product Offerings
 */

story('List Product Offerings', () => {
    scenario('List Product Offerings', ({ given, when, then }) => {
      given('Mavenir catalog for service provider 100000000 is reachable', () => {});
      when('Mavenir is asked to list product offerings with channelName CRM', () => {});
      then('Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering', () => {});
    });
});

/**
 * Story: Choose Onboarding Plan
 * Actor: Customer
 */

story('Choose Onboarding Plan', () => {
    scenario('Choose Onboarding Plan', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Prospect is in Account Setup
      // background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      but('no ++plan++ is in the ++Mavenir shopping cart++', () => {}).and('Keep current plan is not shown', () => {});
      when('the Prospect is forwarded to Plan Selection', () => {});
      then('the system retrieves the ++plan++ catalog from the Midtier', () => {}).and('the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++', () => {}).and('each ++plan++ has a Select operation', () => {});
      when('the Prospect clicks Select on ++plan++ ++{scenario}++', () => {});
      then('the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier', () => {}).and('the ++My Paradise customer++ cart is updated in session with ++{scenario}++', () => {}).and('the Prospect is forwarded to Time to pick your number', () => {});
    });
    scenario('Choose a different ++plan++', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Prospect is in Account Setup
      // background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      given('++plan++ ++Essentials++ is in the ++Mavenir shopping cart++', () => {});
      when('the Prospect arrives at Plan Selection from Checkout', () => {});
      then('the Prospect sees "Your current plan Essentials"', () => {}).and('Keep current plan is enabled', () => {}).and('the ++plan++ catalog is displayed', () => {}).and('each ++plan++ has a Select operation', () => {});
      when('the Prospect clicks Select on ++plan++ ++Data Freedom++', () => {});
      then('the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier', () => {}).and('the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++', () => {}).and('the Prospect is forwarded to Checkout', () => {});
    });
    scenario('Select the ++plan++ already in the cart', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Prospect is in Account Setup
      // background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      given('++plan++ ++Essentials++ is in the ++Mavenir shopping cart++', () => {});
      when('the Prospect clicks Select on ++plan++ ++Essentials++', () => {});
      then('the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan', () => {});
    });
    scenario('Failed to update plan', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Prospect is in Account Setup
      // background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      given('Midtier PATCH to ++Mavenir shopping cart++ returns a server error', () => {});
      when('the Prospect clicks Select on ++plan++ ++Data Freedom++', () => {});
      then('My Paradise shows "Failed to update new plan choice."', () => {}).and('the Prospect stays on Plan Selection', () => {});
    });
});

/**
 * Story: Patch Cart With Plan
 */

story('Patch Cart With Plan', () => {
    scenario('Patch Cart With Plan', ({ given, when, then }) => {
      given('a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir', () => {});
      when('Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++', () => {});
      then('Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir', () => {}).and('builds the cart item payload with the bundle product offering', () => {}).and('patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart', () => {}).and('returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan', () => {});
    });
    scenario('Patch Cart With Plan — portability plan name updated', ({ given, when, then }) => {
      given('a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir', () => {});
      when('Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected "Data Freedom"', () => {});
      then('Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to "Data Freedom"', () => {}).and('patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart', () => {}).and('returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName', () => {});
    });
});

/**
 * Story: Patch Shopping Cart
 */

story('Patch Shopping Cart', () => {
    scenario('Patch shopping cart with portability', ({ given, when, then }) => {
      given('a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++', () => {});
      when('Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics', () => {});
      then('Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)', () => {}).and('Mavenir returns the updated ++Mavenir shopping cart++ to Midtier', () => {});
    });
    scenario('Patch shopping cart with MSISDN', ({ given, when, then }) => {
      given('a ++Mavenir shopping cart++ with a plan bundle cart item', () => {}).but('no MSISDN characteristic on the cart item', () => {});
      when('Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic', () => {});
      then('Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic', () => {}).and('Mavenir returns the updated ++Mavenir shopping cart++ to Midtier', () => {});
    });
    scenario('Patch Shopping Cart', ({ given, when, then }) => {
      given('a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir', () => {});
      when('Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++', () => {});
      then('Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item', () => {}).and('returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan', () => {});
    });
});

/**
 * Story: Keep Current Plan
 */

story('Keep Current Plan', () => {
    scenario('Keep Current Plan', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Prospect is in Account Setup
      // background-step: And | the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      // background-step: And | ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
      when('the Prospect clicks Keep current plan', () => {});
      then('the Prospect is forwarded to Checkout', () => {});
    });
});
