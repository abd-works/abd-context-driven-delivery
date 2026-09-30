/**
 * Epic: Get Number
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Determine Number
 * Actor: Customer
 */

story('Determine Number', () => {
  background('each', ({ given }) => {
    scenario('View available numbers', ({ given, when, then }) => {
      then('no ++MSISDN++ is in the ++Mavenir shopping cart++', () => {});
      when('the Prospect proceeds to selecting their number', () => {});
      then('My Paradise loads ++available number++ inventory through the Midtier', () => {}).and('the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list', () => {}).and('the Prospect can Bring your mobile number', () => {}).and('the Prospect can search for numbers (up to 5 characters: letters or numbers)', () => {}).and('the Prospect can Refresh', () => {}).and('the Continue operation is disabled', () => {});
      when('the Prospect selects ++available number++ ++chosen available number++', () => {});
      then('the Continue operation is enabled', () => {});
    });
    scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {});
      when('the Prospect proceeds to selecting their number', () => {});
      then('the Prospect sees their number is ++available number++ ++held available number++', () => {}).and('the Pick new number operation is disabled', () => {}).and('the Keep current number operation is enabled', () => {});
      when('the Prospect selects ++available number++ ++chosen available number++', () => {});
      then('the Pick new number operation is enabled', () => {});
    });
    scenario('Refresh available numbers', ({ given, when, then }) => {
      when('the Prospect clicks Refresh', () => {});
      then('My Paradise loads a fresh set of ++available number++ through the Midtier', () => {}).and('the Prospect sees a new Available Number list', () => {}).and('the Continue operation is disabled', () => {});
    });
    scenario('Search for a number', ({ given, when, then }) => {
      when('the Prospect enters ++search term++ ++James search++ in the search field', () => {});
      then('the search field helper shows Your number: JAMES (52637)', () => {});
      when('the Prospect triggers the search', () => {});
      then('My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier', () => {});
    });
  });
});

/**
 * Story: Query Msisdn Inventory
 */

story('Query Msisdn Inventory', () => {
  background('each', ({ given }) => {
    scenario('Query MSISDN inventory for porting', ({ given, when, then }) => {
      given('a ++PML customer++ is authenticated in Midtier', () => {}).and('++portability++ is in the portability request', () => {});
      when('Midtier queries ++MSISDN++ inventory for a temporary port-in number (count: 1)', () => {});
      then('Midtier queries Mavenir for 1 available ++MSISDN++ resource', () => {}).and('Midtier receives ++available number++ ++held available number++ as the temporary number', () => {});
    });
    scenario('Query MSISDN inventory', ({ given, when, then }) => {
      given('a ++PML customer++ is authenticated in Midtier', () => {});
      when('Midtier is asked to query ++MSISDN++ inventory', () => {});
      then('Midtier queries Mavenir for 5 available ++MSISDN++ resources', () => {}).and('Midtier returns a list of ++available number++ values to My Paradise', () => {});
    });
  });
});

/**
 * Story: List Msisdn Resources
 */

story('List Msisdn Resources', () => {
  background('each', ({ given }) => {
    scenario('List MSISDN resources for porting', ({ given, when, then }) => {
      given('++MSISDN++ resources with available status are in the Mavenir inventory', () => {});
      when('Mavenir is asked to list 1 ++MSISDN++ resource (/updateAndGetAvailableResources, size: 1)', () => {});
      then('Mavenir transitions 1 ++MSISDN++ resource from available to locked', () => {}).and('Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier', () => {});
    });
    scenario('List MSISDN resources', ({ given, when, then }) => {
      given('++MSISDN++ resources with available status are in the Mavenir inventory', () => {});
      when('Mavenir is asked to list ++MSISDN++ resources (/updateAndGetAvailableResources, size: 5)', () => {});
      then('Mavenir transitions 5 ++MSISDN++ resources from available to locked', () => {}).and('Mavenir returns the list of locked ++available number++ values to Midtier', () => {});
    });
  });
});

/**
 * Story: Search Msisdn Inventory
 */

story('Search Msisdn Inventory', () => {
  background('each', ({ given }) => {
    scenario('Search MSISDN inventory', ({ given, when, then }) => {
      given('a ++PML customer++ is authenticated in Midtier', () => {});
      when('Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (52637)', () => {});
      then('Midtier queries Mavenir for available ++MSISDN++ resources matching 52637', () => {}).and('Midtier returns matching ++available number++ values to My Paradise', () => {});
    });
  });
});

/**
 * Story: Search Msisdn Resources
 */

story('Search Msisdn Resources', () => {
  background('each', ({ given }) => {
    scenario('Search MSISDN resources by pattern', ({ given, when, then }) => {
      given('++MSISDN++ resources with available status are in the Mavenir inventory', () => {});
      when('Mavenir is asked to search ++MSISDN++ resources with pattern_search: 52637 (/updateAndGetAvailableResources)', () => {});
      then('Mavenir transitions matching ++MSISDN++ resources from available to locked', () => {}).and('Mavenir returns the matching ++available number++ values to Midtier', () => {});
    });
  });
});

/**
 * Story: Choose a Number
 * Actor: Customer
 */

story('Choose a Number', () => {
  background('each', ({ given }) => {
    scenario('Pick new number', ({ given, when, then }) => {
      given('the Prospect has selected ++available number++ ++chosen available number++', () => {}).but('no ++MSISDN++ is in the ++Mavenir shopping cart++', () => {});
      when('the Prospect clicks Continue', () => {});
      then('My Paradise reserves ++available number++ ++chosen available number++ through the Midtier', () => {}).and('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Pick new number — replace existing', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {}).and('the Prospect has selected ++available number++ ++chosen available number++', () => {});
      when('the Prospect clicks Pick new number', () => {});
      then('My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier', () => {}).and('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Keep current number', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {});
      when('the Prospect clicks Keep current number', () => {});
      then('the Prospect is forwarded to Select Sim', () => {});
    });
  });
});

/**
 * Story: Submit Reserve Number Request to Mid-Tier
 */

story('Submit Reserve Number Request to Mid-Tier', () => {
  background('each', ({ given }) => {
    scenario('Reserve number', ({ given, when, then }) => {
      given('++available number++ ++chosen available number++ is selected', () => {}).but('no ++MSISDN++ is in the ++Mavenir shopping cart++', () => {});
      when('My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++', () => {});
      then('Midtier returns 204', () => {}).and('My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier', () => {});
    });
    scenario('Reserve number — replace existing', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++', () => {}).and('++available number++ ++chosen available number++ is selected', () => {});
      when('My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++', () => {});
      then('Midtier returns 204', () => {}).and('My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier', () => {});
    });
    scenario('Reserve number request fails', ({ given, when, then }) => {
      given('++available number++ ++chosen available number++ is selected', () => {});
      when('My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++', () => {}).but('Midtier returns an error', () => {});
      then('My Paradise shows Failed to reserve your number.', () => {});
    });
  });
});

/**
 * Story: Submit Reserve Msisdn
 */

story('Submit Reserve Msisdn', () => {
  background('each', ({ given }) => {
    scenario('Reserve temporary MSISDN for porting', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++held available number++ is locked', () => {});
      when('Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (portin: true)', () => {});
      then('Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag', () => {}).and('Midtier returns 204', () => {});
    });
    scenario('Reserve MSISDN', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory', () => {});
      when('Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++', () => {});
      then('Midtier reserves ++available number++ ++chosen available number++ in Mavenir', () => {}).and('Midtier returns 204 to My Paradise', () => {});
    });
    scenario('Reserve MSISDN — release previous', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++chosen available number++ is locked', () => {}).and('++MSISDN++ ++available number++ ++held available number++ is reserved', () => {});
      when('Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++', () => {});
      then('Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir', () => {}).and('Midtier returns 204 to My Paradise', () => {});
    });
  });
});

/**
 * Story: Reserve Msisdn Resource
 */

story('Reserve Msisdn Resource', () => {
  background('each', ({ given }) => {
    scenario('Reserve MSISDN resource as temporary port-in number', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory', () => {});
      when('Mavenir is asked to reserve ++available number++ ++held available number++ with kv_tempNumber: true (/updateResources, locked → reserved, relatedParty: Paradise Mobile)', () => {});
      then('Mavenir transitions ++available number++ ++held available number++ from locked to reserved', () => {}).and('Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (kv_tempNumber)', () => {});
    });
    scenario('Reserve MSISDN resource', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory', () => {});
      when('Mavenir is asked to reserve ++available number++ ++chosen available number++ (/updateResources, locked → reserved, relatedParty: Paradise Mobile)', () => {});
      then('Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved', () => {}).and('Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++', () => {});
    });
    scenario('Reserve MSISDN resource — release previous', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++chosen available number++ is locked', () => {}).and('++MSISDN++ ++available number++ ++held available number++ is reserved', () => {});
      when('Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++', () => {});
      then('Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved', () => {}).and('Mavenir transitions ++available number++ ++held available number++ from reserved to available', () => {});
    });
  });
});

/**
 * Story: Submit Patch Cart With Number Request to Mid-Tier
 */

story('Submit Patch Cart With Number Request to Mid-Tier', () => {
  background('each', ({ given }) => {
    scenario('Patch cart with number', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++chosen available number++ has been reserved', () => {});
      when('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {});
      then('Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Patch cart with number fails', ({ given, when, then }) => {
      given('++MSISDN++ ++available number++ ++chosen available number++ has been reserved', () => {});
      when('My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier', () => {}).but('Midtier returns an error', () => {});
      then('My Paradise shows Failed to update your cart.', () => {});
    });
  });
});

/**
 * Story: Patch Cart With Number
 */

story('Patch Cart With Number', () => {
  background('each', ({ given }) => {
    scenario('Patch cart with MSISDN', ({ given, when, then }) => {
      given('a ++PML customer++ with a ++Mavenir shopping cart++', () => {}).and('++MSISDN++ ++available number++ ++chosen available number++ has been reserved', () => {});
      when('Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++', () => {});
      then('Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic', () => {}).and('Midtier returns the updated ++PML customer++ to My Paradise', () => {});
    });
  });
});

/**
 * Story: Patch Shopping Cart
 */

story('Patch Shopping Cart', () => {
  background('each', ({ given }) => {
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
});

/**
 * Story: Bring a Number
 */

story('Bring a Number', () => {
  background('each', ({ given }) => {
    scenario('Bring a number', ({ given, when, then }) => {
      then('no Transfer Code is on Bring your mobile number', () => {});
      when('the Prospect clicks Get started on Bring your mobile number', () => {});
      then('the Prospect can enter ++portability++', () => {}).and('the Prospect can confirm the information is accurate', () => {}).and('the Prospect can grant permission to Paradise Mobile to bring the number', () => {}).and('the Continue operation is disabled', () => {}).and('the Prospect can go Back', () => {});
      when('the Prospect enters ++portability++ ++valid portability++ and checks both permissions', () => {});
      then('the Continue operation is enabled', () => {});
      when('the Prospect clicks Continue', () => {});
      then('My Paradise submits ++portability++ ++valid portability++ to the Midtier', () => {}).and('Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Number to be ported is incomplete', ({ given, when, then }) => {
      when('the Prospect leaves Number to be ported as the Bermuda prefix only', () => {});
      then('Number to be ported shows Please enter the full Bermuda number.', () => {}).and('the Continue operation stays disabled', () => {});
    });
    scenario('Provider not selected', ({ given, when, then }) => {
      when('the Prospect blurs Your current provider without selecting a provider', () => {});
      then('Your current provider shows Please select a provider.', () => {}).and('the Continue operation stays disabled', () => {});
    });
  });
});

/**
 * Story: Confirm Number Already With Paradise
 */

story('Confirm Number Already With Paradise', () => {
  background('each', ({ given }) => {
    scenario('Confirm the number is not already with Paradise', ({ given, when, then }) => {
      when('the Prospect proceeds to confirming whether their number is already with Paradise', () => {});
      then('the Prospect can confirm whether the ++MSISDN++ is already with Paradise', () => {});
      when('the Prospect confirms the ++MSISDN++ is not already with Paradise', () => {});
      then('My Paradise submits ++portability++ ++valid portability++ to the Midtier', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Confirm the number is already with Paradise', ({ given, when, then }) => {
      when('the Prospect proceeds to confirming whether their number is already with Paradise', () => {});
      then('the Prospect can confirm whether the ++MSISDN++ is already with Paradise', () => {});
      when('the Prospect confirms the ++MSISDN++ is already with Paradise', () => {});
      then('++portability++ is not submitted to the Midtier', () => {}).and('the Prospect is returned to selecting their number', () => {});
    });
  });
});

/**
 * Story: Evaluate Porting Two Factor Flag
 */

story('Evaluate Porting Two Factor Flag', () => {
  background('each', ({ given }) => {
    scenario('Porting two factor flag enabled (Intended)', ({ given, when, then }) => {
      given('porting-2fa is enabled in GrowthBook', () => {}).and('the Prospect is in Account Setup', () => {});
      when('GrowthBook evaluates the porting-2fa flag', () => {});
      then('My Paradise mounts the SMS verification step in the porting wizard', () => {}).and('My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified', () => {});
    });
    scenario('Porting two factor flag disabled (live)', ({ given, when, then }) => {
      given('porting-2fa is disabled in GrowthBook', () => {}).and('the Prospect is in Account Setup', () => {});
      when('GrowthBook evaluates the porting-2fa flag', () => {});
      then('My Paradise omits the SMS verification step from the porting wizard', () => {});
    });
  });
});

/**
 * Story: Submit Portability Request to Mid-Tier
 */

story('Submit Portability Request to Mid-Tier', () => {
  background('each', ({ given }) => {
    scenario('Submit portability request — porting-2fa off (live)', ({ given, when, then }) => {
      given('the Prospect has entered ++portability++ ++valid portability++', () => {});
      when('My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++', () => {});
      then('Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++', () => {}).and('My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Submit portability request — porting-2fa on, SMS sent (Intended)', ({ given, when, then }) => {
      given('the Prospect has entered ++portability++ ++valid portability++', () => {}).and('porting-2fa is enabled', () => {});
      when('My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++', () => {});
      then('Midtier returns { status: sent, temporaryNumber: ++available number++ ++held available number++ }', () => {}).and('My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++', () => {}).and('My Paradise presents the Confirm your number for porting step', () => {});
    });
    scenario('Submit portability request — rate limited, bypass (Intended)', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {});
      when('My Paradise posts a ++portability request++', () => {}).but('Midtier returns { status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }', () => {});
      then('My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with verified: true in the ++Mavenir shopping cart++', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Submit portability request — invalid number (Intended)', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {});
      when('My Paradise posts a ++portability request++', () => {}).but('Midtier returns { status: invalid_number }', () => {});
      then('My Paradise shows This number is invalid. on Number to be ported', () => {});
    });
    scenario('Submit portability request fails', ({ given, when, then }) => {
      when('My Paradise posts a ++portability request++', () => {}).but('Midtier returns an error', () => {});
      then('My Paradise shows Failed to save your portability.', () => {});
    });
  });
});

/**
 * Story: Patch Cart With Portability
 */

story('Patch Cart With Portability', () => {
  background('each', ({ given }) => {
    scenario('Patch cart with portability', ({ given, when, then }) => {
      given('a ++PML customer++ with a ++Mavenir shopping cart++', () => {}).and('++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number', () => {}).and('++portability++ ++valid portability++ is in the request', () => {});
      when('Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++', () => {});
      then('Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)', () => {}).and('Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++', () => {});
    });
  });
});

/**
 * Story: Send Port Verification
 */

story('Send Port Verification', () => {
  background('each', ({ given }) => {
    scenario('Send port verification SMS', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {}).and('++portability++ ++valid portability++ is in the ++Mavenir shopping cart++', () => {});
      when('Midtier sends port verification to ++portability++ ++valid portability++ portNumber', () => {});
      then('Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber', () => {}).and('Midtier returns { status: sent, temporaryNumber: ++available number++ ++held available number++ } to My Paradise', () => {});
    });
    scenario('Send port verification — rate limited', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {});
      when('Midtier sends port verification', () => {}).but('Twilio rate limits the request', () => {});
      then('Midtier returns { status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ } to My Paradise', () => {});
    });
    scenario('Send port verification — invalid number', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {});
      when('Midtier sends port verification', () => {}).but('Twilio rejects the number as invalid', () => {});
      then('Midtier returns { status: invalid_number } to My Paradise', () => {});
    });
  });
});

/**
 * Story: Send Verification Sms
 */

story('Send Verification Sms', () => {
  background('each', ({ given }) => {
    scenario('Send verification SMS', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {}).and('++portability++ ++valid portability++ portNumber is a valid Bermuda number', () => {});
      when('Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber', () => {});
      then('Twilio creates a verification for ++portability++ ++valid portability++ portNumber (channel: sms)', () => {}).and('Twilio returns sent to Midtier', () => {});
    });
    scenario('Send verification SMS — rate limited', ({ given, when, then }) => {
      given('porting-2fa is enabled', () => {});
      when('Twilio is asked to send a verification SMS', () => {}).but('the rate limit for ++portability++ ++valid portability++ portNumber is exceeded', () => {});
      then('Twilio returns rate_limited to Midtier', () => {});
    });
  });
});

/**
 * Story: Enter Porting Sms Code
 */

story('Enter Porting Sms Code', () => {
  background('each', ({ given }) => {
    scenario('Enter ++porting SMS code++', ({ given, when, then }) => {
      when('the Prospect proceeds to confirming their number for porting', () => {});
      then('the Prospect sees the code was sent to the ++portability++ number', () => {}).and('the Prospect can enter ++porting SMS code++ in Enter SMS code', () => {}).and('the Prospect can Resend', () => {}).and('Resend is disabled for 30 seconds', () => {}).and('the Prospect can Change', () => {}).and('the Prospect can go Back', () => {}).and('the Verify code operation is disabled', () => {});
      when('the Prospect enters ++porting SMS code++ ++valid porting SMS code++', () => {});
      then('the Verify code operation is enabled', () => {});
      when('the Prospect clicks Verify code', () => {});
      then('My Paradise checks the ++porting SMS code++ through the Midtier', () => {}).and('the Prospect is forwarded to Select Sim', () => {});
    });
    scenario('Verify with unusable ++porting SMS code++', ({ given, when, then }) => {
      when('the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++', () => {});
      then('Enter SMS code shows helper text Invalid verification code.', () => {});
    });
    scenario('Resend ++porting SMS code++', ({ given, when, then }) => {
      when('the Prospect clicks Resend', () => {});
      then('My Paradise SMSes a ++porting SMS code++ through the Midtier', () => {}).and('the Prospect sees A new code was sent to the ++portability++ number', () => {}).and('Resend is disabled for 30 seconds before it can be used again', () => {});
    });
  });
});

/**
 * Story: Check Port Verification
 */

story('Check Port Verification', () => {
  background('each', ({ given }) => {
    scenario('Check port verification — code valid', ({ given, when, then }) => {
      when('Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {});
      then('Midtier checks the ++porting SMS code++ with Twilio', () => {}).and('Twilio returns approved', () => {}).and('Midtier marks the ++PML customer++ phone as verified', () => {}).and('Midtier returns { verified: true } to My Paradise', () => {});
    });
    scenario('Check port verification — code mismatch', ({ given, when, then }) => {
      when('Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {});
      then('Midtier checks the ++porting SMS code++ with Twilio', () => {}).and('Twilio returns a non-approved status', () => {}).and('Midtier returns { verified: false } to My Paradise', () => {});
    });
  });
});

/**
 * Story: Check Verification
 */

story('Check Verification', () => {
  background('each', ({ given }) => {
    scenario('Check verification — code valid', ({ given, when, then }) => {
      when('Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {});
      then('Twilio creates a verification check (verificationChecks.create)', () => {}).and('Twilio returns approved to Midtier', () => {});
    });
    scenario('Check verification — code mismatch', ({ given, when, then }) => {
      when('Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber', () => {});
      then('Twilio creates a verification check', () => {}).and('Twilio returns a non-approved status to Midtier', () => {});
    });
  });
});

/**
 * Story: Sweep Stale Number Reservations
 * Actor: Care
 */

story('Sweep Stale Number Reservations', () => {
  background('each', ({ given }) => {
    scenario('Sweep stale number reservations', ({ given, when, then }) => {
      given('++MSISDN++ resources have been reserved but have no active order', () => {}).and('Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory', () => {});
      when('Care sweeps stale ++MSISDN++ reservations', () => {});
      then('Mavenir transitions the stale ++MSISDN++ resources from reserved to available', () => {}).and('the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory', () => {});
    });
  });
});
