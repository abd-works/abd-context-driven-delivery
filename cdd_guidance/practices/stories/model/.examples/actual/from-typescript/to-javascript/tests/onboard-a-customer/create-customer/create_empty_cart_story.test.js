/**
 * Epic: Create Empty Cart
 * Orders: 0.0.0.0
 */

import { background, scenario, story } from "../../story-test.js";
import { storedAccountCredentialsWithToken, newMavenirShoppingCart } from "./examples";


/**
 * Story: Ensure Cart on Customer
 */

story('Ensure Cart on Customer', () => {
    scenario('Load Cart — no cart', ({ given, when, then }) => {
      // examples: storedAccountCredentialsWithToken
      given('the Customer enters the onboarding journey with a valid account token and no cart', () => {});
      when('My Paradise loads the cart for the customer', () => {});
      then('My Paradise finds no cart on the customer', () => {});
    });
    scenario('Create Cart', ({ given, when, then }) => {
      // examples: storedAccountCredentialsWithToken
      given('the Customer enters the onboarding journey with a valid account token and no cart', () => {});
      when('My Paradise creates a cart for the customer', () => {});
      then('My Paradise sends the create request to Midtier with the customer id', () => {});
      when('Mavenir creates the shopping cart', () => {});
      then('My Paradise stores the cart on the customer', () => {}).and('the Customer proceeds to Get Number', () => {});
    });
    scenario('customer already has a Mavenir shopping cart', ({ given, when, then }) => {
      // examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
      given('the Customer enters the onboarding journey with a valid account token', () => {}).and('the customer has a Mavenir shopping cart', () => {});
      when('My Paradise loads the cart for the customer', () => {});
      then('My Paradise finds the cart on the customer', () => {}).and('the Customer proceeds to Get Number', () => {});
    });
    scenario('cart already exists', ({ given, when, then }) => {
      // examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
      given('the Customer enters the onboarding journey and already has a cart loaded', () => {});
      when('My Paradise creates a cart for the customer', () => {});
      then('My Paradise reports a cart creation error', () => {});
    });
});
