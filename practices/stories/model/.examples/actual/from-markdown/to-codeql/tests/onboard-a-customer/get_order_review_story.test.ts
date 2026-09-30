/**
 * Epic: Get Order Review
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Check The Order
 * Actor: Customer
 */

story('Check The Order', () => {
  scenario('Check the order', ({ given, when, then }) => {
    given('the Customer has completed account setup, number, SIM, and profile', () => {
      // TODO: implement step
    });
    when('the Customer proceeds to reviewing their order', () => {
      // TODO: implement step
    });
    then('the Customer is forwarded to Checkout', () => {
      // TODO: implement step
    })
      .and('the Checkout step is the next onboarding step', () => {
        // TODO: implement step
      });
  });

  scenario('Check the order with port-in number', ({ given, when, then }) => {
    given('the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN', () => {
      // TODO: implement step
    });
    when('the Customer proceeds to reviewing their order', () => {
      // TODO: implement step
    });
    then('the Customer is forwarded to Checkout', () => {
      // TODO: implement step
    })
      .and('the Checkout step is the next onboarding step', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Upgrade To Data Freedom
 * Actor: Customer
 */

story('Upgrade To Data Freedom', () => {
  scenario('Upgrade plan from review', ({ given, when, then }) => {
    given('++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle', () => {
      // TODO: implement step
    })
      .and('the Customer sees You have been upgraded!', () => {
        // TODO: implement step
      });
  });

  scenario('No upsell shown on top-tier plan', ({ given, when, then }) => {
    given('++plan++ ++Atlas++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('the Customer proceeds to reviewing their order', () => {
      // TODO: implement step
    });
    then('no upgrade option is available', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Change Plan From Review
 * Actor: Customer
 */

story('Change Plan From Review', () => {
  scenario('Select a different plan from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review', () => {
      // TODO: implement step
    });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // TODO: implement step
      });
  });

  scenario('Keep current plan from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review', () => {
      // TODO: implement step
    });
    when('the Customer keeps their current plan', () => {
      // TODO: implement step
    });
    then('the Customer is forwarded to Checkout', () => {
      // TODO: implement step
    });
  });

  scenario('Select the plan already in the cart from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review', () => {
      // TODO: implement step
    });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++', () => {
      // TODO: implement step
    });
    then('the cart bundle remains ++plan++ ++Essentials++', () => {
      // TODO: implement step
    });
  });

  scenario('Plan update fails from review', ({ given, when, then }) => {
    given('the Customer has opened plan selection from review', () => {
      // TODO: implement step
    })
      .and('Mavenir returns an error on cart patch', () => {
        // TODO: implement step
      });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {
      // TODO: implement step
    });
    then('My Paradise shows Failed to update new plan choice.', () => {
      // TODO: implement step
    })
      .and('the cart bundle remains ++plan++ ++Essentials++', () => {
        // TODO: implement step
      });
  });

});
