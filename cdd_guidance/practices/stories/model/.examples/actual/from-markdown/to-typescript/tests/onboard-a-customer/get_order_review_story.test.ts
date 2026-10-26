/**
 * Epic: Get Order Review
 * Orders: 0.0.6
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Check The Order
 * Actor: Customer
 */

story('Check The Order', () => {
  scenario('Check the order', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      })
        .and('++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the Customer has chosen eSIM', () => {
          // TODO: implement step
        });
    });
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
    background('background', ({ given }) => {
      given('the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      })
        .and('++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the Customer has chosen eSIM', () => {
          // TODO: implement step
        });
    });
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

// background-examples: {"upgrade to Data Freedom": {"plan upgrade": "plan upgrade", "example": "upgrade to Data Freedom", "currentPlan": "Essentials", "newPlan": "Data Freedom"}, "upgrade to Ace": {"plan upgrade": "plan upgrade", "example": "upgrade to Ace", "currentPlan": "Data Freedom", "newPlan": "Ace"}, "upgrade to Atlas": {"plan upgrade": "plan upgrade", "example": "upgrade to Atlas", "currentPlan": "Ace", "newPlan": "Atlas"}}
story('Upgrade To Data Freedom', () => {
  background('background', ({ given }) => {
  });

  scenario('Upgrade plan from review', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is reviewing their order', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
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
      .and('the Customer sees *You have been upgraded!*', () => {
        // TODO: implement step
      });
  });

  scenario('No upsell shown on top-tier plan', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is reviewing their order', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
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
    background('background', ({ given }) => {
      given('the Customer is reviewing their order', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
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
    background('background', ({ given }) => {
      given('the Customer is reviewing their order', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
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
    background('background', ({ given }) => {
      given('the Customer is reviewing their order', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
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
    background('background', ({ given }) => {
      given('the Customer is reviewing their order', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('the Customer has opened plan selection from review', () => {
      // TODO: implement step
    })
      .and('Mavenir returns an error on cart patch', () => {
        // TODO: implement step
      });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++', () => {
      // TODO: implement step
    });
    then('My Paradise shows *Failed to update new plan choice.*', () => {
      // TODO: implement step
    })
      .and('the cart bundle remains ++plan++ ++Essentials++', () => {
        // TODO: implement step
      });
  });

});
