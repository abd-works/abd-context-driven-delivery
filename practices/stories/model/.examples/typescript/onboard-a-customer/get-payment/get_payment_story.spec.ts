import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import {
  ApplePayCertificate,
  Payment,
  PaymentErrors,
  PaymentReason,
  PaymentResult,
  PaymentStatus,
  SalesChannel,
  appleRepository,
  paymentRepository,
} from '../../../domain/billing/Payment';
import { type Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { ccsGateway } from '../../../domain/systems/mavenir/ccs-gateway';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { appleGateway } from '../../../domain/systems/apple';
import { zendeskGateway, ZendeskSubject } from '../../../domain/systems/zendesk';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { reloadCart } from '../get-number/examples/cart.examples';
import { customerReadyForPayment } from './examples/checkout-cart.examples';
import { maxPaymentAttempts, paymentWithAuthorization, stubAuth } from './examples/payment-authorization.examples';
import { completedAuth, failedAuth } from './examples/payment-status.examples';
import { bermudaApplePayCert, bermudaApplePayCertificate } from './examples/apple-pay-certificate.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  portalGateway.reset();
  ccsGateway.reset();
  appleGateway.reset();
  zendeskGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Enter Payment', () => {
  let authorizeSpy: MockInstance<typeof ccsGateway.authorize>;

  beforeEach(() => {
    authorizeSpy = vi.spyOn(ccsGateway, 'authorize');
  });

  scenario('Enter Payment', ({ given, when, then }) => {
    let cart: Cart;
    let payment: Payment;
    let result: Payment | PaymentErrors;

    given('the Customer is at Checkout with Essentials', async () => {
      cart = await customerReadyForPayment();
      payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
    }).and('Mavenir CCS authorizes stub auth', () => {
      ccsGateway.seedAuthorization(stubAuth.transactionId, stubAuth.html);
    });
    when('the Customer proceeds to adding their payment', () => {
      result = payment.enter();
    });
    then('My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING', () => {
      expect(authorizeSpy).toHaveBeenCalledWith(expect.objectContaining({
        TotalAmount: stubAuth.totalAmount,
        salesChannel: { name: SalesChannel.OnBoarding },
        OrderIdentifier: expect.stringContaining(cart.customer.id),
      }));
    });
    when('Mavenir authorizes the card and returns the hosted payment page', () => {});
    then('the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING', () => {
      expect(result).toBeInstanceOf(Payment);
      expect(payment.transactionId).toBe(stubAuth.transactionId);
      expect(payment.amount).toBe(stubAuth.totalAmount);
      expect(payment.salesChannel).toBe(SalesChannel.OnBoarding);
    });
  });

  scenario('Payment authorization fails to load', ({ given, when, then }) => {
    let cart: Cart;
    let payment: Payment;
    let result: Payment | PaymentErrors;

    given('the Customer is at Checkout with Essentials', async () => {
      cart = await customerReadyForPayment();
      payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
    }).but('Mavenir CCS does not return a payment authorization', () => {
      ccsGateway.seedAuthorizeError(new Error('Payment authorization unavailable'));
    });
    when('the Customer proceeds to adding their payment', () => {
      result = payment.enter();
    });
    then('My Paradise sends the card authorization request to Mavenir', () => {
      expect(authorizeSpy).toHaveBeenCalled();
    });
    when('Mavenir does not return a payment authorization', () => {});
    then('the payment authorization cannot be loaded', () => {
      expect(result).toBeInstanceOf(PaymentErrors);
      expect((result as PaymentErrors).load).not.toBeNull();
      expect(payment.paymentIframe).toBeNull();
    });
  });

  scenario('FAC authorization timeout', ({ given, when, then }) => {
    let cart: Cart;
    let payment: Payment;
    let result: Payment | PaymentErrors;

    given('the Customer is at Checkout with Essentials', async () => {
      cart = await customerReadyForPayment();
      payment = new Payment(cart, paymentRepository, maxPaymentAttempts);
    }).but('Mavenir does not return a transaction id', () => {
      ccsGateway.seedAuthorizeError(new Error('504'));
    });
    when('the Customer proceeds to adding their payment', () => {
      result = payment.enter();
    });
    then('My Paradise sends the card authorization request to Mavenir', () => {
      expect(authorizeSpy).toHaveBeenCalled();
    });
    when('Mavenir does not return a transaction id', () => {});
    then('the payment authorization cannot be loaded', () => {
      expect(result).toBeInstanceOf(PaymentErrors);
      expect((result as PaymentErrors).load).not.toBeNull();
    });
  });
});

// ---------------------------------------------------------------------------

story('Authorize Card', () => {
  let readTokenizedCardSpy: MockInstance<typeof ccsGateway.readTokenizedCard>;
  let authorizeSpy: MockInstance<typeof ccsGateway.authorize>;
  let createTicketSpy: MockInstance<typeof zendeskGateway.create>;

  beforeEach(() => {
    readTokenizedCardSpy = vi.spyOn(ccsGateway, 'readTokenizedCard');
    authorizeSpy = vi.spyOn(ccsGateway, 'authorize');
    createTicketSpy = vi.spyOn(zendeskGateway, 'create');
  });

  scenario('Payment completed', ({ given, when, then }) => {
    let cart: Cart;
    let payment: Payment;
    let result: PaymentStatus | PaymentErrors;

    given('the Customer has stub auth', async () => {
      cart = await customerReadyForPayment();
      payment = paymentWithAuthorization(cart);
    }).and('Mavenir CCS has completed auth', () => {
      ccsGateway.seedPaymentStatus(completedAuth);
    });
    when('the Customer authorizes their card', () => {
      result = payment.checkStatus();
    });
    then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {
      expect(readTokenizedCardSpy).toHaveBeenCalledWith(
        cart.customer.id,
        stubAuth.transactionId,
        SalesChannel.OnBoarding,
      );
    });
    when('Mavenir returns completed auth', async () => {
      cart = await reloadCart(cart);
    });
    then('the payment is authorized', () => {
      expect(result).toBeInstanceOf(PaymentStatus);
      expect((result as PaymentStatus).status).toBe(PaymentResult.Completed);
      expect((result as PaymentStatus).reason).toBe(PaymentReason.Approved);
    }).and('the payment step does not place the order', () => {
      expect(cart.customer.billing).toBeNull();
      expect(cart.orderSuccess).toBeNull();
      expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
    });
  });

  scenario('Card not verified', ({ given, when, then }) => {
    let cart: Cart;
    let payment: Payment;
    let result: PaymentStatus | PaymentErrors;

    given('the Customer has stub auth', async () => {
      cart = await customerReadyForPayment();
      payment = paymentWithAuthorization(cart, maxPaymentAttempts);
    }).and('Mavenir CCS has failed auth', () => {
      ccsGateway.seedPaymentStatus(failedAuth);
      ccsGateway.seedAuthorization(stubAuth.transactionId, stubAuth.html);
    }).and('payment attempts are under the maximum', () => {
      payment.paymentAttempts = 0;
      payment.maxAttempts = maxPaymentAttempts;
    });
    when('the Customer authorizes their card', () => {
      result = payment.checkStatus();
    });
    then('My Paradise sends the tokenized card request to Mavenir', () => {
      expect(readTokenizedCardSpy).toHaveBeenCalledWith(
        cart.customer.id,
        stubAuth.transactionId,
        SalesChannel.OnBoarding,
      );
    });
    when('Mavenir returns failed auth', () => {});
    then('the card is not verified', () => {
      expect(result).toBeInstanceOf(PaymentErrors);
      expect((result as PaymentErrors).unverified).not.toBeNull();
    }).and('My Paradise requests a fresh payment authorization from Mavenir', () => {
      expect(authorizeSpy).toHaveBeenCalled();
      expect(payment.transactionId).toBe(stubAuth.transactionId);
      expect(payment.amount).toBe(stubAuth.totalAmount);
      expect(payment.salesChannel).toBe(SalesChannel.OnBoarding);
    });
  });

  scenario('Maximum payment attempts', ({ given, when, then }) => {
    let cart: Cart;
    let payment: Payment;
    let result: PaymentStatus | PaymentErrors;

    given('the Customer has stub auth', async () => {
      cart = await customerReadyForPayment();
      payment = paymentWithAuthorization(cart, maxPaymentAttempts);
    }).and('Mavenir CCS has failed auth', () => {
      ccsGateway.seedPaymentStatus(failedAuth);
    }).and('payment attempts equal the maximum', () => {
      payment.paymentAttempts = maxPaymentAttempts;
    });
    when('the Customer authorizes their card', () => {
      result = payment.checkStatus();
    });
    then('My Paradise sends the tokenized card request to Mavenir for stub auth', () => {
      expect(readTokenizedCardSpy).toHaveBeenCalledWith(
        cart.customer.id,
        stubAuth.transactionId,
        SalesChannel.OnBoarding,
      );
    });
    when('Mavenir returns failed auth', async () => {
      cart = await reloadCart(cart);
    });
    then('My Paradise records the failed card addition with Zendesk', () => {
      expect(createTicketSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          ticket: expect.objectContaining({
            subject: ZendeskSubject.CardAdditionFailed,
          }),
        }),
      );
      expect(result).toBeInstanceOf(PaymentStatus);
      expect((result as PaymentStatus).status).toBe(PaymentResult.Failed);
      expect((result as PaymentStatus).reason).toBe(PaymentReason.Declined);
    }).and('the payment step does not place the order', () => {
      expect(cart.customer.billing).toBeNull();
      expect(cart.orderSuccess).toBeNull();
      expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
    });
  });
});

// ---------------------------------------------------------------------------

story('Provide Apple Pay Certificate', () => {
  let readSpy: MockInstance<typeof appleGateway.read>;

  beforeEach(() => {
    readSpy = vi.spyOn(appleGateway, 'read');
  });

  scenario('Provide Apple Pay certificate', ({ given, when, then }) => {
    let certificate: ApplePayCertificate;

    given('the Apple Pay merchant certificate is available', () => {
      appleGateway.seed(bermudaApplePayCert);
    });
    when('My Paradise provides the Apple Pay certificate', () => {
      certificate = appleRepository.read();
    });
    then('My Paradise sends the certificate request to Apple', () => {
      expect(readSpy).toHaveBeenCalledOnce();
    });
    when('Apple returns Bermuda Apple Pay cert', () => {});
    then('My Paradise returns Bermuda Apple Pay cert', () => {
      expect(certificate).toBeInstanceOf(ApplePayCertificate);
      expect(certificate.keyIdentifier).toBe(bermudaApplePayCertificate.keyIdentifier);
      expect(certificate.certificate).toBe(bermudaApplePayCertificate.certificate);
    });
  });
});
