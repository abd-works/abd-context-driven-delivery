import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { Customer } from '../../../domain/customer/Customer';
import {
  Cart,
  CartException,
  CartRepository,
} from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { storedAccountCredentialsWithToken } from '../examples/account-credentials.examples';
import { newMavenirShoppingCart } from './examples/mavenir-shopping-cart.examples';


afterEach(() => {
  shoppingCartGateway.reset();
  vi.restoreAllMocks();
});

// Token validation (valid token → customer id, invalid token → Error) is covered by
// create-unconfirmed-user/create_unconfirmed_user_story.spec.ts.
// Any protected Midtier operation uses the same MidtierCartService.validate() path.
// Do not repeat it here — see validate-story-is-shared-not-duplicated in stories/AGENTS.md.

story('Ensure Cart on Customer', () => {
  const cartRepository = new CartRepository(shoppingCartGateway);

  let createSpy: MockInstance<typeof shoppingCartGateway.create>;

  beforeEach(() => {
    createSpy = vi.spyOn(shoppingCartGateway, 'create');
  });

  scenario('Load Cart — no cart', ({ given, when, then }) => {
    let customer: Customer;

    given('the Customer enters the onboarding journey with a valid account token and no cart', () => {
      customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
    });
    when('My Paradise loads the cart for the customer', () => {
      customer.cart = cartRepository.load(customer);
    });
    then('My Paradise finds no cart on the customer', () => {
      expect(customer.cart).toBeNull();
    });
  });

  scenario('Create Cart', ({ given, when, then }) => {
    let customer: Customer;
    let result: Cart;

    given('the Customer enters the onboarding journey with a valid account token and no cart', () => {
      customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
    });
    when('My Paradise creates a cart for the customer', () => {
      result = cartRepository.create(customer);
    });
    then('My Paradise sends the create request to Midtier with the customer id', () => {
      expect(createSpy).toHaveBeenCalledWith('cus_1');
    });
    when('Mavenir creates the shopping cart', () => {
      customer.cart = cartRepository.load(customer);
    });
    then('My Paradise stores the cart on the customer', () => {
      expect(result).toBeInstanceOf(Cart);
      expect(customer.cart?.id).toBe(result.id);
    }).and('the Customer proceeds to Get Number', () => {
      expect(customer.cart?.onboardingStep).toBe('SelectPlan');
    });
  });

  scenario('customer already has a Mavenir shopping cart', ({ given, when, then }) => {
    let customer: Customer;

    given('the Customer enters the onboarding journey with a valid account token', () => {
      customer = new Customer(storedAccountCredentialsWithToken());
    }).and('the customer has a Mavenir shopping cart', () => {
      shoppingCartGateway.seedCart(customer.id, newMavenirShoppingCart.id);
    });
    when('My Paradise loads the cart for the customer', () => {
      customer.cart = cartRepository.load(customer);
    });
    then('My Paradise finds the cart on the customer', () => {
      expect(customer.cart).not.toBeNull();
    }).and('the Customer proceeds to Get Number', () => {
      expect(customer.cart?.id).toBe(newMavenirShoppingCart.id);
    });
  });

  scenario('cart already exists', ({ given, when, then }) => {
    let customer: Customer;
    let error: CartException;

    given('the Customer enters the onboarding journey and already has a cart loaded', () => {
      customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
      shoppingCartGateway.seedCart('cus_1', newMavenirShoppingCart.id);
      customer.cart = cartRepository.load(customer);
    });
    when('My Paradise creates a cart for the customer', () => {
      try { cartRepository.create(customer); } catch (e) { error = e as CartException; }
    });
    then('My Paradise reports a cart creation error', () => {
      expect(error).toBeInstanceOf(CartException);
      expect(error.operation).toBe('create');
    });
  });
});
