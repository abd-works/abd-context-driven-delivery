from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import storedAccountCredentialsWithToken, newMavenirShoppingCart


# Epic: Create Empty Cart
# Orders: 0.0.0.0

# Story: Ensure Cart on Customer
with story("Ensure Cart on Customer"):
    # typescript body to translate:
    # const cartRepository = new CartRepository(shoppingCartGateway);
    #
    # let createSpy: MockInstance<typeof shoppingCartGateway.create>;
    #
    # beforeEach(() => {
    #   createSpy = vi.spyOn(shoppingCartGateway, 'create');
    # });
        with scenario("Load Cart — no cart"):
            # typescript body to translate:
            # let customer: Customer;
            # examples: storedAccountCredentialsWithToken
            with given("the Customer enters the onboarding journey with a valid account token and no cart"):
                # typescript body to translate:
                # customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
                pass
            with when("My Paradise loads the cart for the customer"):
                # typescript body to translate:
                # customer.cart = cartRepository.load(customer);
                pass
            with then("My Paradise finds no cart on the customer"):
                # typescript body to translate:
                # expect(customer.cart).toBeNull();
                pass
        with scenario("Create Cart"):
            # typescript body to translate:
            # let customer: Customer;
            # let result: Cart;
            # examples: storedAccountCredentialsWithToken
            with given("the Customer enters the onboarding journey with a valid account token and no cart"):
                # typescript body to translate:
                # customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
                pass
            with when("My Paradise creates a cart for the customer"):
                # typescript body to translate:
                # result = cartRepository.create(customer);
                pass
            with then("My Paradise sends the create request to Midtier with the customer id"):
                # typescript body to translate:
                # expect(createSpy).toHaveBeenCalledWith('cus_1');
                pass
            with when("Mavenir creates the shopping cart"):
                # typescript body to translate:
                # customer.cart = cartRepository.load(customer);
                pass
            with then("My Paradise stores the cart on the customer"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Cart);
                # expect(customer.cart?.id).toBe(result.id);
                pass
            with and_("the Customer proceeds to Get Number"):
                # typescript body to translate:
                # expect(customer.cart?.onboardingStep).toBe('SelectPlan');
                pass
        with scenario("customer already has a Mavenir shopping cart"):
            # typescript body to translate:
            # let customer: Customer;
            # examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
            with given("the Customer enters the onboarding journey with a valid account token"):
                # typescript body to translate:
                # customer = new Customer(storedAccountCredentialsWithToken());
                pass
            with and_("the customer has a Mavenir shopping cart"):
                # typescript body to translate:
                # shoppingCartGateway.seedCart(customer.id, newMavenirShoppingCart.id);
                pass
            with when("My Paradise loads the cart for the customer"):
                # typescript body to translate:
                # customer.cart = cartRepository.load(customer);
                pass
            with then("My Paradise finds the cart on the customer"):
                # typescript body to translate:
                # expect(customer.cart).not.toBeNull();
                pass
            with and_("the Customer proceeds to Get Number"):
                # typescript body to translate:
                # expect(customer.cart?.id).toBe(newMavenirShoppingCart.id);
                pass
        with scenario("cart already exists"):
            # typescript body to translate:
            # let customer: Customer;
            # let error: CartException;
            # examples: storedAccountCredentialsWithToken, newMavenirShoppingCart
            with given("the Customer enters the onboarding journey and already has a cart loaded"):
                # typescript body to translate:
                # customer = new Customer(storedAccountCredentialsWithToken('cus_1'));
                # shoppingCartGateway.seedCart('cus_1', newMavenirShoppingCart.id);
                # customer.cart = cartRepository.load(customer);
                pass
            with when("My Paradise creates a cart for the customer"):
                # typescript body to translate:
                # try { cartRepository.create(customer); } catch (e) { error = e as CartException; }
                pass
            with then("My Paradise reports a cart creation error"):
                # typescript body to translate:
                # expect(error).toBeInstanceOf(CartException);
                # expect(error.operation).toBe('create');
                pass
