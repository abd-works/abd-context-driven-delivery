from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import customerReadyForPayment, maxPaymentAttempts, stubAuth, reloadCart, paymentWithAuthorization, completedAuth, failedAuth, bermudaApplePayCert, bermudaApplePayCertificate


# Epic: Get Payment
# Orders: 0.0.4

# Story: Enter Payment
with story("Enter Payment"):
    # typescript body to translate:
    # let authorizeSpy: MockInstance<typeof ccsGateway.authorize>;
    #
    # beforeEach(() => {
    #   authorizeSpy = vi.spyOn(ccsGateway, 'authorize');
    # });
        with scenario("Enter Payment"):
            # typescript body to translate:
            # let cart: Cart;
            # let payment: Payment;
            # let result: Payment | PaymentErrors;
            # examples: customerReadyForPayment, maxPaymentAttempts, stubAuth
            with given("the Customer is at Checkout with Essentials"):
                # typescript body to translate:
                # cart = await customerReadyForPayment();
                # payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
                pass
            with and_("Mavenir CCS authorizes stub auth"):
                # typescript body to translate:
                # ccsGateway.seedAuthorization(stubAuth.transactionId, stubAuth.html);
                pass
            with when("the Customer proceeds to adding their payment"):
                # typescript body to translate:
                # result = payment.enter();
                pass
            with then("My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING"):
                # typescript body to translate:
                # expect(authorizeSpy).toHaveBeenCalledWith(expect.objectContaining({
                #   TotalAmount: stubAuth.totalAmount,
                #   salesChannel: { name: SalesChannel.OnBoarding },
                #   OrderIdentifier: expect.stringContaining(cart.customer.id),
                # }));
                pass
            with when("Mavenir authorizes the card and returns the hosted payment page"):
                pass
            with then("the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Payment);
                # expect(payment.transactionId).toBe(stubAuth.transactionId);
                # expect(payment.amount).toBe(stubAuth.totalAmount);
                # expect(payment.salesChannel).toBe(SalesChannel.OnBoarding);
                pass
        with scenario("Payment authorization fails to load"):
            # typescript body to translate:
            # let cart: Cart;
            # let payment: Payment;
            # let result: Payment | PaymentErrors;
            # examples: customerReadyForPayment, maxPaymentAttempts
            with given("the Customer is at Checkout with Essentials"):
                # typescript body to translate:
                # cart = await customerReadyForPayment();
                # payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
                pass
            with but_("Mavenir CCS does not return a payment authorization"):
                # typescript body to translate:
                # ccsGateway.seedAuthorizeError(new Error('Payment authorization unavailable'));
                pass
            with when("the Customer proceeds to adding their payment"):
                # typescript body to translate:
                # result = payment.enter();
                pass
            with then("My Paradise sends the card authorization request to Mavenir"):
                # typescript body to translate:
                # expect(authorizeSpy).toHaveBeenCalled();
                pass
            with when("Mavenir does not return a payment authorization"):
                pass
            with then("the payment authorization cannot be loaded"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(PaymentErrors);
                # expect((result as PaymentErrors).load).not.toBeNull();
                # expect(payment.paymentIframe).toBeNull();
                pass
        with scenario("FAC authorization timeout"):
            # typescript body to translate:
            # let cart: Cart;
            # let payment: Payment;
            # let result: Payment | PaymentErrors;
            # examples: customerReadyForPayment, maxPaymentAttempts
            with given("the Customer is at Checkout with Essentials"):
                # typescript body to translate:
                # cart = await customerReadyForPayment();
                # payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
                pass
            with but_("Mavenir does not return a transaction id"):
                # typescript body to translate:
                # ccsGateway.seedAuthorizeError(new Error('504'));
                pass
            with when("the Customer proceeds to adding their payment"):
                # typescript body to translate:
                # result = payment.enter();
                pass
            with then("My Paradise sends the card authorization request to Mavenir"):
                # typescript body to translate:
                # expect(authorizeSpy).toHaveBeenCalled();
                pass
            with when("Mavenir does not return a transaction id"):
                pass
            with then("the payment authorization cannot be loaded"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(PaymentErrors);
                # expect((result as PaymentErrors).load).not.toBeNull();
                pass

# Story: Authorize Card
with story("Authorize Card"):
    # typescript body to translate:
    # let readTokenizedCardSpy: MockInstance<typeof ccsGateway.readTokenizedCard>;
    # let authorizeSpy: MockInstance<typeof ccsGateway.authorize>;
    # let createTicketSpy: MockInstance<typeof zendeskGateway.create>;
    #
    # beforeEach(() => {
    #   readTokenizedCardSpy = vi.spyOn(ccsGateway, 'readTokenizedCard');
    #   authorizeSpy = vi.spyOn(ccsGateway, 'authorize');
    #   createTicketSpy = vi.spyOn(zendeskGateway, 'create');
    # });
        with scenario("Payment completed"):
            # typescript body to translate:
            # let cart: Cart;
            # let payment: Payment;
            # let result: PaymentStatus | PaymentErrors;
            # examples: reloadCart, customerReadyForPayment, paymentWithAuthorization, stubAuth, completedAuth
            with given("the Customer has stub auth"):
                # typescript body to translate:
                # cart = await customerReadyForPayment();
                # payment = paymentWithAuthorization(cart);
                pass
            with and_("Mavenir CCS has completed auth"):
                # typescript body to translate:
                # ccsGateway.seedPaymentStatus(completedAuth);
                pass
            with when("the Customer authorizes their card"):
                # typescript body to translate:
                # result = payment.checkStatus();
                pass
            with then("My Paradise sends the tokenized card request to Mavenir for stub auth"):
                # typescript body to translate:
                # expect(readTokenizedCardSpy).toHaveBeenCalledWith(
                #   cart.customer.id,
                #   stubAuth.transactionId,
                #   SalesChannel.OnBoarding,
                # );
                pass
            with when("Mavenir returns completed auth"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the payment is authorized"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(PaymentStatus);
                # expect((result as PaymentStatus).status).toBe(PaymentResult.Completed);
                # expect((result as PaymentStatus).reason).toBe(PaymentReason.Approved);
                pass
            with and_("the payment step does not place the order"):
                # typescript body to translate:
                # expect(cart.customer.billing).toBeNull();
                # expect(cart.orderSuccess).toBeNull();
                # expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
                pass
        with scenario("Card not verified"):
            # typescript body to translate:
            # let cart: Cart;
            # let payment: Payment;
            # let result: PaymentStatus | PaymentErrors;
            # examples: customerReadyForPayment, maxPaymentAttempts, paymentWithAuthorization, stubAuth, failedAuth
            with given("the Customer has stub auth"):
                # typescript body to translate:
                # cart = await customerReadyForPayment();
                # payment = paymentWithAuthorization(cart, maxPaymentAttempts);
                pass
            with and_("Mavenir CCS has failed auth"):
                # typescript body to translate:
                # ccsGateway.seedPaymentStatus(failedAuth);
                # ccsGateway.seedAuthorization(stubAuth.transactionId, stubAuth.html);
                pass
            with and_("payment attempts are under the maximum"):
                # typescript body to translate:
                # payment.paymentAttempts = 0;
                # payment.maxAttempts = maxPaymentAttempts;
                pass
            with when("the Customer authorizes their card"):
                # typescript body to translate:
                # result = payment.checkStatus();
                pass
            with then("My Paradise sends the tokenized card request to Mavenir"):
                # typescript body to translate:
                # expect(readTokenizedCardSpy).toHaveBeenCalledWith(
                #   cart.customer.id,
                #   stubAuth.transactionId,
                #   SalesChannel.OnBoarding,
                # );
                pass
            with when("Mavenir returns failed auth"):
                pass
            with then("the card is not verified"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(PaymentErrors);
                # expect((result as PaymentErrors).unverified).not.toBeNull();
                pass
            with and_("My Paradise requests a fresh payment authorization from Mavenir"):
                # typescript body to translate:
                # expect(authorizeSpy).toHaveBeenCalled();
                # expect(payment.transactionId).toBe(stubAuth.transactionId);
                # expect(payment.amount).toBe(stubAuth.totalAmount);
                # expect(payment.salesChannel).toBe(SalesChannel.OnBoarding);
                pass
        with scenario("Maximum payment attempts"):
            # typescript body to translate:
            # let cart: Cart;
            # let payment: Payment;
            # let result: PaymentStatus | PaymentErrors;
            # examples: reloadCart, customerReadyForPayment, maxPaymentAttempts, paymentWithAuthorization, stubAuth, failedAuth
            with given("the Customer has stub auth"):
                # typescript body to translate:
                # cart = await customerReadyForPayment();
                # payment = paymentWithAuthorization(cart, maxPaymentAttempts);
                pass
            with and_("Mavenir CCS has failed auth"):
                # typescript body to translate:
                # ccsGateway.seedPaymentStatus(failedAuth);
                pass
            with and_("payment attempts equal the maximum"):
                # typescript body to translate:
                # payment.paymentAttempts = maxPaymentAttempts;
                pass
            with when("the Customer authorizes their card"):
                # typescript body to translate:
                # result = payment.checkStatus();
                pass
            with then("My Paradise sends the tokenized card request to Mavenir for stub auth"):
                # typescript body to translate:
                # expect(readTokenizedCardSpy).toHaveBeenCalledWith(
                #   cart.customer.id,
                #   stubAuth.transactionId,
                #   SalesChannel.OnBoarding,
                # );
                pass
            with when("Mavenir returns failed auth"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise records the failed card addition with Zendesk"):
                # typescript body to translate:
                # expect(createTicketSpy).toHaveBeenCalledWith(
                #   expect.objectContaining({
                #     ticket: expect.objectContaining({
                #       subject: ZendeskSubject.CardAdditionFailed,
                #     }),
                #   }),
                # );
                # expect(result).toBeInstanceOf(PaymentStatus);
                # expect((result as PaymentStatus).status).toBe(PaymentResult.Failed);
                # expect((result as PaymentStatus).reason).toBe(PaymentReason.Declined);
                pass
            with and_("the payment step does not place the order"):
                # typescript body to translate:
                # expect(cart.customer.billing).toBeNull();
                # expect(cart.orderSuccess).toBeNull();
                # expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
                pass

# Story: Provide Apple Pay Certificate
with story("Provide Apple Pay Certificate"):
    # typescript body to translate:
    # let readSpy: MockInstance<typeof appleGateway.read>;
    #
    # beforeEach(() => {
    #   readSpy = vi.spyOn(appleGateway, 'read');
    # });
        with scenario("Provide Apple Pay certificate"):
            # typescript body to translate:
            # let certificate: ApplePayCertificate;
            # examples: bermudaApplePayCert, bermudaApplePayCertificate
            with given("the Apple Pay merchant certificate is available"):
                # typescript body to translate:
                # appleGateway.seed(bermudaApplePayCert);
                pass
            with when("My Paradise provides the Apple Pay certificate"):
                # typescript body to translate:
                # certificate = appleRepository.read();
                pass
            with then("My Paradise sends the certificate request to Apple"):
                # typescript body to translate:
                # expect(readSpy).toHaveBeenCalledOnce();
                pass
            with when("Apple returns Bermuda Apple Pay cert"):
                pass
            with then("My Paradise returns Bermuda Apple Pay cert"):
                # typescript body to translate:
                # expect(certificate).toBeInstanceOf(ApplePayCertificate);
                # expect(certificate.keyIdentifier).toBe(bermudaApplePayCertificate.keyIdentifier);
                # expect(certificate.certificate).toBe(bermudaApplePayCertificate.certificate);
                pass
