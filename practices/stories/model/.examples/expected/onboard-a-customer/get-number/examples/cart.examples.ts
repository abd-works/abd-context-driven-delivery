import {
  Bundle,
  Cart,
  CartRepository,
} from '../../../../domain/cart/Cart';
import type { SimType } from '../../../../domain/subscription/Subscription';
import { shoppingCartGateway } from '../../../../domain/systems/mavenir/shopping-cart-gateway';
import { Plan } from '../../../../domain/plans/Plan';
import { portabilityRepository, type DonorOperator, type UserType, type AccountType, type Device } from '../../../../domain/number/Portability';
import { customerRepository } from '../../../../domain/customer/Customer';
import { portalGateway } from '../../../../domain/systems/mavenir/portal-gateway';
import { purchasablePlansExamples } from '../../examples/purchasable-plans.examples';
import { storedAccountCredentialsWithToken } from '../../examples/account-credentials.examples';
import { storedHeldAvailableNumber } from './available-number.examples';
import { enteredValidPortability } from './portability.examples';

const stubPlan = new Plan('plan_1', 'Standard', 'Standard', 0, 0, 0, [], true, null, false);
export const stubBundle = Bundle.fromPlan(stubPlan);

const allKnownPlans = [...purchasablePlansExamples, stubPlan];

const cartRepository = new CartRepository(shoppingCartGateway);

export interface CartOpts {
  bundleId?: string;
  msisdn?: string;
  simType?: SimType;
  iccid?: string;
  idNumber?: string;
  givenName?: string;
  familyName?: string;
  validated?: boolean;
  portNumber?: string;
  donorOperator?: DonorOperator;
  accountNumber?: string;
  userType?: UserType;
  accountType?: AccountType;
  device?: Device;
  portabilityVerified?: boolean;
}

/** Seed both gateways (portal + shopping cart) without loading. */
export function seedCustomerCart(customerId = 'cus_1', opts?: CartOpts): void {
  const accountCredentials = storedAccountCredentialsWithToken(customerId);
  portalGateway.seedCustomerById(customerId, accountCredentials.email ?? '', {
    idNumber: opts?.idNumber,
    givenName: opts?.givenName,
    familyName: opts?.familyName,
    validated: opts?.validated,
  });
  shoppingCartGateway.seedCart(customerId, `cart_${customerId}`, {
    bundleId: opts?.bundleId,
    msisdn: opts?.msisdn,
    simType: opts?.simType,
    iccid: opts?.iccid,
    portNumber: opts?.portNumber,
    donorOperator: opts?.donorOperator,
    accountNumber: opts?.accountNumber,
    userType: opts?.userType,
    accountType: opts?.accountType,
    device: opts?.device,
    portabilityVerified: opts?.portabilityVerified,
  });
}

/** Load the cart through the full repository chain (customerRepository + cartRepository). */
export async function loadCart(customerId = 'cus_1'): Promise<Cart> {
  const accountCredentials = storedAccountCredentialsWithToken(customerId);
  const customer = await customerRepository.load(accountCredentials);
  const cart = cartRepository.load(customer)!;
  const plan = cart.bundleId ? allKnownPlans.find((p) => p.id === cart.bundleId) : undefined;
  if (plan) cart.bundle = Bundle.fromPlan(plan);
  cartRepository.loadOrderResult(cart);
  portabilityRepository.load(cart);
  return cart;
}

/** Seed gateways then load. Convenience helper for specs that don't need the separation. */
export async function customerWithCart(customerId = 'cus_1', opts?: CartOpts): Promise<Cart> {
  seedCustomerCart(customerId, opts);
  return loadCart(customerId);
}

/** Reload cart (and customer billing/done/order flags) from the gateways after a system call. */
export async function reloadCart(cart: Cart): Promise<Cart> {
  return loadCart(cart.customer.id);
}

export async function customerWithCartAndPortability(customerId = 'cus_1'): Promise<Cart> {
  return customerWithCart(customerId, {
    bundleId: stubPlan.id,
    msisdn: storedHeldAvailableNumber,
    portNumber: enteredValidPortability.portNumber,
    donorOperator: enteredValidPortability.donorOperator,
    accountNumber: enteredValidPortability.accountNumber,
    userType: enteredValidPortability.userType,
    accountType: enteredValidPortability.accountType,
    device: enteredValidPortability.device,
  });
}
