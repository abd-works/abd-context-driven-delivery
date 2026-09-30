/**
 * Epic: Get Order Review
 * Orders: 0.0.6
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Check The Order
 * Actor: Customer
 */

story('Check The Order', () => {
    scenario('Check the order', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
      // background-step: And | ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
      // background-step: And | the Customer has chosen eSIM
      given('the Customer has completed account setup, number, SIM, and profile', () => {});
      when('the Customer proceeds to reviewing their order', () => {});
      then('the Customer is forwarded to Checkout', () => {}).and('the Checkout step is the next onboarding step', () => {});
    });
    scenario('Check the order with port-in number', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
      // background-step: And | ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
      // background-step: And | the Customer has chosen eSIM
      given('the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN', () => {});
      when('the Customer proceeds to reviewing their order', () => {});
      then('the Customer is forwarded to Checkout', () => {}).and('the Checkout step is the next onboarding step', () => {});
    });
});

/**
 * Story: Upgrade To Data Freedom
 * Actor: Customer
 */

// background-examples: {"upgrade to Data Freedom": {"plan upgrade": "plan upgrade", "example": "upgrade to Data Freedom", "currentPlan": "Essentials", "newPlan": "Data Freedom"}, "upgrade to Ace": {"plan upgrade": "plan upgrade", "example": "upgrade to Ace", "currentPlan": "Data Freedom", "newPlan": "Ace"}, "upgrade to Atlas": {"plan upgrade": "plan upgrade", "example": "upgrade to Atlas", "currentPlan": "Ace", "newPlan": "Atlas"}}
story('Upgrade To Data Freedom', () => {
  background('background', ({ given }) => {
  });
    scenario('Upgrade plan from review', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer is reviewing their order
      // background-step: And | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      given('++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++', () => {});
      when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++', () => {});
      then('My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId', () => {});
      when('Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++', () => {});
      then('My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle', () => {}).and('the Customer sees *You have been upgraded!*', () => {});
    });
    scenario('No upsell shown on top-tier plan', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer is reviewing their order
      // background-step: And | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++
      given('++plan++ ++Atlas++ is in the ++Mavenir shopping cart++', () => {});
      when('the Customer proceeds to reviewing their order', () => {});
      then('no upgrade option is available', () => {});
    });
});

/**
 * Story: Change Plan From Review
 * Actor: Customer
 */

story('Change Plan From Review', () => {
    scenario('Select a different plan from review', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer is reviewing their order
      // background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
      given('the Customer has opened plan selection from review', () => {});
      when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {});
      then('My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId', () => {});
      when('Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {});
      then('My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle', () => {}).and('the Customer is forwarded to Checkout', () => {});
    });
    scenario('Keep current plan from review', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer is reviewing their order
      // background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
      given('the Customer has opened plan selection from review', () => {});
      when('the Customer keeps their current plan', () => {});
      then('the Customer is forwarded to Checkout', () => {});
    });
    scenario('Select the plan already in the cart from review', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer is reviewing their order
      // background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
      given('the Customer has opened plan selection from review', () => {});
      when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++', () => {});
      then('the cart bundle remains ++plan++ ++Essentials++', () => {});
    });
    scenario('Plan update fails from review', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the Customer is reviewing their order
      // background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
      given('the Customer has opened plan selection from review', () => {}).and('Mavenir returns an error on cart patch', () => {});
      when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {});
      then('My Paradise shows *Failed to update new plan choice.*', () => {}).and('the cart bundle remains ++plan++ ++Essentials++', () => {});
    });
});
