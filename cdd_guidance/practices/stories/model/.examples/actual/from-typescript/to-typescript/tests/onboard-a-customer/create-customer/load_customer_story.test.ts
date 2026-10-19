/**
 * Epic: Load Customer
 * Orders: 0.0.0.2
 */

import { scenario, story } from "tests/story-test";
import { enteredValidAccountCredentials, storedAccountCredentialsWithToken } from "./examples";


/**
 * Story: Load My Paradise Customer From Midtier And Store In Session
 */

story('Load My Paradise Customer From Midtier And Store In Session', () => {
  background('each', ({ given }) => {
    given('Mavenir has a customer and the Cognito user holds its id', () => {
      // TODO: implement step
    });
  });

  scenario('Load My Paradise Customer From Midtier And Store In Session', ({ given, when, then }) => {
    // examples: enteredValidAccountCredentials
    when('My Paradise loads the customer through Midtier', () => {
      // TODO: implement step
    });
    then('My Paradise calls Midtier with the correct customer id', () => {
      // TODO: implement step
    })
      .and('Midtier maps the Mavenir contact medium to Paradise identity and address', () => {
        // TODO: implement step
      });
  });

  scenario('Load customer fails', ({ given, when, then }) => {
    given('Mavenir no longer has that customer', () => {
      // TODO: implement step
    });
    when('My Paradise loads the customer', () => {
      // TODO: implement step
    });
    then('My Paradise signs the User out', () => {
      // TODO: implement step
    })
      .and('My Paradise shows Something went wrong when loading your account', () => {
        // TODO: implement step
      });
  });

  scenario('Terminated account', ({ given, when, then }) => {
    // examples: storedAccountCredentialsWithToken
    given('the Customer has an account token', () => {
      // TODO: implement step
    })
      .and('the Mavenir customer billing state is terminated', () => {
        // TODO: implement step
      });
    when('My Paradise loads the customer', () => {
      // TODO: implement step
    });
    then('My Paradise signs the Customer out', () => {
      // TODO: implement step
    })
      .and('the Customer account is terminated', () => {
        // TODO: implement step
      });
  });

});
