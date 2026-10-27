/**
 * ++Mavenir shopping cart++ examples for Create Empty Cart.
 *
 * Created empty (no items) at the start of onboarding.
 * The id comes from the Mavenir shoppingCart POST response.
 *
 * Source: stories/onboard-a-customer/create-empty-cart/story-scenarios.md
 */

import { MavenirShoppingCart, MavenirCreateCartRequest } from '../../../../domain/systems/mavenir/shopping-cart-gateway';

export const newMavenirShoppingCart = new MavenirShoppingCart('cart_1');

export function newMavenirShoppingCartId(): string {
  return newMavenirShoppingCart.id;
}

export function onboardingCreateCartRequest(customerId: string): MavenirCreateCartRequest {
  return MavenirCreateCartRequest.onboarding(customerId);
}
