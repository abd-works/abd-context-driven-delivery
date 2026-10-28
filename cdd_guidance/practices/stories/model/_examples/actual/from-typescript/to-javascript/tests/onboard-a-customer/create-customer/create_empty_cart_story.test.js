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
  // typescript body to translate:
  // const cartRepository = new CartRepository(shoppingCartGateway);
  //
  // let createSpy: MockInstance<typeof shoppingCartGateway.create>;
  //
  // beforeEach(() => {
  //   createSpy = vi.spyOn(shoppingCartGateway, 'create');
  // });
  scenario('Load Cart — no cart', ({ given, when, then }) => {
    // typescript body to translate:
    // let customer: Customer;
    // examples: storedAccountCredentialsWithToken
    given('the Customer enters the onboarding journey with a valid account token and no cart', () => {
      // typescript body to translate:
      // customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
      // TODO: implement step
    });
    when('My Paradise loads the cart for the customer', () => {
      // typescript body to translate:
      // customer.cart = cartRepository.load(customer);
      // TODO: implement step
    });
    then('My Paradise finds no cart on the customer', () => {
      // typescript body to translate:
      // expect(customer.cart).toBeNull();
      // TODO: implement step
    });
  });

  scenario('Create Cart', ({ given, when, then }) => {
    // typescript body to translate:
    // let customer: Customer;
    // let result: Cart;
    // examples: storedAccountCredentialsWithToken
    given('the Customer enters the onboarding journey with a valid account token and no cart', () => {
      // typescript body to translate:
      // customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
      // TODO: implement step
    });
    when('My Paradise creates a cart for the customer', () => {
      // typescript body to translate:
      // result = cartRepository.create(customer);
      // TODO: implement step
    });
    then('My Paradise sends the create request to Midtier with the customer id', () => {
      // typescript body to translate:
      // expect(createSpy).toHaveBeenCalledWith('cus_1');
      // TODO: implement step
    });
    when('Mavenir creates the shopping cart', () => {
      // typescript body to translate:
      // customer.cart = cartRepository.load(customer);
      // TODO: implement step
    });
    then('My Paradise stores the cart on the customer', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Cart);
      // expect(customer.cart?.id).toBe(result.id);
      // TODO: implement step
    })
      .and('the Customer proceeds to Get Number', () => {
        // typescript body to translate:
        // expect(customer.cart?.onboardingStep).toBe('SelectPlan');
        // TODO: implement step
      });
  });

  scenario('customer already has a Mavenir shopping cart', ({ given, when, then }) => {
    // typescript body to translate:
    // let customer: Customer;
    // examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
    given('the Customer enters the onboarding journey with a valid account token', () => {
      // typescript body to translate:
      // customer = new Customer(storedAccountCredentialsWithToken());
      // TODO: implement step
    })
      .and('the customer has a Mavenir shopping cart', () => {
        // typescript body to translate:
        // shoppingCartGateway.seedCart(customer.id, newMavenirShoppingCart.id);
        // TODO: implement step
      });
    when('My Paradise loads the cart for the customer', () => {
      // typescript body to translate:
      // customer.cart = cartRepository.load(customer);
      // TODO: implement step
    });
    then('My Paradise finds the cart on the customer', () => {
      // typescript body to translate:
      // expect(customer.cart).not.toBeNull();
      // TODO: implement step
    })
      .and('the Customer proceeds to Get Number', () => {
        // typescript body to translate:
        // expect(customer.cart?.id).toBe(newMavenirShoppingCart.id);
        // TODO: implement step
      });
  });

  scenario('cart already exists', ({ given, when, then }) => {
    // typescript body to translate:
    // let customer: Customer;
    // let error: CartException;
    // examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
    given('the Customer enters the onboarding journey and already has a cart loaded', () => {
      // typescript body to translate:
      // customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
      // shoppingCartGateway.seedCart('cus_1', newMavenirShoppingCart.id);
      // customer.cart = cartRepository.load(customer);
      // TODO: implement step
    });
    when('My Paradise creates a cart for the customer', () => {
      // typescript body to translate:
      // try { cartRepository.create(customer); } catch (e) { error = e as CartException; }
      // TODO: implement step
    });
    then('My Paradise reports a cart creation error', () => {
      // typescript body to translate:
      // expect(error).toBeInstanceOf(CartException);
      // expect(error.operation).toBe('create');
      // TODO: implement step
    });
  });
});
