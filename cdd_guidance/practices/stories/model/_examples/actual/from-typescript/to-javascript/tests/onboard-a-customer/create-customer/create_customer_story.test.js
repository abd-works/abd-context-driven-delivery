/**
 * Epic: Create Customer
 * Orders: 0.0.0
 */

import { background, scenario, story } from "../../story-test.js";
import { enteredValidAccountCredentials } from "./examples";


/**
 * Story: Create Customer
 */

story('Create Customer', () => {
  background('each', ({ given }) => {
    given('the User has a verified account with an account token', () => {});
  });
    scenario('Create customer', ({ given, when, then }) => {
      // examples: enteredValidAccountCredentials
      when('the User creates their Paradise account', () => {});
      then('My Paradise sends the correct create request to Mavenir', () => {});
      when('Mavenir creates the customer', () => {});
      then('the customer has a Mavenir customer id', () => {}).and('My Paradise stores the customer id on the Cognito user', () => {});
    });
    scenario('Mavenir customer already exists', ({ given, when, then }) => {
      // examples: enteredValidAccountCredentials
      given('Mavenir already has a customer for that email', () => {});
      when('the User creates their Paradise account', () => {});
      then('My Paradise shows Could not create customer', () => {});
    });
});
