import { Billing } from '../../../../domain/billing/Billing';
import type { Cart } from '../../../../domain/cart/Cart';
import { portalGateway } from '../../../../domain/systems/mavenir/portal-gateway';
import { WaitingPsim } from '../../../../domain/systems/mavenir/portal-gateway';
import { SimType } from '../../../../domain/subscription/Subscription';
import {
  customerWithCart,
  stubBundle,
  type CartOpts,
} from '../../get-number/examples/cart.examples';
import { enteredChosenAvailableNumber } from '../../get-number/examples/available-number.examples';

export async function customerReadyToChooseSim(opts?: CartOpts): Promise<Cart> {
  return customerWithCart('cus_1', {
    bundleId: stubBundle.id,
    msisdn: enteredChosenAvailableNumber,
    ...opts,
  });
}

export async function customerWaitingForPsim(opts?: CartOpts): Promise<Cart> {
  const cart = await customerWithCart('cus_1', {
    bundleId: stubBundle.id,
    msisdn: enteredChosenAvailableNumber,
    simType: SimType.Psim,
    idNumber: 'ID12345',
    ...opts,
  });
  cart.customer.billing = new Billing('bill_1');
  const mavenirCustomer = portalGateway.read(cart.customer.id);
  if (!(mavenirCustomer instanceof Error)) {
    mavenirCustomer.waitingPsim = WaitingPsim.Active;
  }
  return cart;
}
