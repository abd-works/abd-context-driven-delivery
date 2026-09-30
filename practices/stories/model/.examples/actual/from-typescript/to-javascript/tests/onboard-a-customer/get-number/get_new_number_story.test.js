/**
 * Epic: Get New Number
 */

import { background, scenario, story } from "../../story-test.js";

/**
 * Story: Determine Number
 */

story('Determine Number', () => {
  background('each', ({ given }) => {
    scenario('View available numbers', ({ given, when, then }) => {
      given('a My Paradise customer with a Mavenir shopping cart and no MSISDN', () => {});
      when('the Customer loads available numbers', () => {});
      then('My Paradise sends the list resources request to Mavenir', () => {});
      when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {});
      then('My Paradise returns the available numbers', () => {});
    });
    scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
      when('the Customer loads available numbers', () => {});
      then('My Paradise sends the list resources request to Mavenir', () => {});
      when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {}).and('My Paradise returns the available numbers', () => {});
    });
    scenario('Refresh available numbers', ({ given, when, then }) => {
      given('a My Paradise customer with a Mavenir shopping cart', () => {});
      when('the Customer refreshes the number list', () => {});
      then('My Paradise sends the list resources request to Mavenir', () => {});
      when('Mavenir locks 20 MSISDN resources and returns the available numbers', () => {});
      then('My Paradise returns a fresh set of available numbers', () => {});
    });
    scenario('Search for a number', ({ given, when, then }) => {
      given('a My Paradise customer with a Mavenir shopping cart', () => {});
      when('the Customer searches for numbers matching JAMES (52637)', () => {});
      then('My Paradise sends the search request to Mavenir with pattern 52637', () => {});
      when('Mavenir locks MSISDN resources matching 52637 and returns matching values', () => {});
      then('My Paradise returns Available Numbers matching 52637', () => {}).and('the matching numbers are stored on the line for selection', () => {});
    });
    scenario('Numbers locked by another customer are excluded from results', ({ given, when, then }) => {
      given('another customer has already locked the standard available numbers in Mavenir', () => {});
      when('the Customer loads available numbers', () => {});
      then('My Paradise sends the list resources request to Mavenir', () => {});
      when('Mavenir returns only available numbers, excluding the locked ones', () => {});
      then('the locked numbers are not in the available numbers list', () => {}).and('only the currently available numbers are returned', () => {});
    });
    scenario('Pick number', ({ given, when, then }) => {
      when('Mavenir confirms the reservation and patches the cart', () => {}).and('the Customer is forwarded to Select Sim', () => {});
    });
    scenario('Pick number — replace existing', ({ given, when, then }) => {
    });
    scenario('Reserve number request fails', ({ given, when, then }) => {
      then('My Paradise shows Failed to reserve your number.', () => {});
    });
    scenario('Patch cart with number fails', ({ given, when, then }) => {
      then('My Paradise shows Failed to update your cart.', () => {});
    });
  });
});
