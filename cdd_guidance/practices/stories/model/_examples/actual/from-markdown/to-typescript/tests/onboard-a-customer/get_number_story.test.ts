/**
 * Epic: Get Number
 * Orders: 0.0.2
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Determine Number
 * Actor: Customer
 */

// background-examples: {"held available number": {"available number": "available number", "example": "held available number", "number": "4415550100", "group": "available number"}, "chosen available number": {"available number": "available number", "example": "chosen available number", "number": "4415550101", "group": "available number"}, "James search": {"search term": "search term", "example": "James search", "input": "JAMES", "converted": "52637", "group": "search term"}}
story('Determine Number', () => {
  background('background', ({ given }) => {
  });

  scenario('View available numbers', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    but('no ++MSISDN++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('the Prospect proceeds to selecting their number', () => {
      // TODO: implement step
    });
    then('My Paradise loads ++available number++ inventory through the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list', () => {
        // TODO: implement step
      })
      .and('the Prospect can Bring your mobile number', () => {
        // TODO: implement step
      })
      .and('the Prospect can search for numbers (up to 5 characters: letters or numbers)', () => {
        // TODO: implement step
      })
      .and('the Prospect can Refresh', () => {
        // TODO: implement step
      })
      .and('the Continue operation is disabled', () => {
        // TODO: implement step
      });
    when('the Prospect selects ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    });
    then('the Continue operation is enabled', () => {
      // TODO: implement step
    });
  });

  scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('the Prospect proceeds to selecting their number', () => {
      // TODO: implement step
    });
    then('the Prospect sees their number is ++available number++ ++held available number++', () => {
      // TODO: implement step
    })
      .and('the Pick new number operation is disabled', () => {
        // TODO: implement step
      })
      .and('the Keep current number operation is enabled', () => {
        // TODO: implement step
      });
    when('the Prospect selects ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    });
    then('the Pick new number operation is enabled', () => {
      // TODO: implement step
    });
  });

  scenario('Refresh available numbers', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('the Prospect clicks Refresh', () => {
      // TODO: implement step
    });
    then('My Paradise loads a fresh set of ++available number++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect sees a new Available Number list', () => {
        // TODO: implement step
      })
      .and('the Continue operation is disabled', () => {
        // TODO: implement step
      });
  });

  scenario('Search for a number', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('the Prospect enters ++search term++ ++James search++ in the search field', () => {
      // TODO: implement step
    });
    then('the search field helper shows *Your number: JAMES (52637)*', () => {
      // TODO: implement step
    });
    when('the Prospect triggers the search', () => {
      // TODO: implement step
    });
    then('My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Query Msisdn Inventory
 */

story('Query Msisdn Inventory', () => {
  scenario('Query MSISDN inventory for porting', ({ given, when, then }) => {
    given('a ++PML customer++ is authenticated in Midtier', () => {
      // TODO: implement step
    })
      .and('++portability++ is in the portability request', () => {
        // TODO: implement step
      });
    when('Midtier queries ++MSISDN++ inventory for a temporary port-in number (`count: 1`)', () => {
      // TODO: implement step
    });
    then('Midtier queries Mavenir for 1 available ++MSISDN++ resource', () => {
      // TODO: implement step
    })
      .and('Midtier receives ++available number++ ++held available number++ as the temporary number', () => {
        // TODO: implement step
      });
  });

  scenario('Query MSISDN inventory', ({ given, when, then }) => {
    given('a ++PML customer++ is authenticated in Midtier', () => {
      // TODO: implement step
    });
    when('Midtier is asked to query ++MSISDN++ inventory', () => {
      // TODO: implement step
    });
    then('Midtier queries Mavenir for 5 available ++MSISDN++ resources', () => {
      // TODO: implement step
    })
      .and('Midtier returns a list of ++available number++ values to My Paradise', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: List Msisdn Resources
 */

story('List Msisdn Resources', () => {
  scenario('List MSISDN resources for porting', ({ given, when, then }) => {
    given('++MSISDN++ resources with available status are in the Mavenir inventory', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to list 1 ++MSISDN++ resource (`/updateAndGetAvailableResources`, `size: 1`)', () => {
      // TODO: implement step
    });
    then('Mavenir transitions 1 ++MSISDN++ resource from available to locked', () => {
      // TODO: implement step
    })
      .and('Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('List MSISDN resources', ({ given, when, then }) => {
    given('++MSISDN++ resources with available status are in the Mavenir inventory', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to list ++MSISDN++ resources (`/updateAndGetAvailableResources`, `size: 5`)', () => {
      // TODO: implement step
    });
    then('Mavenir transitions 5 ++MSISDN++ resources from available to locked', () => {
      // TODO: implement step
    })
      .and('Mavenir returns the list of locked ++available number++ values to Midtier', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Search Msisdn Inventory
 */

story('Search Msisdn Inventory', () => {
  scenario('Search MSISDN inventory', ({ given, when, then }) => {
    given('a ++PML customer++ is authenticated in Midtier', () => {
      // TODO: implement step
    });
    when('Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (`52637`)', () => {
      // TODO: implement step
    });
    then('Midtier queries Mavenir for available ++MSISDN++ resources matching `52637`', () => {
      // TODO: implement step
    })
      .and('Midtier returns matching ++available number++ values to My Paradise', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Search Msisdn Resources
 */

story('Search Msisdn Resources', () => {
  scenario('Search MSISDN resources by pattern', ({ given, when, then }) => {
    given('++MSISDN++ resources with available status are in the Mavenir inventory', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to search ++MSISDN++ resources with `pattern_search: 52637` (`/updateAndGetAvailableResources`)', () => {
      // TODO: implement step
    });
    then('Mavenir transitions matching ++MSISDN++ resources from available to locked', () => {
      // TODO: implement step
    })
      .and('Mavenir returns the matching ++available number++ values to Midtier', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Choose a Number
 * Actor: Customer
 */

story('Choose a Number', () => {
  scenario('Pick new number', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('the Prospect has selected ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    })
      .but('no ++MSISDN++ is in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      });
    when('the Prospect clicks Continue', () => {
      // TODO: implement step
    });
    then('My Paradise reserves ++available number++ ++chosen available number++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {
        // TODO: implement step
      })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Pick new number — replace existing', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('the Prospect has selected ++available number++ ++chosen available number++', () => {
        // TODO: implement step
      });
    when('the Prospect clicks Pick new number', () => {
      // TODO: implement step
    });
    then('My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {
        // TODO: implement step
      })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Keep current number', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    });
    when('the Prospect clicks Keep current number', () => {
      // TODO: implement step
    });
    then('the Prospect is forwarded to Select Sim', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Submit Reserve Number Request to Mid-Tier
 */

story('Submit Reserve Number Request to Mid-Tier', () => {
  scenario('Reserve number', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('++available number++ ++chosen available number++ is selected', () => {
      // TODO: implement step
    })
      .but('no ++MSISDN++ is in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      });
    when('My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    });
    then('Midtier returns 204', () => {
      // TODO: implement step
    })
      .and('My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Reserve number — replace existing', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('++available number++ ++chosen available number++ is selected', () => {
        // TODO: implement step
      });
    when('My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++', () => {
      // TODO: implement step
    });
    then('Midtier returns 204', () => {
      // TODO: implement step
    })
      .and('My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Reserve number request fails', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('++available number++ ++chosen available number++ is selected', () => {
      // TODO: implement step
    });
    when('My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    })
      .but('Midtier returns an error', () => {
        // TODO: implement step
      });
    then('My Paradise shows *Failed to reserve your number.*', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Submit Reserve Msisdn
 */

story('Submit Reserve Msisdn', () => {
  scenario('Reserve temporary MSISDN for porting', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++held available number++ is locked', () => {
      // TODO: implement step
    });
    when('Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (`portin: true`)', () => {
      // TODO: implement step
    });
    then('Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag', () => {
      // TODO: implement step
    })
      .and('Midtier returns 204', () => {
        // TODO: implement step
      });
  });

  scenario('Reserve MSISDN', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory', () => {
      // TODO: implement step
    });
    when('Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    });
    then('Midtier reserves ++available number++ ++chosen available number++ in Mavenir', () => {
      // TODO: implement step
    })
      .and('Midtier returns 204 to My Paradise', () => {
        // TODO: implement step
      });
  });

  scenario('Reserve MSISDN — release previous', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++chosen available number++ is locked', () => {
      // TODO: implement step
    })
      .and('++MSISDN++ ++available number++ ++held available number++ is reserved', () => {
        // TODO: implement step
      });
    when('Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++', () => {
      // TODO: implement step
    });
    then('Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir', () => {
      // TODO: implement step
    })
      .and('Midtier returns 204 to My Paradise', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Reserve Msisdn Resource
 */

story('Reserve Msisdn Resource', () => {
  scenario('Reserve MSISDN resource as temporary port-in number', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to reserve ++available number++ ++held available number++ with `kv_tempNumber: true` (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)', () => {
      // TODO: implement step
    });
    then('Mavenir transitions ++available number++ ++held available number++ from locked to reserved', () => {
      // TODO: implement step
    })
      .and('Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (`kv_tempNumber`)', () => {
        // TODO: implement step
      });
  });

  scenario('Reserve MSISDN resource', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to reserve ++available number++ ++chosen available number++ (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)', () => {
      // TODO: implement step
    });
    then('Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved', () => {
      // TODO: implement step
    })
      .and('Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++', () => {
        // TODO: implement step
      });
  });

  scenario('Reserve MSISDN resource — release previous', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++chosen available number++ is locked', () => {
      // TODO: implement step
    })
      .and('++MSISDN++ ++available number++ ++held available number++ is reserved', () => {
        // TODO: implement step
      });
    when('Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++', () => {
      // TODO: implement step
    });
    then('Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved', () => {
      // TODO: implement step
    })
      .and('Mavenir transitions ++available number++ ++held available number++ from reserved to available', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Submit Patch Cart With Number Request to Mid-Tier
 */

story('Submit Patch Cart With Number Request to Mid-Tier', () => {
  scenario('Patch cart with number', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++chosen available number++ has been reserved', () => {
      // TODO: implement step
    });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {
      // TODO: implement step
    });
    then('Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Patch cart with number fails', ({ given, when, then }) => {
    given('++MSISDN++ ++available number++ ++chosen available number++ has been reserved', () => {
      // TODO: implement step
    });
    when('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {
      // TODO: implement step
    })
      .but('Midtier returns an error', () => {
        // TODO: implement step
      });
    then('My Paradise shows *Failed to update your cart.*', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Patch Cart With Number
 */

story('Patch Cart With Number', () => {
  scenario('Patch cart with MSISDN', ({ given, when, then }) => {
    given('a ++PML customer++ with a ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('++MSISDN++ ++available number++ ++chosen available number++ has been reserved', () => {
        // TODO: implement step
      });
    when('Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++', () => {
      // TODO: implement step
    });
    then('Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic', () => {
      // TODO: implement step
    })
      .and('Midtier returns the updated ++PML customer++ to My Paradise', () => {
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
 * Story: Bring a Number
 */

// background-examples: {"valid portability": {"portability": "portability", "example": "valid portability", "donorOperator": "Digicel", "portNumber": "4412345678", "accountNumber": "12345", "userType": "Residential", "accountType": "Postpaid", "device": "Iphone", "group": "portability"}}
story('Bring a Number', () => {
  background('background', ({ given }) => {
  });

  scenario('Bring a number', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    but('no Transfer Code is on Bring your mobile number', () => {
      // TODO: implement step
    });
    when('the Prospect clicks Get started on Bring your mobile number', () => {
      // TODO: implement step
    });
    then('the Prospect can enter ++portability++', () => {
      // TODO: implement step
    })
      .and('the Prospect can confirm the information is accurate', () => {
        // TODO: implement step
      })
      .and('the Prospect can grant permission to Paradise Mobile to bring the number', () => {
        // TODO: implement step
      })
      .and('the Continue operation is disabled', () => {
        // TODO: implement step
      })
      .and('the Prospect can go Back', () => {
        // TODO: implement step
      });
    when('the Prospect enters ++portability++ ++valid portability++ and checks both permissions', () => {
      // TODO: implement step
    });
    then('the Continue operation is enabled', () => {
      // TODO: implement step
    });
    when('the Prospect clicks Continue', () => {
      // TODO: implement step
    });
    then('My Paradise submits ++portability++ ++valid portability++ to the Midtier', () => {
      // TODO: implement step
    })
      .and('Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++', () => {
        // TODO: implement step
      })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Number to be ported is incomplete', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('the Prospect leaves Number to be ported as the Bermuda prefix only', () => {
      // TODO: implement step
    });
    then('Number to be ported shows *Please enter the full Bermuda number.*', () => {
      // TODO: implement step
    })
      .and('the Continue operation stays disabled', () => {
        // TODO: implement step
      });
  });

  scenario('Provider not selected', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('the Prospect blurs Your current provider without selecting a provider', () => {
      // TODO: implement step
    });
    then('Your current provider shows *Please select a provider.*', () => {
      // TODO: implement step
    })
      .and('the Continue operation stays disabled', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Confirm Number Already With Paradise
 */

story('Confirm Number Already With Paradise', () => {
  scenario('Confirm the number is not already with Paradise', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the Prospect has entered ++portability++ ++valid portability++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('the Prospect proceeds to confirming whether their number is already with Paradise', () => {
      // TODO: implement step
    });
    then('the Prospect can confirm whether the ++MSISDN++ is already with Paradise', () => {
      // TODO: implement step
    });
    when('the Prospect confirms the ++MSISDN++ is not already with Paradise', () => {
      // TODO: implement step
    });
    then('My Paradise submits ++portability++ ++valid portability++ to the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Confirm the number is already with Paradise', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the Prospect has entered ++portability++ ++valid portability++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('the Prospect proceeds to confirming whether their number is already with Paradise', () => {
      // TODO: implement step
    });
    then('the Prospect can confirm whether the ++MSISDN++ is already with Paradise', () => {
      // TODO: implement step
    });
    when('the Prospect confirms the ++MSISDN++ is already with Paradise', () => {
      // TODO: implement step
    });
    then('++portability++ is not submitted to the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect is returned to selecting their number', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Evaluate Porting Two Factor Flag
 */

story('Evaluate Porting Two Factor Flag', () => {
  scenario('Porting two factor flag enabled (Intended)', ({ given, when, then }) => {
    given('`porting-2fa` is enabled in GrowthBook', () => {
      // TODO: implement step
    })
      .and('the Prospect is in Account Setup', () => {
        // TODO: implement step
      });
    when('GrowthBook evaluates the `porting-2fa` flag', () => {
      // TODO: implement step
    });
    then('My Paradise mounts the SMS verification step in the porting wizard', () => {
      // TODO: implement step
    })
      .and('My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified', () => {
        // TODO: implement step
      });
  });

  scenario('Porting two factor flag disabled (live)', ({ given, when, then }) => {
    given('`porting-2fa` is disabled in GrowthBook', () => {
      // TODO: implement step
    })
      .and('the Prospect is in Account Setup', () => {
        // TODO: implement step
      });
    when('GrowthBook evaluates the `porting-2fa` flag', () => {
      // TODO: implement step
    });
    then('My Paradise omits the SMS verification step from the porting wizard', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Submit Portability Request to Mid-Tier
 */

story('Submit Portability Request to Mid-Tier', () => {
  scenario('Submit portability request — porting-2fa off (live)', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('the Prospect has entered ++portability++ ++valid portability++', () => {
      // TODO: implement step
    });
    when('My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++', () => {
      // TODO: implement step
    });
    then('Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++', () => {
      // TODO: implement step
    })
      .and('My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Submit portability request — porting-2fa on, SMS sent (Intended)', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('the Prospect has entered ++portability++ ++valid portability++', () => {
      // TODO: implement step
    })
      .and('`porting-2fa` is enabled', () => {
        // TODO: implement step
      });
    when('My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++', () => {
      // TODO: implement step
    });
    then('Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`', () => {
      // TODO: implement step
    })
      .and('My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      })
      .and('My Paradise presents the Confirm your number for porting step', () => {
        // TODO: implement step
      });
  });

  scenario('Submit portability request — rate limited, bypass (Intended)', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    });
    when('My Paradise posts a ++portability request++', () => {
      // TODO: implement step
    })
      .but('Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`', () => {
        // TODO: implement step
      });
    then('My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Submit portability request — invalid number (Intended)', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    });
    when('My Paradise posts a ++portability request++', () => {
      // TODO: implement step
    })
      .but('Midtier returns `{ status: invalid_number }`', () => {
        // TODO: implement step
      });
    then('My Paradise shows *This number is invalid.* on Number to be ported', () => {
      // TODO: implement step
    });
  });

  scenario('Submit portability request fails', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .but('no ++portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    when('My Paradise posts a ++portability request++', () => {
      // TODO: implement step
    })
      .but('Midtier returns an error', () => {
        // TODO: implement step
      });
    then('My Paradise shows *Failed to save your portability.*', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Patch Cart With Portability
 */

story('Patch Cart With Portability', () => {
  scenario('Patch cart with portability', ({ given, when, then }) => {
    given('a ++PML customer++ with a ++Mavenir shopping cart++', () => {
      // TODO: implement step
    })
      .and('++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number', () => {
        // TODO: implement step
      })
      .and('++portability++ ++valid portability++ is in the request', () => {
        // TODO: implement step
      });
    when('Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++', () => {
      // TODO: implement step
    });
    then('Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)', () => {
      // TODO: implement step
    })
      .and('Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Send Port Verification
 */

story('Send Port Verification', () => {
  scenario('Send port verification SMS', ({ given, when, then }) => {
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    })
      .and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {
        // TODO: implement step
      });
    when('Midtier sends port verification to ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    });
    then('Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    })
      .and('Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise', () => {
        // TODO: implement step
      });
  });

  scenario('Send port verification — rate limited', ({ given, when, then }) => {
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    });
    when('Midtier sends port verification', () => {
      // TODO: implement step
    })
      .but('Twilio rate limits the request', () => {
        // TODO: implement step
      });
    then('Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise', () => {
      // TODO: implement step
    });
  });

  scenario('Send port verification — invalid number', ({ given, when, then }) => {
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    });
    when('Midtier sends port verification', () => {
      // TODO: implement step
    })
      .but('Twilio rejects the number as invalid', () => {
        // TODO: implement step
      });
    then('Midtier returns `{ status: invalid_number }` to My Paradise', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Send Verification Sms
 */

story('Send Verification Sms', () => {
  scenario('Send verification SMS', ({ given, when, then }) => {
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    })
      .and('++portability++ ++valid portability++ portNumber is a valid Bermuda number', () => {
        // TODO: implement step
      });
    when('Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    });
    then('Twilio creates a verification for ++portability++ ++valid portability++ portNumber (`channel: sms`)', () => {
      // TODO: implement step
    })
      .and('Twilio returns `sent` to Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Send verification SMS — rate limited', ({ given, when, then }) => {
    given('`porting-2fa` is enabled', () => {
      // TODO: implement step
    });
    when('Twilio is asked to send a verification SMS', () => {
      // TODO: implement step
    })
      .but('the rate limit for ++portability++ ++valid portability++ portNumber is exceeded', () => {
        // TODO: implement step
      });
    then('Twilio returns `rate_limited` to Midtier', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Enter Porting Sms Code
 */

// background-examples: {"valid porting SMS code": {"porting SMS code": "porting SMS code", "example": "valid porting SMS code", "code": "123456", "group": "porting SMS code"}, "mismatch porting SMS code": {"porting SMS code": "porting SMS code", "example": "mismatch porting SMS code", "code": "Invalid verification code.", "group": "porting SMS code"}, "example": {"porting SMS code": "porting SMS code", "example": "example", "code": "helper", "group": "porting SMS code"}}
story('Enter Porting Sms Code', () => {
  background('background', ({ given }) => {
  });

  scenario('Enter ++porting SMS code++', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('My Paradise has SMSed a ++porting SMS code++ through the Midtier', () => {
          // TODO: implement step
        });
    });
    when('the Prospect proceeds to confirming their number for porting', () => {
      // TODO: implement step
    });
    then('the Prospect sees the code was sent to the ++portability++ number', () => {
      // TODO: implement step
    })
      .and('the Prospect can enter ++porting SMS code++ in Enter SMS code', () => {
        // TODO: implement step
      })
      .and('the Prospect can Resend', () => {
        // TODO: implement step
      })
      .and('Resend is disabled for 30 seconds', () => {
        // TODO: implement step
      })
      .and('the Prospect can Change', () => {
        // TODO: implement step
      })
      .and('the Prospect can go Back', () => {
        // TODO: implement step
      })
      .and('the Verify code operation is disabled', () => {
        // TODO: implement step
      });
    when('the Prospect enters ++porting SMS code++ ++valid porting SMS code++', () => {
      // TODO: implement step
    });
    then('the Verify code operation is enabled', () => {
      // TODO: implement step
    });
    when('the Prospect clicks Verify code', () => {
      // TODO: implement step
    });
    then('My Paradise checks the ++porting SMS code++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Verify with unusable ++porting SMS code++', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('My Paradise has SMSed a ++porting SMS code++ through the Midtier', () => {
          // TODO: implement step
        });
    });
    when('the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++', () => {
      // TODO: implement step
    });
    then('Enter SMS code shows helper text *Invalid verification code.*', () => {
      // TODO: implement step
    });
  });

  scenario('Resend ++porting SMS code++', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Prospect is in Account Setup', () => {
        // TODO: implement step
      })
        .and('a ++My Paradise customer++ with a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('My Paradise has SMSed a ++porting SMS code++ through the Midtier', () => {
          // TODO: implement step
        });
    });
    when('the Prospect clicks Resend', () => {
      // TODO: implement step
    });
    then('My Paradise SMSes a ++porting SMS code++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('the Prospect sees *A new code was sent to* the ++portability++ number', () => {
        // TODO: implement step
      })
      .and('Resend is disabled for 30 seconds before it can be used again', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Check Port Verification
 */

story('Check Port Verification', () => {
  scenario('Check port verification — code valid', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('a ++PML customer++ with a ++Mavenir shopping cart++', () => {
        // TODO: implement step
      })
        .and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber', () => {
          // TODO: implement step
        });
    });
    when('Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    });
    then('Midtier checks the ++porting SMS code++ with Twilio', () => {
      // TODO: implement step
    })
      .and('Twilio returns `approved`', () => {
        // TODO: implement step
      })
      .and('Midtier marks the ++PML customer++ phone as verified', () => {
        // TODO: implement step
      })
      .and('Midtier returns `{ verified: true }` to My Paradise', () => {
        // TODO: implement step
      });
  });

  scenario('Check port verification — code mismatch', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('a ++PML customer++ with a ++Mavenir shopping cart++', () => {
        // TODO: implement step
      })
        .and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber', () => {
          // TODO: implement step
        });
    });
    when('Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    });
    then('Midtier checks the ++porting SMS code++ with Twilio', () => {
      // TODO: implement step
    })
      .and('Twilio returns a non-approved status', () => {
        // TODO: implement step
      })
      .and('Midtier returns `{ verified: false }` to My Paradise', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Check Verification
 */

story('Check Verification', () => {
  scenario('Check verification — code valid', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('a verification was sent to ++portability++ ++valid portability++ portNumber', () => {
        // TODO: implement step
      });
    });
    when('Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    });
    then('Twilio creates a verification check (`verificationChecks.create`)', () => {
      // TODO: implement step
    })
      .and('Twilio returns `approved` to Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Check verification — code mismatch', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('a verification was sent to ++portability++ ++valid portability++ portNumber', () => {
        // TODO: implement step
      });
    });
    when('Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {
      // TODO: implement step
    });
    then('Twilio creates a verification check', () => {
      // TODO: implement step
    })
      .and('Twilio returns a non-approved status to Midtier', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Keep Current Number
 * Actor: Customer
 */

story('Keep Current Number', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Sweep Stale Number Reservations
 * Actor: Care
 */

story('Sweep Stale Number Reservations', () => {
  scenario('Sweep stale number reservations', ({ given, when, then }) => {
    given('++MSISDN++ resources have been reserved but have no active order', () => {
      // TODO: implement step
    })
      .and('Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory', () => {
        // TODO: implement step
      });
    when('Care sweeps stale ++MSISDN++ reservations', () => {
      // TODO: implement step
    });
    then('Mavenir transitions the stale ++MSISDN++ resources from reserved to available', () => {
      // TODO: implement step
    })
      .and('the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory', () => {
        // TODO: implement step
      });
  });

});
