/**
 * Epic: Get Onboarding Plan
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Query Product Offerings And Map To Catalog
 */

story('Query Product Offerings And Map To Catalog', () => {
  scenario('Query Product Offerings And Map To Catalog', ({ given, when, then }) => {
    given('Mavenir has returned product offerings for service provider 100000000', () => {
      // TODO: implement step
    });
    when('Midtier is asked to query product offerings and map to catalog', () => {
      // TODO: implement step
    });
    then('Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++', () => {
      // TODO: implement step
    })
      .and('strips "PROMO" from ++plan++ ++Internal Test Plan PROMO++ name', () => {
        // TODO: implement step
      })
      .and('marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable', () => {
        // TODO: implement step
      })
      .and('marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable', () => {
        // TODO: implement step
      })
      .and('tags ++plan++ ++Ace++ as "Best value"', () => {
        // TODO: implement step
      })
      .and('returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: List Product Offerings
 */

story('List Product Offerings', () => {
  scenario('List Product Offerings', ({ given, when, then }) => {
    given('Mavenir catalog for service provider 100000000 is reachable', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to list product offerings with channelName CRM', () => {
      // TODO: implement step
    });
    then('Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Load Plan Catalog
 * Actor: My Paradise
 */

story('Load Plan Catalog', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Choose Onboarding Plan
 * Actor: Customer
 */

story('Choose Onboarding Plan', () => {
  scenario('Choose Onboarding Plan', ({ given, when, then }) => {
    then('no ++plan++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('Keep current plan is not shown', () => {
        // TODO: implement step
      });
    when('the Prospect is forwarded to Plan Selection', () => {
      // TODO: implement step
    });
    then('the system retrieves the ++plan++ catalog from the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++', () => {
        // TODO: implement step
      })
      .and('each ++plan++ has a Select operation', () => {
        // TODO: implement step
      });
    when('the Prospect clicks Select on ++plan++ ++{scenario}++', () => {
      // TODO: implement step
    });
    then('the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('the ++My Paradise customer++ cart is updated in session with ++{scenario}++', () => {
        // TODO: implement step
      })
      .and('the Prospect is forwarded to Time to pick your number', () => {
        // TODO: implement step
      });
  });

  scenario('Choose a different ++plan++', ({ given, when, then }) => {
    given('++plan++ ++Essentials++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('the Prospect arrives at Plan Selection from Checkout', () => {
      // TODO: implement step
    });
    then('the Prospect sees "Your current plan Essentials"', () => {
      // TODO: implement step
    })
      .and('Keep current plan is enabled', () => {
        // TODO: implement step
      })
      .and('the ++plan++ catalog is displayed', () => {
        // TODO: implement step
      })
      .and('each ++plan++ has a Select operation', () => {
        // TODO: implement step
      });
    when('the Prospect clicks Select on ++plan++ ++Data Freedom++', () => {
      // TODO: implement step
    });
    then('the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++', () => {
        // TODO: implement step
      })
      .and('the Prospect is forwarded to Checkout', () => {
        // TODO: implement step
      });
  });

  scenario('Select the ++plan++ already in the cart', ({ given, when, then }) => {
    given('++plan++ ++Essentials++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('the Prospect clicks Select on ++plan++ ++Essentials++', () => {
      // TODO: implement step
    });
    then('the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan', () => {
      // TODO: implement step
    });
  });

  scenario('Failed to update plan', ({ given, when, then }) => {
    given('Midtier PATCH to ++Mavenir shopping cart++ returns a server error', () => {
      // TODO: implement step
    });
    when('the Prospect clicks Select on ++plan++ ++Data Freedom++', () => {
      // TODO: implement step
    });
    then('My Paradise shows "Failed to update new plan choice."', () => {
      // TODO: implement step
    })
      .and('the Prospect stays on Plan Selection', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Patch Cart With Plan
 */

story('Patch Cart With Plan', () => {
  scenario('Patch Cart With Plan', ({ given, when, then }) => {
    given('a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir', () => {
      // TODO: implement step
    });
    when('Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++', () => {
      // TODO: implement step
    });
    then('Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir', () => {
      // TODO: implement step
    })
      .and('builds the cart item payload with the bundle product offering', () => {
        // TODO: implement step
      })
      .and('patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart', () => {
        // TODO: implement step
      })
      .and('returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan', () => {
        // TODO: implement step
      });
  });

  scenario('Patch Cart With Plan — portability plan name updated', ({ given, when, then }) => {
    given('a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir', () => {
      // TODO: implement step
    });
    when('Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected "Data Freedom"', () => {
      // TODO: implement step
    });
    then('Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to "Data Freedom"', () => {
      // TODO: implement step
    })
      .and('patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart', () => {
        // TODO: implement step
      })
      .and('returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Patch Shopping Cart
 */

story('Patch Shopping Cart', () => {
  scenario('Patch shopping cart with portability', ({ given, when, then }) => {
    given('a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics', () => {
      // TODO: implement step
    });
    then('Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)', () => {
      // TODO: implement step
    })
      .and('Mavenir returns the updated ++Mavenir shopping cart++ to Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Patch shopping cart with MSISDN', ({ given, when, then }) => {
    given('a ++Mavenir shopping cart++ with a plan bundle cart item', () => {
      // TODO: implement step
    })
      .but('no MSISDN characteristic on the cart item', () => {
        // TODO: implement step
      });
    when('Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic', () => {
      // TODO: implement step
    });
    then('Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic', () => {
      // TODO: implement step
    })
      .and('Mavenir returns the updated ++Mavenir shopping cart++ to Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Patch Shopping Cart', ({ given, when, then }) => {
    given('a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++', () => {
      // TODO: implement step
    });
    then('Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item', () => {
      // TODO: implement step
    })
      .and('returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Keep Current Plan
 */

story('Keep Current Plan', () => {
  scenario('Keep Current Plan', ({ given, when, then }) => {
    when('the Prospect clicks Keep current plan', () => {
      // TODO: implement step
    });
    then('the Prospect is forwarded to Checkout', () => {
      // TODO: implement step
    });
  });

});
