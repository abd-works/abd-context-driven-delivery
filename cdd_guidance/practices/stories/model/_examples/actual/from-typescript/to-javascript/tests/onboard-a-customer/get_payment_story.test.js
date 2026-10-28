/**
 * Epic: Get Payment
 * Orders: 0.0.4
 */

import { background, scenario, story } from "../story-test.js";
import { customerReadyForPayment, maxPaymentAttempts, stubAuth, reloadCart, paymentWithAuthorization, completedAuth, failedAuth, bermudaApplePayCert, bermudaApplePayCertificate } from "./examples";

/**
 * Story: Enter Payment
 */

story('Enter Payment', () => {
  // typescript body to translate:
  // let authorizeSpy: MockInstance<typeof ccsGateway.authorize>;
  //
  // beforeEach(() => {
  //   authorizeSpy = vi.spyOn(ccsGateway, 'authorize');
  // });
  scenario('Enter Payment', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let payment: Payment;
    // let result: Payment | PaymentErrors;
    // examples: customerReadyForPayment, maxPaymentAttempts, stubAuth
    given('the Customer is at Checkout with Essentials', async () => {
      // typescript body to translate:
      // cart = await customerReadyForPayment();
      // payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
      // TODO: implement step
    })
      .and('Mavenir CCS authorizes stub auth', () => {
        // typescript body to translate:
        // ccsGateway.seedAuthorization(stubAuth.transactionId, stubAuth.html);
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // typescript body to translate:
      // result = payment.enter();
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {
      // typescript body to translate:
      // expect(authorizeSpy).toHaveBeenCalledWith(expect.objectContaining({
      //   TotalAmount: stubAuth.totalAmount,
      //   salesChannel: { name: SalesChannel.OnBoarding },
      //   OrderIdentifier: expect.stringContaining(cart.customer.id),
      // }));
      // TODO: implement step
    });
    when('Mavenir authorizes the card and returns the hosted payment page', () => {
      // TODO: implement step
    });
    then('the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Payment);
      // expect(payment.transactionId).toBe(stubAuth.transactionId);
      // expect(payment.amount).toBe(stubAuth.totalAmount);
      // expect(payment.salesChannel).toBe(SalesChannel.OnBoarding);
      // TODO: implement step
    });
  });

  scenario('Payment authorization fails to load', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let payment: Payment;
    // let result: Payment | PaymentErrors;
    // examples: customerReadyForPayment, maxPaymentAttempts
    given('the Customer is at Checkout with Essentials', async () => {
      // typescript body to translate:
      // cart = await customerReadyForPayment();
      // payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
      // TODO: implement step
    })
      .but('Mavenir CCS does not return a payment authorization', () => {
        // typescript body to translate:
        // ccsGateway.seedAuthorizeError(new Error('Payment authorization unavailable'));
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // typescript body to translate:
      // result = payment.enter();
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir', () => {
      // typescript body to translate:
      // expect(authorizeSpy).toHaveBeenCalled();
      // TODO: implement step
    });
    when('Mavenir does not return a payment authorization', () => {
      // TODO: implement step
    });
    then('the payment authorization cannot be loaded', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(PaymentErrors);
      // expect((result as PaymentErrors).load).not.toBeNull();
      // expect(payment.paymentIframe).toBeNull();
      // TODO: implement step
    });
  });

  scenario('FAC authorization timeout', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let payment: Payment;
    // let result: Payment | PaymentErrors;
    // examples: customerReadyForPayment, maxPaymentAttempts
    given('the Customer is at Checkout with Essentials', async () => {
      // typescript body to translate:
      // cart = await customerReadyForPayment();
      // payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
      // TODO: implement step
    })
      .but('Mavenir does not return a transaction id', () => {
        // typescript body to translate:
        // ccsGateway.seedAuthorizeError(new Error('504'));
        // TODO: implement step
      });
    when('the Customer proceeds to adding their payment', () => {
      // typescript body to translate:
      // result = payment.enter();
      // TODO: implement step
    });
    then('My Paradise sends the card authorization request to Mavenir', () => {
      // typescript body to translate:
      // expect(authorizeSpy).toHaveBeenCalled();
      // TODO: implement step
    });
    when('Mavenir does not return a transaction id', () => {
      // TODO: implement step
    });
    then('the payment authorization cannot be loaded', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(PaymentErrors);
      // expect((result as PaymentErrors).load).not.toBeNull();
      // TODO: implement step
    });
  });
});

/**
 * Story: Authorize Card
 */

story('Authorize Card', () => {
  // typescript body to translate:
  // let readTokenizedCardSpy: MockInstance<typeof ccsGateway.readTokenizedCard>;
  // let authorizeSpy: MockInstance<typeof ccsGateway.authorize>;
  // let createTicketSpy: MockInstance<typeof zendeskGateway.create>;
  //
  // beforeEach(() => {
  //   readTokenizedCardSpy = vi.spyOn(ccsGateway, 'readTokenizedCard');
  //   authorizeSpy = vi.spyOn(ccsGateway, 'authorize');
  //   createTicketSpy = vi.spyOn(zendeskGateway, 'create');
  // });
  scenario('Payment completed', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let payment: Payment;
    // let result: PaymentStatus | PaymentErrors;
    // examples: reloadCart, customerReadyForPayment, paymentWithAuthorization, stubAuth, completedAuth
    given('the Customer has stub auth', async () => {
      // typescript body to translate:
      // cart = await customerReadyForPayment();
      // payment = paymentWithAuthorization(cart);
      // TODO: implement step
    })
      .and('Mavenir CCS has completed auth', () => {
        // typescript body to translate:
        // ccsGateway.seedPaymentStatus(completedAuth);
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // typescript body to translate:
      // result = payment.checkStatus();
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {
      // typescript body to translate:
      // expect(readTokenizedCardSpy).toHaveBeenCalledWith(
      //   cart.customer.id,
      //   stubAuth.transactionId,
      //   SalesChannel.OnBoarding,
      // );
      // TODO: implement step
    });
    when('Mavenir returns completed auth', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the payment is authorized', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(PaymentStatus);
      // expect((result as PaymentStatus).status).toBe(PaymentResult.Completed);
      // expect((result as PaymentStatus).reason).toBe(PaymentReason.Approved);
      // TODO: implement step
    })
      .and('the payment step does not place the order', () => {
        // typescript body to translate:
        // expect(cart.customer.billing).toBeNull();
        // expect(cart.orderSuccess).toBeNull();
        // expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
        // TODO: implement step
      });
  });

  scenario('Card not verified', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let payment: Payment;
    // let result: PaymentStatus | PaymentErrors;
    // examples: customerReadyForPayment, maxPaymentAttempts, paymentWithAuthorization, stubAuth, failedAuth
    given('the Customer has stub auth', async () => {
      // typescript body to translate:
      // cart = await customerReadyForPayment();
      // payment = paymentWithAuthorization(cart, maxPaymentAttempts);
      // TODO: implement step
    })
      .and('Mavenir CCS has failed auth', () => {
        // typescript body to translate:
        // ccsGateway.seedPaymentStatus(failedAuth);
        // ccsGateway.seedAuthorization(stubAuth.transactionId, stubAuth.html);
        // TODO: implement step
      })
      .and('payment attempts are under the maximum', () => {
        // typescript body to translate:
        // payment.paymentAttempts = 0;
        // payment.maxAttempts = maxPaymentAttempts;
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // typescript body to translate:
      // result = payment.checkStatus();
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir', () => {
      // typescript body to translate:
      // expect(readTokenizedCardSpy).toHaveBeenCalledWith(
      //   cart.customer.id,
      //   stubAuth.transactionId,
      //   SalesChannel.OnBoarding,
      // );
      // TODO: implement step
    });
    when('Mavenir returns failed auth', () => {
      // TODO: implement step
    });
    then('the card is not verified', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(PaymentErrors);
      // expect((result as PaymentErrors).unverified).not.toBeNull();
      // TODO: implement step
    })
      .and('My Paradise requests a fresh payment authorization from Mavenir', () => {
        // typescript body to translate:
        // expect(authorizeSpy).toHaveBeenCalled();
        // expect(payment.transactionId).toBe(stubAuth.transactionId);
        // expect(payment.amount).toBe(stubAuth.totalAmount);
        // expect(payment.salesChannel).toBe(SalesChannel.OnBoarding);
        // TODO: implement step
      });
  });

  scenario('Maximum payment attempts', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let payment: Payment;
    // let result: PaymentStatus | PaymentErrors;
    // examples: reloadCart, customerReadyForPayment, maxPaymentAttempts, paymentWithAuthorization, stubAuth, failedAuth
    given('the Customer has stub auth', async () => {
      // typescript body to translate:
      // cart = await customerReadyForPayment();
      // payment = paymentWithAuthorization(cart, maxPaymentAttempts);
      // TODO: implement step
    })
      .and('Mavenir CCS has failed auth', () => {
        // typescript body to translate:
        // ccsGateway.seedPaymentStatus(failedAuth);
        // TODO: implement step
      })
      .and('payment attempts equal the maximum', () => {
        // typescript body to translate:
        // payment.paymentAttempts = maxPaymentAttempts;
        // TODO: implement step
      });
    when('the Customer authorizes their card', () => {
      // typescript body to translate:
      // result = payment.checkStatus();
      // TODO: implement step
    });
    then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {
      // typescript body to translate:
      // expect(readTokenizedCardSpy).toHaveBeenCalledWith(
      //   cart.customer.id,
      //   stubAuth.transactionId,
      //   SalesChannel.OnBoarding,
      // );
      // TODO: implement step
    });
    when('Mavenir returns failed auth', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise records the failed card addition with Zendesk', () => {
      // typescript body to translate:
      // expect(createTicketSpy).toHaveBeenCalledWith(
      //   expect.objectContaining({
      //     ticket: expect.objectContaining({
      //       subject: ZendeskSubject.CardAdditionFailed,
      //     }),
      //   }),
      // );
      // expect(result).toBeInstanceOf(PaymentStatus);
      // expect((result as PaymentStatus).status).toBe(PaymentResult.Failed);
      // expect((result as PaymentStatus).reason).toBe(PaymentReason.Declined);
      // TODO: implement step
    })
      .and('the payment step does not place the order', () => {
        // typescript body to translate:
        // expect(cart.customer.billing).toBeNull();
        // expect(cart.orderSuccess).toBeNull();
        // expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
        // TODO: implement step
      });
  });
});

/**
 * Story: Provide Apple Pay Certificate
 */

story('Provide Apple Pay Certificate', () => {
  // typescript body to translate:
  // let readSpy: MockInstance<typeof appleGateway.read>;
  //
  // beforeEach(() => {
  //   readSpy = vi.spyOn(appleGateway, 'read');
  // });
  scenario('Provide Apple Pay certificate', ({ given, when, then }) => {
    // typescript body to translate:
    // let certificate: ApplePayCertificate;
    // examples: bermudaApplePayCert, bermudaApplePayCertificate
    given('the Apple Pay merchant certificate is available', () => {
      // typescript body to translate:
      // appleGateway.seed(bermudaApplePayCert);
      // TODO: implement step
    });
    when('My Paradise provides the Apple Pay certificate', () => {
      // typescript body to translate:
      // certificate = appleRepository.read();
      // TODO: implement step
    });
    then('My Paradise sends the certificate request to Apple', () => {
      // typescript body to translate:
      // expect(readSpy).toHaveBeenCalledOnce();
      // TODO: implement step
    });
    when('Apple returns Bermuda Apple Pay cert', () => {
      // TODO: implement step
    });
    then('My Paradise returns Bermuda Apple Pay cert', () => {
      // typescript body to translate:
      // expect(certificate).toBeInstanceOf(ApplePayCertificate);
      // expect(certificate.keyIdentifier).toBe(bermudaApplePayCertificate.keyIdentifier);
      // expect(certificate.certificate).toBe(bermudaApplePayCertificate.certificate);
      // TODO: implement step
    });
  });
});
