/**
 * Epic: Load Customer
 */

import { background, scenario, story } from "../../story-test.js";

/**
 * Story: Load My Paradise Customer From Midtier And Store In Session
 */

story('Load My Paradise Customer From Midtier And Store In Session', () => {
  background('each', ({ given }) => {
    given('Mavenir has a customer and the Cognito user holds its id', () => {});
    scenario('Load My Paradise Customer From Midtier And Store In Session', ({ given, when, then }) => {
      when('My Paradise loads the customer through Midtier', () => {});
      then('My Paradise calls Midtier with the correct customer id', () => {}).and('Midtier maps the Mavenir contact medium to Paradise identity and address', () => {});
    });
    scenario('Load customer fails', ({ given, when, then }) => {
      given('Mavenir no longer has that customer', () => {});
      when('My Paradise loads the customer', () => {});
      then('My Paradise signs the User out', () => {}).and('My Paradise shows Something went wrong when loading your account', () => {});
    });
    scenario('Terminated account', ({ given, when, then }) => {
      given('the Customer has an account token', () => {}).and('the Mavenir customer billing state is terminated', () => {});
      when('My Paradise loads the customer', () => {});
      then('My Paradise signs the Customer out', () => {}).and('the Customer account is terminated', () => {});
    });
  });
});
