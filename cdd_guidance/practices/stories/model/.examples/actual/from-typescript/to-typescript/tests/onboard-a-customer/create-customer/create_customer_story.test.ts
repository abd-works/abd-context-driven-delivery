/**
 * Epic: Create Customer
 * Orders: 0.0.0
 */

import { scenario, story } from "tests/story-test";
import { enteredValidAccountCredentials } from "./examples";


/**
 * Story: Create Customer
 */

story('Create Customer', () => {
  background('each', ({ given }) => {
    given('the User has a verified account with an account token', () => {
      // TODO: implement step
    });
  });

  scenario('Create customer', ({ given, when, then }) => {
    // examples: enteredValidAccountCredentials
    when('the User creates their Paradise account', () => {
      // TODO: implement step
    });
    then('My Paradise sends the correct create request to Mavenir', () => {
      // TODO: implement step
    });
    when('Mavenir creates the customer', () => {
      // TODO: implement step
    });
    then('the customer has a Mavenir customer id', () => {
      // TODO: implement step
    })
      .and('My Paradise stores the customer id on the Cognito user', () => {
        // TODO: implement step
      });
  });

  scenario('Mavenir customer already exists', ({ given, when, then }) => {
    // examples: enteredValidAccountCredentials
    given('Mavenir already has a customer for that email', () => {
      // TODO: implement step
    });
    when('the User creates their Paradise account', () => {
      // TODO: implement step
    });
    then('My Paradise shows Could not create customer', () => {
      // TODO: implement step
    });
  });

});
