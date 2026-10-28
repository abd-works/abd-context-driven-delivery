from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import reloadCart, customerReadyToPlaceOrder, expectedBillingAccountRequest, expectedProductOrderRequest, expectedTicketRequest, requesterName


# Epic: Place Order
# Orders: 0.0.9

# Story: Create Billing Account
with story("Create Billing Account"):
    # typescript body to translate:
    # let createBillingSpy: MockInstance<typeof portalGateway.createBilling>;
    #
    # beforeEach(() => {
    #   createBillingSpy = vi.spyOn(portalGateway, 'createBilling');
    # });
        with scenario("Create billing account"):
            # typescript body to translate:
            # let cart: Cart;
            # let billing: Billing;
            # examples: reloadCart, customerReadyToPlaceOrder, expectedBillingAccountRequest
            with given("the Customer has a configured cart and no billing account"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ billing: false });
                pass
            with when("the Customer creates a billing account"):
                # typescript body to translate:
                # billing = cart.customer.createBilling();
                pass
            with then("My Paradise sends the billing account request to Mavenir"):
                # typescript body to translate:
                # expect(createBillingSpy).toHaveBeenCalledWith(
                #   expect.objectContaining(expectedBillingAccountRequest(cart.customer.id)),
                # );
                pass
            with when("Mavenir creates the billing account"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the Customer has a billing account"):
                # typescript body to translate:
                # expect(billing).toBeInstanceOf(Billing);
                # expect(cart.customer.billing?.id).toBe(billing.id);
                pass
            with and_("the Customer is on the Done step"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.Done);
                pass
        with scenario("Billing account already exists"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: BillingException | undefined;
            # examples: customerReadyToPlaceOrder
            with given("the Customer already has a billing account"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder();
                pass
            with when("the Customer creates a billing account"):
                # typescript body to translate:
                # try { cart.customer.createBilling(); } catch (e) { result = e as BillingException; }
                pass
            with then("the billing account is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(BillingException);
                # expect(result?.cause.message).toBe('409');
                pass
            with and_("Mavenir does not receive a billing account request"):
                # typescript body to translate:
                # expect(createBillingSpy).not.toHaveBeenCalled();
                pass
        with scenario("Billing account creation fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: BillingException | undefined;
            # examples: reloadCart, customerReadyToPlaceOrder
            with given("Mavenir returns an error for the billing account request"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ billing: false });
                # portalGateway.seedCreateBillingError(new Error('Mavenir unavailable'));
                pass
            with when("the Customer creates a billing account"):
                # typescript body to translate:
                # try { cart.customer.createBilling(); } catch (e) { result = e as BillingException; }
                pass
            with then("the billing account cannot be created"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(BillingException);
                # expect(result?.message).toBe('Could not create billing account.');
                pass
            with when("My Paradise reloads the customer"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the Customer has no billing account"):
                # typescript body to translate:
                # expect(cart.customer.billing).toBeNull();
                pass

# Story: Create Product Order
with story("Create Product Order"):
    # typescript body to translate:
    # // Pay-up-front is internal: GrowthBook pay-up-front + remaining amount at cook.
    # // Midtier createOrder calls payUpFront() / postPayNow('onboarding', totalAmount) after a payment
    # // method exists. Charge failure: Zendesk payUpFrontFailed, { payUpFront: false }, no product order.
    # // $0 remaining (voucher) skips postPayNow; the customer cannot opt out.
    # let createOrderSpy: MockInstance<typeof portalGateway.createOrder>;
    # let patchDoneSpy: MockInstance<typeof portalGateway.patchDone>;
    #
    # beforeEach(() => {
    #   createOrderSpy = vi.spyOn(portalGateway, 'createOrder');
    #   patchDoneSpy = vi.spyOn(portalGateway, 'patchDone');
    # });
        with scenario("Create product order"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Cart;
            # examples: reloadCart, customerReadyToPlaceOrder, expectedProductOrderRequest
            with given("the Customer is verified and has a billing account, plan, number, and eSIM"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ verified: true });
                pass
            with when("the Customer places the product order"):
                # typescript body to translate:
                # result = cart.createOrder();
                pass
            with then("My Paradise sends the product order request to Mavenir"):
                # typescript body to translate:
                # expect(createOrderSpy).toHaveBeenCalledWith(
                #   expect.objectContaining(expectedProductOrderRequest(cart.customer.id)),
                # );
                pass
            with when("Mavenir creates the product order"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the order succeeded with pay-up-front"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Cart);
                # expect(cart.orderSuccess).toBe(true);
                # expect(cart.payUpFront).toBe(true);
                # expect(cart.defaultPayment).toBe(true);
                # expect(cart.customer.verified).toBe(true);
                pass
            with and_("the Customer onboarding is done"):
                # typescript body to translate:
                # expect(patchDoneSpy).toHaveBeenCalledWith(
                #   expect.objectContaining({ customerId: cart.customer.id }),
                # );
                # expect(cart.customer.done).toBe(true);
                pass
        with scenario("Pay-up-front charge fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Cart;
            # examples: reloadCart, customerReadyToPlaceOrder
            with given("the pay-up-front charge fails"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ verified: true });
                # portalGateway.seedPayUpFrontFailed();
                pass
            with when("the Customer places the product order"):
                # typescript body to translate:
                # result = cart.createOrder();
                pass
            with then("My Paradise does not send a product order to Mavenir"):
                # typescript body to translate:
                # expect(createOrderSpy).not.toHaveBeenCalled();
                pass
            with when("My Paradise reloads the cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the order succeeded without pay-up-front"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Cart);
                # expect(cart.orderSuccess).toBe(true);
                # expect(cart.payUpFront).toBe(false);
                # expect(cart.defaultPayment).toBe(true);
                # expect(cart.customer.done).toBe(false);
                pass
        with scenario("Product order fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Cart;
            # examples: reloadCart, customerReadyToPlaceOrder
            with given("Mavenir returns an error for the product order"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ verified: true });
                # portalGateway.seedCreateOrderError(new Error('Mavenir unavailable'));
                pass
            with when("the Customer places the product order"):
                # typescript body to translate:
                # result = cart.createOrder();
                pass
            with then("My Paradise sends the product order request to Mavenir"):
                # typescript body to translate:
                # expect(createOrderSpy).toHaveBeenCalled();
                pass
            with when("My Paradise reloads the cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the order did not succeed"):
                # typescript body to translate:
                # expect(cart.orderSuccess).toBe(false);
                # expect(cart.payUpFront).toBeNull();
                # expect(cart.defaultPayment).toBe(true);
                pass
        with scenario("Onboarding is already done"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: CartException | undefined;
            # examples: customerReadyToPlaceOrder
            with given("the Customer onboarding is already done"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ done: true });
                pass
            with when("the Customer places the product order"):
                # typescript body to translate:
                # try { cart.createOrder(); } catch (e) { result = e as CartException; }
                pass
            with then("the product order is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(CartException);
                # expect(result?.cause.message).toBe('409');
                pass
            with and_("Mavenir does not receive a product order request"):
                # typescript body to translate:
                # expect(createOrderSpy).not.toHaveBeenCalled();
                pass
        with scenario("Unverified with no bypass and no portability"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Cart;
            # examples: reloadCart, customerReadyToPlaceOrder
            with given("the Customer is not verified and the plan does not bypass verification"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ verified: false });
                pass
            with when("the Customer places the product order"):
                # typescript body to translate:
                # result = cart.createOrder();
                pass
            with then("My Paradise does not send a product order to Mavenir"):
                # typescript body to translate:
                # expect(createOrderSpy).not.toHaveBeenCalled();
                pass
            with and_("the cart is marked to submit the order later"):
                # typescript body to translate:
                # expect(result.submitOrder).toBe(true);
                pass
            with when("My Paradise reloads the cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the Customer onboarding is done"):
                # typescript body to translate:
                # expect(patchDoneSpy).toHaveBeenCalledWith(
                #   expect.objectContaining({ customerId: cart.customer.id }),
                # );
                # expect(cart.customer.done).toBe(true);
                # expect(cart.orderSuccess).toBe(true);
                # expect(cart.customer.verified).toBe(false);
                pass

# Story: View Order Result
with story("View Order Result"):
    # typescript body to translate:
    # orderResultOutlines.forEach(({ example, seed, orderSuccess, payUpFront, result: expected }) => {
    # });
        with scenario("View order result: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: OrderResult;
            #
            # then(expected === OrderResult.AllSet ? 'the order is complete' : 'the order is not yet complete', () => {
            #   expect(result).toBe(expected);
            # });
            # examples: reloadCart, customerReadyToPlaceOrder
            with given("the order result is ${example}"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder({ ...seed, orderSuccess, payUpFront });
                # cart = await reloadCart(cart);
                pass
            with when("the Customer views their order result"):
                # typescript body to translate:
                # result = cart.orderResult;
                pass

# Story: Create Order Ticket
with story("Create Order Ticket"):
    # typescript body to translate:
    # let createTicketSpy: MockInstance<typeof zendeskGateway.create>;
    #
    # beforeEach(() => {
    #   createTicketSpy = vi.spyOn(zendeskGateway, 'create');
    # });
    #
    # ticketOutlines.forEach(({ example, seed, subject }) => {
    # });
        with scenario("Create order ticket: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # let tickets: ReturnType<Cart['createOrderTicket']>;
            # examples: customerReadyToPlaceOrder, expectedTicketRequest, requesterName
            with given("the Customer ${example}"):
                # typescript body to translate:
                # cart = await customerReadyToPlaceOrder(seed);
                pass
            with when("the Customer creates the order ticket"):
                # typescript body to translate:
                # tickets = cart.createOrderTicket();
                pass
            with then("My Paradise sends the ${subject} ticket to Zendesk"):
                # typescript body to translate:
                # expect(createTicketSpy).toHaveBeenCalledWith(
                #   expect.objectContaining(expectedTicketRequest(cart.customer, subject)),
                # );
                pass
            with when("Zendesk creates the ticket"):
                pass
            with then("the ticket is created for the Customer"):
                # typescript body to translate:
                # expect(tickets.some(ticket => ticket.subject === subject)).toBe(true);
                # expect(tickets[0].requesterName).toBe(requesterName);
                # expect(tickets[0].requesterEmail).toBe(cart.customer.identity.email);
                pass
