import type { Cart } from '../../../../domain/cart/Cart';
import { portalGateway } from '../../../../domain/systems/mavenir/portal-gateway';
import {
  loadCart,
  seedCustomerCart,
} from '../../get-number/examples/cart.examples';

export const billingAccountId = '200000005678';

export async function cartWithBilling(bundleId: string): Promise<Cart> {
  seedCustomerCart('cus_1', { bundleId });
  portalGateway.seedBilling('cus_1', billingAccountId);
  return loadCart('cus_1');
}
