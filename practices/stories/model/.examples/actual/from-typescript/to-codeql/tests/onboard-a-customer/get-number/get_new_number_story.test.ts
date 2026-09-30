/**
 * Epic: Get New Number
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Determine Number
 */

story('Determine Number', () => {
  scenario('View available numbers', ({ given, when, then }) => {
    given('a My Paradise customer with a Mavenir shopping cart and no MSISDN', () => {
      // TODO: implement step
    });
    when('the Customer loads available numbers', () => {
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {
      // TODO: implement step
    });
    then('My Paradise returns the available numbers', () => {
      // TODO: implement step
    });
  });

  scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
    when('the Customer loads available numbers', () => {
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {
      // TODO: implement step
    })
      .and('My Paradise returns the available numbers', () => {
        // TODO: implement step
      });
  });

  scenario('Refresh available numbers', ({ given, when, then }) => {
    given('a My Paradise customer with a Mavenir shopping cart', () => {
      // TODO: implement step
    });
    when('the Customer refreshes the number list', () => {
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir locks 20 MSISDN resources and returns the available numbers', () => {
      // TODO: implement step
    });
    then('My Paradise returns a fresh set of available numbers', () => {
      // TODO: implement step
    });
  });

  scenario('Search for a number', ({ given, when, then }) => {
    given('a My Paradise customer with a Mavenir shopping cart', () => {
      // TODO: implement step
    });
    when('the Customer searches for numbers matching JAMES (52637)', () => {
      // TODO: implement step
    });
    then('My Paradise sends the search request to Mavenir with pattern 52637', () => {
      // TODO: implement step
    });
    when('Mavenir locks MSISDN resources matching 52637 and returns matching values', () => {
      // TODO: implement step
    });
    then('My Paradise returns Available Numbers matching 52637', () => {
      // TODO: implement step
    })
      .and('the matching numbers are stored on the line for selection', () => {
        // TODO: implement step
      });
  });

  scenario('Numbers locked by another customer are excluded from results', ({ given, when, then }) => {
    given('another customer has already locked the standard available numbers in Mavenir', () => {
      // TODO: implement step
    });
    when('the Customer loads available numbers', () => {
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir returns only available numbers, excluding the locked ones', () => {
      // TODO: implement step
    });
    then('the locked numbers are not in the available numbers list', () => {
      // TODO: implement step
    })
      .and('only the currently available numbers are returned', () => {
        // TODO: implement step
      });
  });

  scenario('Pick number', ({ given, when, then }) => {
    when('Mavenir confirms the reservation and patches the cart', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Select Sim', () => {
        // TODO: implement step
      });
  });

  scenario('Pick number — replace existing', ({ given, when, then }) => {
  });

  scenario('Reserve number request fails', ({ given, when, then }) => {
    then('My Paradise shows Failed to reserve your number.', () => {
      // TODO: implement step
    });
  });

  scenario('Patch cart with number fails', ({ given, when, then }) => {
    then('My Paradise shows Failed to update your cart.', () => {
      // TODO: implement step
    });
  });

});
