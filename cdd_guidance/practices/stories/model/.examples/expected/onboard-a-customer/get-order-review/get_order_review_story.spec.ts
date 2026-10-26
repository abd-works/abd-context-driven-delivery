import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { type Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import {
  seedCustomerCart,
  loadCart,
  customerWithCart,
  reloadCart,
  stubBundle,
} from '../get-number/examples/cart.examples';
import { enteredChosenAvailableNumber } from '../get-number/examples/available-number.examples';
import { checkOrderOutlines } from './examples/check-order.examples';
import { essentials, dataFreedom, upgradeOutlines } from './examples/plan-upgrade.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Check The Order', () => {
  checkOrderOutlines.forEach(({ example, opts, expectedMsisdn, expectedPortNumber }) => {
    scenario(`Check the order: ${example}`, ({ given, when, then }) => {
      let cart: Cart;

      given('the Customer has completed account setup, number, SIM, and profile', () => {
        seedCustomerCart('cus_1', opts);
      });
      when('My Paradise loads the order state from the Mavenir shopping cart', async () => {
        cart = await loadCart('cus_1');
      });
      then('the Customer is forwarded to Checkout', () => {
        expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
      }).and('the order summary shows the plan', () => {
        expect(cart.bundle?.plan).toBe(stubBundle.plan);
        expect(cart.bundle?.name).toBe(stubBundle.name);
        expect(cart.bundle?.price).toBe(stubBundle.price);
      }).and('the order summary shows the number and SIM', () => {
        expect(cart.line?.msisdn).toBe(expectedMsisdn);
        expect(cart.line?.simType).toBe('eSIM');
        if (expectedPortNumber) {
          expect(cart.line?.portability?.portNumber).toBe(expectedPortNumber);
          expect(cart.line?.portability?.verified).toBe(true);
        }
      }).and('the order summary shows the profile', () => {
        expect(cart.customer.identity.idNumber).toBe('ID12345');
      });
    });
  });
});

// ---------------------------------------------------------------------------

story('Upgrade To Data Freedom', () => {
  let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;

  beforeEach(() => {
    patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
  });

  upgradeOutlines.forEach(({ example, currentPlan, newPlan }) => {
    scenario(`Upgrade plan from review: ${example}`, ({ given, when, then }) => {
      let cart: Cart;

      given(`${currentPlan.name} is in the Mavenir shopping cart`, async () => {
        cart = await customerWithCart('cus_1', { bundleId: currentPlan.id });
      });
      when(`My Paradise patches the Mavenir shopping cart with ${newPlan.name}`, () => {
        cart.bundle = newPlan;
      });
      then(`My Paradise sends the patch cart request to Mavenir with ${newPlan.name} bundleId`, () => {
        expect(patchCartWithPlanSpy).toHaveBeenCalledWith(
          expect.any(String),
          newPlan.id,
        );
      });
      when(`Mavenir returns the updated Mavenir shopping cart with ${newPlan.name}`, async () => {
        cart = await reloadCart(cart);
      });
      then(`My Paradise stores ${newPlan.name} as the cart bundle`, () => {
        expect(cart.bundle?.plan).toBe(newPlan);
      });
    });
  });
});

// ---------------------------------------------------------------------------

story('Change Plan From Review', () => {
  let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;

  beforeEach(() => {
    patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
  });

  scenario('Select a different plan from review', ({ given, when, then }) => {
    let cart: Cart;

    given('the Customer has opened plan selection from review with Essentials in the cart', async () => {
      cart = await customerWithCart('cus_1', {
        bundleId: essentials.id,
        msisdn: enteredChosenAvailableNumber,
        simType: 'eSIM',
        idNumber: 'ID12345',
      });
    });
    when('My Paradise patches the Mavenir shopping cart with Data Freedom', () => {
      cart.bundle = dataFreedom;
    });
    then('My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId', () => {
      expect(patchCartWithPlanSpy).toHaveBeenCalledWith(
        expect.any(String),
        dataFreedom.id,
      );
    });
    when('Mavenir returns the updated Mavenir shopping cart with Data Freedom', async () => {
      cart = await reloadCart(cart);
    });
    then('My Paradise stores Data Freedom as the cart bundle loaded from the gateway', () => {
      expect(cart.bundle?.plan).toBe(dataFreedom);
    }).and('the Customer is forwarded to Checkout', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
    });
  });

  scenario('Keep current plan from review', ({ given, when, then }) => {
    let cart: Cart;

    given('the Customer has opened plan selection from review with Essentials in the cart', async () => {
      cart = await customerWithCart('cus_1', {
        bundleId: essentials.id,
        msisdn: enteredChosenAvailableNumber,
        simType: 'eSIM',
        idNumber: 'ID12345',
      });
    });
    when('the Customer keeps their current plan', () => {});
    then('the cart bundle remains Essentials', () => {
      expect(cart.bundle?.plan).toBe(essentials);
    }).and('the Customer is forwarded to Checkout', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
    });
  });

  scenario('Plan update fails from review', ({ given, when, then }) => {
    let cart: Cart;
    let result: Error | undefined;

    given('the Customer has opened plan selection from review with Essentials in the cart', async () => {
      cart = await customerWithCart('cus_1', { bundleId: essentials.id });
      shoppingCartGateway.seedPatchCartWithPlanError(new Error('Failed to update new plan choice.'));
    });
    when('My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error', () => {
      try { cart.bundle = dataFreedom; } catch (e) { result = e as Error; }
    });
    then('My Paradise shows Failed to update new plan choice.', () => {
      expect(result).toBeInstanceOf(Error);
    });
    when('My Paradise reloads the shopping cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the cart bundle remains Essentials', () => {
      expect(cart.bundle?.plan).toBe(essentials);
    });
  });
});
