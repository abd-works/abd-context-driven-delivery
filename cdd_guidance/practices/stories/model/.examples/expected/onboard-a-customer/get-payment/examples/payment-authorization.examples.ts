import { SalesChannel, Payment, PaymentIframe, paymentRepository } from '../../../../domain/billing/Payment';
import type { Cart } from '../../../../domain/cart/Cart';

export const stubAuth = {
  transactionId: 'd4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3',
  totalAmount: 1,
  salesChannel: SalesChannel.OnBoarding,
  html: '<html>FAC HPP</html>',
};

export const maxPaymentAttempts = 3;

export function paymentWithAuthorization(cart: Cart, maxAttempts = maxPaymentAttempts): Payment {
  const payment = new Payment(cart, paymentRepository, maxAttempts);
  payment.paymentIframe = new PaymentIframe(stubAuth.html, stubAuth.transactionId);
  return payment;
}
