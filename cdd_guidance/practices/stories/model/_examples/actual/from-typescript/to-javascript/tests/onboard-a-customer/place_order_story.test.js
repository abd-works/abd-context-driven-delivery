/**
 * Epic: Place Order
 * Orders: 0.0.9
 */

import { background, scenario, story } from "../story-test.js";
import { reloadCart, customerReadyToPlaceOrder, expectedBillingAccountRequest, expectedProductOrderRequest, expectedTicketRequest, requesterName } from "./examples";

/**
 * Story: Create Billing Account
 */

story('Create Billing Account', () => {
  // typescript body to translate:
  // let createBillingSpy: MockInstance<typeof portalGateway.createBilling>;
  //
  // beforeEach(() => {
  //   createBillingSpy = vi.spyOn(portalGateway, 'createBilling');
  // });
  scenario('Create billing account', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let billing: Billing;
    // examples: reloadCart, customerReadyToPlaceOrder, expectedBillingAccountRequest
    given('the Customer has a configured cart and no billing account', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ billing: false });
      // TODO: implement step
    });
    when('the Customer creates a billing account', () => {
      // typescript body to translate:
      // billing = cart.customer.createBilling();
      // TODO: implement step
    });
    then('My Paradise sends the billing account request to Mavenir', () => {
      // typescript body to translate:
      // expect(createBillingSpy).toHaveBeenCalledWith(
      //   expect.objectContaining(expectedBillingAccountRequest(cart.customer.id)),
      // );
      // TODO: implement step
    });
    when('Mavenir creates the billing account', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the Customer has a billing account', () => {
      // typescript body to translate:
      // expect(billing).toBeInstanceOf(Billing);
      // expect(cart.customer.billing?.id).toBe(billing.id);
      // TODO: implement step
    })
      .and('the Customer is on the Done step', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.Done);
        // TODO: implement step
      });
  });

  scenario('Billing account already exists', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: BillingException | undefined;
    // examples: customerReadyToPlaceOrder
    given('the Customer already has a billing account', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder();
      // TODO: implement step
    });
    when('the Customer creates a billing account', () => {
      // typescript body to translate:
      // try { cart.customer.createBilling(); } catch (e) { result = e as BillingException; }
      // TODO: implement step
    });
    then('the billing account is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(BillingException);
      // expect(result?.cause.message).toBe('409');
      // TODO: implement step
    })
      .and('Mavenir does not receive a billing account request', () => {
        // typescript body to translate:
        // expect(createBillingSpy).not.toHaveBeenCalled();
        // TODO: implement step
      });
  });

  scenario('Billing account creation fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: BillingException | undefined;
    // examples: reloadCart, customerReadyToPlaceOrder
    given('Mavenir returns an error for the billing account request', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ billing: false });
      // portalGateway.seedCreateBillingError(new Error('Mavenir unavailable'));
      // TODO: implement step
    });
    when('the Customer creates a billing account', () => {
      // typescript body to translate:
      // try { cart.customer.createBilling(); } catch (e) { result = e as BillingException; }
      // TODO: implement step
    });
    then('the billing account cannot be created', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(BillingException);
      // expect(result?.message).toBe('Could not create billing account.');
      // TODO: implement step
    });
    when('My Paradise reloads the customer', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the Customer has no billing account', () => {
      // typescript body to translate:
      // expect(cart.customer.billing).toBeNull();
      // TODO: implement step
    });
  });
});

/**
 * Story: Create Product Order
 */

story('Create Product Order', () => {
  // typescript body to translate:
  // // Pay-up-front is internal: GrowthBook pay-up-front + remaining amount at cook.
  // // Midtier createOrder calls payUpFront() / postPayNow('onboarding', totalAmount) after a payment
  // // method exists. Charge failure: Zendesk payUpFrontFailed, { payUpFront: false }, no product order.
  // // $0 remaining (voucher) skips postPayNow; the customer cannot opt out.
  // let createOrderSpy: MockInstance<typeof portalGateway.createOrder>;
  // let patchDoneSpy: MockInstance<typeof portalGateway.patchDone>;
  //
  // beforeEach(() => {
  //   createOrderSpy = vi.spyOn(portalGateway, 'createOrder');
  //   patchDoneSpy = vi.spyOn(portalGateway, 'patchDone');
  // });
  scenario('Create product order', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Cart;
    // examples: reloadCart, customerReadyToPlaceOrder, expectedProductOrderRequest
    given('the Customer is verified and has a billing account, plan, number, and eSIM', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ verified: true });
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // typescript body to translate:
      // result = cart.createOrder();
      // TODO: implement step
    });
    then('My Paradise sends the product order request to Mavenir', () => {
      // typescript body to translate:
      // expect(createOrderSpy).toHaveBeenCalledWith(
      //   expect.objectContaining(expectedProductOrderRequest(cart.customer.id)),
      // );
      // TODO: implement step
    });
    when('Mavenir creates the product order', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the order succeeded with pay-up-front', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Cart);
      // expect(cart.orderSuccess).toBe(true);
      // expect(cart.payUpFront).toBe(true);
      // expect(cart.defaultPayment).toBe(true);
      // expect(cart.customer.verified).toBe(true);
      // TODO: implement step
    })
      .and('the Customer onboarding is done', () => {
        // typescript body to translate:
        // expect(patchDoneSpy).toHaveBeenCalledWith(
        //   expect.objectContaining({ customerId: cart.customer.id }),
        // );
        // expect(cart.customer.done).toBe(true);
        // TODO: implement step
      });
  });

  scenario('Pay-up-front charge fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Cart;
    // examples: reloadCart, customerReadyToPlaceOrder
    given('the pay-up-front charge fails', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ verified: true });
      // portalGateway.seedPayUpFrontFailed();
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // typescript body to translate:
      // result = cart.createOrder();
      // TODO: implement step
    });
    then('My Paradise does not send a product order to Mavenir', () => {
      // typescript body to translate:
      // expect(createOrderSpy).not.toHaveBeenCalled();
      // TODO: implement step
    });
    when('My Paradise reloads the cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the order succeeded without pay-up-front', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Cart);
      // expect(cart.orderSuccess).toBe(true);
      // expect(cart.payUpFront).toBe(false);
      // expect(cart.defaultPayment).toBe(true);
      // expect(cart.customer.done).toBe(false);
      // TODO: implement step
    });
  });

  scenario('Product order fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Cart;
    // examples: reloadCart, customerReadyToPlaceOrder
    given('Mavenir returns an error for the product order', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ verified: true });
      // portalGateway.seedCreateOrderError(new Error('Mavenir unavailable'));
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // typescript body to translate:
      // result = cart.createOrder();
      // TODO: implement step
    });
    then('My Paradise sends the product order request to Mavenir', () => {
      // typescript body to translate:
      // expect(createOrderSpy).toHaveBeenCalled();
      // TODO: implement step
    });
    when('My Paradise reloads the cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the order did not succeed', () => {
      // typescript body to translate:
      // expect(cart.orderSuccess).toBe(false);
      // expect(cart.payUpFront).toBeNull();
      // expect(cart.defaultPayment).toBe(true);
      // TODO: implement step
    });
  });

  scenario('Onboarding is already done', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: CartException | undefined;
    // examples: customerReadyToPlaceOrder
    given('the Customer onboarding is already done', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ done: true });
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // typescript body to translate:
      // try { cart.createOrder(); } catch (e) { result = e as CartException; }
      // TODO: implement step
    });
    then('the product order is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(CartException);
      // expect(result?.cause.message).toBe('409');
      // TODO: implement step
    })
      .and('Mavenir does not receive a product order request', () => {
        // typescript body to translate:
        // expect(createOrderSpy).not.toHaveBeenCalled();
        // TODO: implement step
      });
  });

  scenario('Unverified with no bypass and no portability', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Cart;
    // examples: reloadCart, customerReadyToPlaceOrder
    given('the Customer is not verified and the plan does not bypass verification', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ verified: false });
      // TODO: implement step
    });
    when('the Customer places the product order', () => {
      // typescript body to translate:
      // result = cart.createOrder();
      // TODO: implement step
    });
    then('My Paradise does not send a product order to Mavenir', () => {
      // typescript body to translate:
      // expect(createOrderSpy).not.toHaveBeenCalled();
      // TODO: implement step
    })
      .and('the cart is marked to submit the order later', () => {
        // typescript body to translate:
        // expect(result.submitOrder).toBe(true);
        // TODO: implement step
      });
    when('My Paradise reloads the cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the Customer onboarding is done', () => {
      // typescript body to translate:
      // expect(patchDoneSpy).toHaveBeenCalledWith(
      //   expect.objectContaining({ customerId: cart.customer.id }),
      // );
      // expect(cart.customer.done).toBe(true);
      // expect(cart.orderSuccess).toBe(true);
      // expect(cart.customer.verified).toBe(false);
      // TODO: implement step
    });
  });
});

/**
 * Story: View Order Result
 */

story('View Order Result', () => {
  // typescript body to translate:
  // orderResultOutlines.forEach(({ example, seed, orderSuccess, payUpFront, result: expected }) => {
  // });
  scenario('View order result: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: OrderResult;
    //
    // then(expected === OrderResult.AllSet ? 'the order is complete' : 'the order is not yet complete', () => {
    //   expect(result).toBe(expected);
    // });
    // examples: reloadCart, customerReadyToPlaceOrder
    given('the order result is ${example}', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder({ ...seed, orderSuccess, payUpFront });
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    when('the Customer views their order result', () => {
      // typescript body to translate:
      // result = cart.orderResult;
      // TODO: implement step
    });
  });
});

/**
 * Story: Create Order Ticket
 */

story('Create Order Ticket', () => {
  // typescript body to translate:
  // let createTicketSpy: MockInstance<typeof zendeskGateway.create>;
  //
  // beforeEach(() => {
  //   createTicketSpy = vi.spyOn(zendeskGateway, 'create');
  // });
  //
  // ticketOutlines.forEach(({ example, seed, subject }) => {
  // });
  scenario('Create order ticket: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let tickets: ReturnType<Cart['createOrderTicket']>;
    // examples: customerReadyToPlaceOrder, expectedTicketRequest, requesterName
    given('the Customer ${example}', async () => {
      // typescript body to translate:
      // cart = await customerReadyToPlaceOrder(seed);
      // TODO: implement step
    });
    when('the Customer creates the order ticket', () => {
      // typescript body to translate:
      // tickets = cart.createOrderTicket();
      // TODO: implement step
    });
    then('My Paradise sends the ${subject} ticket to Zendesk', () => {
      // typescript body to translate:
      // expect(createTicketSpy).toHaveBeenCalledWith(
      //   expect.objectContaining(expectedTicketRequest(cart.customer, subject)),
      // );
      // TODO: implement step
    });
    when('Zendesk creates the ticket', () => {
      // TODO: implement step
    });
    then('the ticket is created for the Customer', () => {
      // typescript body to translate:
      // expect(tickets.some(ticket => ticket.subject === subject)).toBe(true);
      // expect(tickets[0].requesterName).toBe(requesterName);
      // expect(tickets[0].requesterEmail).toBe(cart.customer.identity.email);
      // TODO: implement step
    });
  });
});
