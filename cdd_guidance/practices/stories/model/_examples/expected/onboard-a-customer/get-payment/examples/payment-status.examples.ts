import { PaymentReason, PaymentResult } from '../../../../domain/billing/Payment';
import { FacTokenizedCard } from '../../../../domain/systems/mavenir/ccs-gateway';
import { stubAuth } from './payment-authorization.examples';

export const completedAuth = new FacTokenizedCard(
  'cus_1',
  stubAuth.transactionId,
  PaymentResult.Completed,
  PaymentReason.Approved,
);

export const failedAuth = new FacTokenizedCard(
  'cus_1',
  stubAuth.transactionId,
  PaymentResult.Failed,
  PaymentReason.Declined,
);
