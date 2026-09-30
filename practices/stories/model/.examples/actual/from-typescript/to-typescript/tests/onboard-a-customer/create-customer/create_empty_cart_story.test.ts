/**
 * Epic: Create Empty Cart
 * Orders: 0.0.0.0
 */

import { scenario, story } from "tests/story-test";
import { storedAccountCredentialsWithToken, newMavenirShoppingCart } from "./examples";


/**
 * Story: Ensure Cart on Customer
 */

story('Ensure Cart on Customer', () => {
  scenario('Load Cart — no cart', ({ given, when, then }) => {
    // examples: storedAccountCredentialsWithToken
    given('the Customer enters the onboarding journey with a valid account token and no cart', () => {
      // TODO: implement step
    });
    when('My Paradise loads the cart for the customer', () => {
      // TODO: implement step
    });
    then('My Paradise finds no cart on the customer', () => {
      // TODO: implement step
    });
  });

  scenario('Create Cart', ({ given, when, then }) => {
    // examples: storedAccountCredentialsWithToken
    given('the Customer enters the onboarding journey with a valid account token and no cart', () => {
      // TODO: implement step
    });
    when('My Paradise creates a cart for the customer', () => {
      // TODO: implement step
    });
    then('My Paradise sends the create request to Midtier with the customer id', () => {
      // TODO: implement step
    });
    when('Mavenir creates the shopping cart', () => {
      // TODO: implement step
    });
    then('My Paradise stores the cart on the customer', () => {
      // TODO: implement step
    })
      .and('the Customer proceeds to Get Number', () => {
        // TODO: implement step
      });
  });

  scenario('customer already has a Mavenir shopping cart', ({ given, when, then }) => {
    // examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
    given('the Customer enters the onboarding journey with a valid account token', () => {
      // TODO: implement step
    })
      .and('the customer has a Mavenir shopping cart', () => {
        // TODO: implement step
      });
    when('My Paradise loads the cart for the customer', () => {
      // TODO: implement step
    });
    then('My Paradise finds the cart on the customer', () => {
      // TODO: implement step
    })
      .and('the Customer proceeds to Get Number', () => {
        // TODO: implement step
      });
  });

  scenario('cart already exists', ({ given, when, then }) => {
    // examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
    given('the Customer enters the onboarding journey and already has a cart loaded', () => {
      // TODO: implement step
    });
    when('My Paradise creates a cart for the customer', () => {
      // TODO: implement step
    });
    then('My Paradise reports a cart creation error', () => {
      // TODO: implement step
    });
  });

});
