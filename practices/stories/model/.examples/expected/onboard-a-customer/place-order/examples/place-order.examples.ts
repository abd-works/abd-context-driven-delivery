import { Billing } from '../../../../domain/billing/Billing';
import { Voucher } from '../../../../domain/cart/Voucher';
import { type Cart, OrderResult } from '../../../../domain/cart/Cart';
import { SimType } from '../../../../domain/subscription/Subscription';
import { portalGateway } from '../../../../domain/systems/mavenir/portal-gateway';
import {
  BillingAccountState,
  BillingCommunicationMedium,
  BillingCycle,
  BillingRatingType,
  BillingTemplate,
  CreditServiceProviderId,
} from '../../../../domain/systems/mavenir/billing';
import { ZendeskSubject } from '../../../../domain/systems/zendesk';
import { customerWithCart, stubBundle } from '../../get-number/examples/cart.examples';
import { enteredChosenAvailableNumber } from '../../get-number/examples/available-number.examples';
import { enteredValidPortability } from '../../get-number/examples/portability.examples';
import { atlas } from '../../get-order-review/examples/plan-upgrade.examples';

export const billingAccountId = 'bill_cus_1';
export const existingIccid = '89014103211118510720';
export const requesterName = 'Jane Customer';

export const trialVoucher = new Voucher(
  'TRIAL7',
  'trial',
  false,
  false,
  { trial: true, trialDays: 7 },
  {},
);

export interface PlaceOrderSeed {
  verified?: boolean;
  billing?: boolean;
  done?: boolean;
  simType?: string;
  iccid?: string;
  bundleId?: string;
  voucher?: Voucher;
  bypassVerified?: boolean;
  portability?: boolean;
  portabilityVerified?: boolean;
  payUpFront?: boolean | null;
  orderSuccess?: boolean | null;
}

export async function customerReadyToPlaceOrder(opts: PlaceOrderSeed = {}): Promise<Cart> {
  const withPort = opts.portability === true;
  const cart = await customerWithCart('cus_1', {
    bundleId: opts.bundleId ?? stubBundle.id,
    msisdn: enteredChosenAvailableNumber,
    simType: opts.simType ?? SimType.Esim,
    iccid: opts.iccid,
    idNumber: 'ID12345',
    givenName: 'Jane',
    familyName: 'Customer',
    validated: opts.verified ?? true,
    ...(withPort ? {
      portNumber: enteredValidPortability.portNumber,
      donorOperator: enteredValidPortability.donorOperator,
      accountNumber: enteredValidPortability.accountNumber,
      userType: enteredValidPortability.userType,
      accountType: enteredValidPortability.accountType,
      device: enteredValidPortability.device,
      portabilityVerified: opts.portabilityVerified ?? false,
    } : {}),
  });
  if (opts.billing !== false) {
    portalGateway.seedBilling(cart.customer.id, billingAccountId);
    cart.customer.billing = new Billing(billingAccountId);
  }
  cart.customer.verified = opts.verified ?? true;
  cart.customer.identity.fullName = requesterName;
  if (opts.done) {
    portalGateway.seedDone(cart.customer.id);
    cart.customer.done = true;
  }
  if (opts.voucher) cart.voucher = opts.voucher;
  if (opts.bypassVerified && cart.bundle) cart.bundle.plan.bypassVerified = true;
  if (opts.orderSuccess !== undefined) cart.orderSuccess = opts.orderSuccess;
  if (opts.payUpFront !== undefined) cart.payUpFront = opts.payUpFront;
  if (opts.orderSuccess !== undefined || opts.payUpFront !== undefined) {
    portalGateway.storeOrderResult(
      cart.customer.id,
      opts.orderSuccess ?? null,
      opts.payUpFront ?? null,
      opts.verified ?? true,
    );
    cart.defaultPayment = true;
  }
  return cart;
}

export function expectedBillingAccountRequest(customerId: string) {
  return {
    customerId,
    name: '',
    state: BillingAccountState.Active,
    ratingType: BillingRatingType.Postpaid,
    billCycle: BillingCycle.FirstOfMonth,
    billingTemplate: BillingTemplate.Summary,
    communicationMedium: BillingCommunicationMedium.Email,
  };
}

export function expectedProductOrderRequest(customerId: string) {
  return {
    customerId,
    serviceProviderId: CreditServiceProviderId.Paradise,
  };
}

export function expectedTicketRequest(customer: { identity: { fullName: string; email: string } }, subject: ZendeskSubject) {
  return {
    ticket: {
      requester: {
        name: customer.identity.fullName,
        email: customer.identity.email,
      },
      subject,
    },
  };
}

export const roamingPlan = atlas;

export const ticketOutlines = [
  {
    example: 'unverified eSIM',
    seed: { verified: false, simType: SimType.Esim } as PlaceOrderSeed,
    subject: ZendeskSubject.Id,
  },
  {
    example: 'verified pSIM without ICCID',
    seed: { verified: true, simType: SimType.Psim } as PlaceOrderSeed,
    subject: ZendeskSubject.PSim,
  },
  {
    example: 'unverified pSIM without ICCID',
    seed: { verified: false, simType: SimType.Psim } as PlaceOrderSeed,
    subject: ZendeskSubject.IdAndPSim,
  },
  {
    example: 'trial voucher',
    seed: { verified: true, voucher: trialVoucher } as PlaceOrderSeed,
    subject: ZendeskSubject.Trial,
  },
  {
    example: 'unverified portability',
    seed: { verified: true, portability: true, portabilityVerified: false } as PlaceOrderSeed,
    subject: ZendeskSubject.Portability,
  },
  {
    example: 'pay-up-front charge failed',
    seed: { verified: true, payUpFront: false } as PlaceOrderSeed,
    subject: ZendeskSubject.PayUpFrontFailed,
  },
  {
    example: 'roaming plan',
    seed: { verified: true, bundleId: roamingPlan.id } as PlaceOrderSeed,
    subject: ZendeskSubject.RoamingNewSubscription,
  },
];

export const orderResultOutlines = [
  {
    example: 'verified eSIM',
    seed: { verified: true, simType: SimType.Esim } as PlaceOrderSeed,
    orderSuccess: true,
    payUpFront: true as boolean | null,
    result: OrderResult.AllSet,
  },
  {
    example: 'verified pSIM with ICCID',
    seed: { verified: true, simType: SimType.Psim, iccid: existingIccid } as PlaceOrderSeed,
    orderSuccess: true,
    payUpFront: true as boolean | null,
    result: OrderResult.AllSet,
  },
  {
    example: 'unverified',
    seed: { verified: false, simType: SimType.Esim } as PlaceOrderSeed,
    orderSuccess: true,
    payUpFront: true as boolean | null,
    result: OrderResult.AlmostThere,
  },
  {
    example: 'verified pSIM without ICCID',
    seed: { verified: true, simType: SimType.Psim } as PlaceOrderSeed,
    orderSuccess: true,
    payUpFront: true as boolean | null,
    result: OrderResult.AlmostThere,
  },
  {
    example: 'pay-up-front failed',
    seed: { verified: true, simType: SimType.Esim } as PlaceOrderSeed,
    orderSuccess: true,
    payUpFront: false as boolean | null,
    result: OrderResult.AlmostThere,
  },
  {
    example: 'order failed',
    seed: { verified: true, simType: SimType.Esim } as PlaceOrderSeed,
    orderSuccess: false,
    payUpFront: null as boolean | null,
    result: OrderResult.AlmostThere,
  },
];
