import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { Billing, BillingException } from '../../../domain/billing/Billing';
import { Cart, CartException, OnboardingStep, OrderResult } from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { zendeskGateway } from '../../../domain/systems/zendesk';
import { reloadCart } from '../get-number/examples/cart.examples';
import {
  customerReadyToPlaceOrder,
  expectedBillingAccountRequest,
  expectedProductOrderRequest,
  expectedTicketRequest,
  orderResultOutlines,
  requesterName,
  ticketOutlines,
} from './examples/place-order.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  portalGateway.reset();
  zendeskGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Create Billing Account', () => {
  let createBillingSpy: MockInstance<typeof portalGateway.createBilling>;

  beforeEach(() => {
    createBillingSpy = vi.spyOn(portalGateway, 'createBilling');
  });

  scenario('Create billing account', ({ given, when, then }) => {
    let cart: Cart;
    let billing: Billing;

    given('the Customer has a configured cart and no billing account', async () => {
      cart = await customerReadyToPlaceOrder({ billing: false });
    });
    when('the Customer creates a billing account', () => {
      billing = cart.customer.createBilling();
    });
    then('My Paradise sends the billing account request to Mavenir', () => {
      expect(createBillingSpy).toHaveBeenCalledWith(
        expect.objectContaining(expectedBillingAccountRequest(cart.customer.id)),
      );
    });
    when('Mavenir creates the billing account', async () => {
      cart = await reloadCart(cart);
    });
    then('the Customer has a billing account', () => {
      expect(billing).toBeInstanceOf(Billing);
      expect(cart.customer.billing?.id).toBe(billing.id);
    }).and('the Customer is on the Done step', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.Done);
    });
  });

  scenario('Billing account already exists', ({ given, when, then }) => {
    let cart: Cart;
    let result: BillingException | undefined;

    given('the Customer already has a billing account', async () => {
      cart = await customerReadyToPlaceOrder();
    });
    when('the Customer creates a billing account', () => {
      try { cart.customer.createBilling(); } catch (e) { result = e as BillingException; }
    });
    then('the billing account is rejected', () => {
      expect(result).toBeInstanceOf(BillingException);
      expect(result?.cause.message).toBe('409');
    }).and('Mavenir does not receive a billing account request', () => {
      expect(createBillingSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Billing account creation fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: BillingException | undefined;

    given('Mavenir returns an error for the billing account request', async () => {
      cart = await customerReadyToPlaceOrder({ billing: false });
      portalGateway.seedCreateBillingError(new Error('Mavenir unavailable'));
    });
    when('the Customer creates a billing account', () => {
      try { cart.customer.createBilling(); } catch (e) { result = e as BillingException; }
    });
    then('the billing account cannot be created', () => {
      expect(result).toBeInstanceOf(BillingException);
      expect(result?.message).toBe('Could not create billing account.');
    });
    when('My Paradise reloads the customer', async () => {
      cart = await reloadCart(cart);
    });
    then('the Customer has no billing account', () => {
      expect(cart.customer.billing).toBeNull();
    });
  });
});

// ---------------------------------------------------------------------------

story('Create Product Order', () => {
  // Pay-up-front is internal: GrowthBook pay-up-front + remaining amount at cook.
  // Midtier createOrder calls payUpFront() / postPayNow('onboarding', totalAmount) after a payment
  // method exists. Charge failure: Zendesk payUpFrontFailed, { payUpFront: false }, no product order.
  // $0 remaining (voucher) skips postPayNow; the customer cannot opt out.
  let createOrderSpy: MockInstance<typeof portalGateway.createOrder>;
  let patchDoneSpy: MockInstance<typeof portalGateway.patchDone>;

  beforeEach(() => {
    createOrderSpy = vi.spyOn(portalGateway, 'createOrder');
    patchDoneSpy = vi.spyOn(portalGateway, 'patchDone');
  });

  scenario('Create product order', ({ given, when, then }) => {
    let cart: Cart;
    let result: Cart;

    given('the Customer is verified and has a billing account, plan, number, and eSIM', async () => {
      cart = await customerReadyToPlaceOrder({ verified: true });
    });
    when('the Customer places the product order', () => {
      result = cart.createOrder();
    });
    then('My Paradise sends the product order request to Mavenir', () => {
      expect(createOrderSpy).toHaveBeenCalledWith(
        expect.objectContaining(expectedProductOrderRequest(cart.customer.id)),
      );
    });
    when('Mavenir creates the product order', async () => {
      cart = await reloadCart(cart);
    });
    then('the order succeeded with pay-up-front', () => {
      expect(result).toBeInstanceOf(Cart);
      expect(cart.orderSuccess).toBe(true);
      expect(cart.payUpFront).toBe(true);
      expect(cart.defaultPayment).toBe(true);
      expect(cart.customer.verified).toBe(true);
    }).and('the Customer onboarding is done', () => {
      expect(patchDoneSpy).toHaveBeenCalledWith(
        expect.objectContaining({ customerId: cart.customer.id }),
      );
      expect(cart.customer.done).toBe(true);
    });
  });

  scenario('Pay-up-front charge fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: Cart;

    given('the pay-up-front charge fails', async () => {
      cart = await customerReadyToPlaceOrder({ verified: true });
      portalGateway.seedPayUpFrontFailed();
    });
    when('the Customer places the product order', () => {
      result = cart.createOrder();
    });
    then('My Paradise does not send a product order to Mavenir', () => {
      expect(createOrderSpy).not.toHaveBeenCalled();
    });
    when('My Paradise reloads the cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the order succeeded without pay-up-front', () => {
      expect(result).toBeInstanceOf(Cart);
      expect(cart.orderSuccess).toBe(true);
      expect(cart.payUpFront).toBe(false);
      expect(cart.defaultPayment).toBe(true);
      expect(cart.customer.done).toBe(false);
    });
  });

  scenario('Product order fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: Cart;

    given('Mavenir returns an error for the product order', async () => {
      cart = await customerReadyToPlaceOrder({ verified: true });
      portalGateway.seedCreateOrderError(new Error('Mavenir unavailable'));
    });
    when('the Customer places the product order', () => {
      result = cart.createOrder();
    });
    then('My Paradise sends the product order request to Mavenir', () => {
      expect(createOrderSpy).toHaveBeenCalled();
    });
    when('My Paradise reloads the cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the order did not succeed', () => {
      expect(cart.orderSuccess).toBe(false);
      expect(cart.payUpFront).toBeNull();
      expect(cart.defaultPayment).toBe(true);
    });
  });

  scenario('Onboarding is already done', ({ given, when, then }) => {
    let cart: Cart;
    let result: CartException | undefined;

    given('the Customer onboarding is already done', async () => {
      cart = await customerReadyToPlaceOrder({ done: true });
    });
    when('the Customer places the product order', () => {
      try { cart.createOrder(); } catch (e) { result = e as CartException; }
    });
    then('the product order is rejected', () => {
      expect(result).toBeInstanceOf(CartException);
      expect(result?.cause.message).toBe('409');
    }).and('Mavenir does not receive a product order request', () => {
      expect(createOrderSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Unverified with no bypass and no portability', ({ given, when, then }) => {
    let cart: Cart;
    let result: Cart;

    given('the Customer is not verified and the plan does not bypass verification', async () => {
      cart = await customerReadyToPlaceOrder({ verified: false });
    });
    when('the Customer places the product order', () => {
      result = cart.createOrder();
    });
    then('My Paradise does not send a product order to Mavenir', () => {
      expect(createOrderSpy).not.toHaveBeenCalled();
    }).and('the cart is marked to submit the order later', () => {
      expect(result.submitOrder).toBe(true);
    });
    when('My Paradise reloads the cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the Customer onboarding is done', () => {
      expect(patchDoneSpy).toHaveBeenCalledWith(
        expect.objectContaining({ customerId: cart.customer.id }),
      );
      expect(cart.customer.done).toBe(true);
      expect(cart.orderSuccess).toBe(true);
      expect(cart.customer.verified).toBe(false);
    });
  });
});

// ---------------------------------------------------------------------------

story('View Order Result', () => {
  orderResultOutlines.forEach(({ example, seed, orderSuccess, payUpFront, result: expected }) => {
    scenario(`View order result: ${example}`, ({ given, when, then }) => {
      let cart: Cart;
      let result: OrderResult;

      given(`the order result is ${example}`, async () => {
        cart = await customerReadyToPlaceOrder({ ...seed, orderSuccess, payUpFront });
        cart = await reloadCart(cart);
      });
      when('the Customer views their order result', () => {
        result = cart.orderResult;
      });
      then(expected === OrderResult.AllSet ? 'the order is complete' : 'the order is not yet complete', () => {
        expect(result).toBe(expected);
      });
    });
  });
});

// ---------------------------------------------------------------------------

story('Create Order Ticket', () => {
  let createTicketSpy: MockInstance<typeof zendeskGateway.create>;

  beforeEach(() => {
    createTicketSpy = vi.spyOn(zendeskGateway, 'create');
  });

  ticketOutlines.forEach(({ example, seed, subject }) => {
    scenario(`Create order ticket: ${example}`, ({ given, when, then }) => {
      let cart: Cart;
      let tickets: ReturnType<Cart['createOrderTicket']>;

      given(`the Customer ${example}`, async () => {
        cart = await customerReadyToPlaceOrder(seed);
      });
      when('the Customer creates the order ticket', () => {
        tickets = cart.createOrderTicket();
      });
      then(`My Paradise sends the ${subject} ticket to Zendesk`, () => {
        expect(createTicketSpy).toHaveBeenCalledWith(
          expect.objectContaining(expectedTicketRequest(cart.customer, subject)),
        );
      });
      when('Zendesk creates the ticket', () => {});
      then('the ticket is created for the Customer', () => {
        expect(tickets.some(ticket => ticket.subject === subject)).toBe(true);
        expect(tickets[0].requesterName).toBe(requesterName);
        expect(tickets[0].requesterEmail).toBe(cart.customer.identity.email);
      });
    });
  });
});
