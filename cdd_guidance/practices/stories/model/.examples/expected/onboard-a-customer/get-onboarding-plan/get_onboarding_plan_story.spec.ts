import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import type { Plan } from '../../../domain/plans/Plan';
import { planRepository } from '../../../domain/plans/PlanRepository';
import { type Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { essentials, internalTestPlan, purchasablePlansExamples } from '../examples/purchasable-plans.examples';
import { customerWithCart, reloadCart } from '../get-number/examples/cart.examples';
const dataFreedom = purchasablePlansExamples.find(p => p.name === 'Data Freedom')!;

afterEach(() => {
  shoppingCartGateway.reset();
  planRepository.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

// ─────────────────────────────────────────────────────────────────────────────

story('Load Plan Catalog', () => {
  scenario('Load plan catalog', ({ given, when, then }) => {
    let plans: Plan[];

    given('the plan catalog is available', async () => {
      await planRepository.seed([...purchasablePlansExamples, internalTestPlan]);
    });
    when('My Paradise loads the plan catalog', async () => {
      plans = await planRepository.list();
    });
    then('the catalog includes Essentials, Data Freedom, Ace, and Atlas', () => {
      expect(plans.map(p => p.name)).toEqual(
        expect.arrayContaining(['Essentials', 'Data Freedom', 'Ace', 'Atlas']),
      );
    }).and('Internal Test Plan PROMO is excluded from the catalog', () => {
      expect(plans.every(p => p.isSellable)).toBe(true);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────

story('Choose Onboarding Plan', () => {
  let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;

  beforeEach(() => {
    patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
  });

  scenario('Select a plan', ({ given, when, then }) => {
    let cart: Cart;

    given('no plan is in the Mavenir shopping cart', async () => {
      cart = await customerWithCart();
    });
    when('the Customer selects Essentials', () => {
      cart.bundle = essentials;
    });
    then('My Paradise patches the Mavenir cart with the Essentials planId', () => {
      expect(patchCartWithPlanSpy).toHaveBeenCalledWith('cart_cus_1', essentials.id);
    }).and('the Customer is forwarded to Pick Number', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.PickNumber);
    });
    when('Mavenir confirms the cart is patched with Essentials', async () => {
      cart = await reloadCart(cart);
    });
    then('the cart bundle is a snapshot of Essentials loaded from the gateway', () => {
      expect(cart.bundle?.id).toBe(essentials.id);
      expect(cart.bundle?.name).toBe(essentials.name);
      expect(cart.bundle?.description).toBe(essentials.name);
      expect(cart.bundle?.price).toBe(essentials.price);
      expect(cart.bundle?.fees).toBe(0);
      expect(cart.bundle?.totalPrice).toBe(essentials.price);
      expect(cart.bundle?.features).toEqual([]);
      expect(cart.bundle?.plan).toBe(essentials);
    });
  });

  scenario('Change an existing plan', ({ given, when, then }) => {
    let cart: Cart;

    given('Essentials is in the Mavenir shopping cart', async () => {
      cart = await customerWithCart('cus_1', { bundleId: essentials.id });
    });
    when('the Customer selects Data Freedom', () => {
      cart.bundle = dataFreedom;
    });
    then('My Paradise patches the Mavenir cart with the Data Freedom planId', () => {
      expect(patchCartWithPlanSpy).toHaveBeenCalledWith('cart_cus_1', dataFreedom.id);
    });
    when('Mavenir confirms the cart is patched with Data Freedom', async () => {
      cart = await reloadCart(cart);
    });
    then('the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway', () => {
      expect(cart.bundle?.id).toBe(dataFreedom.id);
      expect(cart.bundle?.name).toBe(dataFreedom.name);
      expect(cart.bundle?.description).toBe(dataFreedom.name);
      expect(cart.bundle?.price).toBe(dataFreedom.price);
      expect(cart.bundle?.fees).toBe(0);
      expect(cart.bundle?.totalPrice).toBe(dataFreedom.price);
      expect(cart.bundle?.features).toEqual([]);
      expect(cart.bundle?.plan).toBe(dataFreedom);
    });
  });

  scenario('Failed to update plan', ({ given, when, then }) => {
    let cart: Cart;
    let result: Error | undefined;

    given('the Mavenir cart patch returns an error', async () => {
      cart = await customerWithCart();
      shoppingCartGateway.seedPatchCartWithPlanError(new Error('Mavenir unavailable'));
    });
    when('the Customer selects Essentials', () => {
      try { cart.bundle = essentials; } catch (e) { result = e as Error; }
    });
    then('the plan selection fails', () => {
      expect(result).toBeInstanceOf(Error);
    });
    when('My Paradise reloads the shopping cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the cart bundle remains empty', () => {
      expect(cart.bundle).toBeNull();
    });
  });
});
