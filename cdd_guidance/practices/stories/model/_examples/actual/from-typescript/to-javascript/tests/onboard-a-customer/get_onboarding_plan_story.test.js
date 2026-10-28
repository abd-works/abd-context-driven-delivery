/**
 * Epic: Get Onboarding Plan
 * Orders: 0.0.2
 */

import { background, scenario, story } from "../story-test.js";
import { internalTestPlan, purchasablePlansExamples, essentials, customerWithCart, reloadCart } from "./examples";

/**
 * Story: Load Plan Catalog
 */

story('Load Plan Catalog', () => {
  scenario('Load plan catalog', ({ given, when, then }) => {
    // typescript body to translate:
    // let plans: Plan[];
    // examples: internalTestPlan, purchasablePlansExamples
    given('the plan catalog is available', async () => {
      // typescript body to translate:
      // await planRepository.seed([...purchasablePlansExamples, internalTestPlan]);
      // TODO: implement step
    });
    when('My Paradise loads the plan catalog', async () => {
      // typescript body to translate:
      // plans = await planRepository.list();
      // TODO: implement step
    });
    then('the catalog includes Essentials, Data Freedom, Ace, and Atlas', () => {
      // typescript body to translate:
      // expect(plans.map(p => p.name)).toEqual(
      //   expect.arrayContaining(['Essentials', 'Data Freedom', 'Ace', 'Atlas']),
      // );
      // TODO: implement step
    })
      .and('Internal Test Plan PROMO is excluded from the catalog', () => {
        // typescript body to translate:
        // expect(plans.every(p => p.isSellable)).toBe(true);
        // TODO: implement step
      });
  });
});

/**
 * Story: Choose Onboarding Plan
 */

story('Choose Onboarding Plan', () => {
  // typescript body to translate:
  // let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;
  //
  // beforeEach(() => {
  //   patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
  // });
  scenario('Select a plan', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: essentials, customerWithCart, reloadCart
    given('no plan is in the Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart();
      // TODO: implement step
    });
    when('the Customer selects Essentials', () => {
      // typescript body to translate:
      // cart.bundle = essentials;
      // TODO: implement step
    });
    then('My Paradise patches the Mavenir cart with the Essentials planId', () => {
      // typescript body to translate:
      // expect(patchCartWithPlanSpy).toHaveBeenCalledWith('cart_cus_1', essentials.id);
      // TODO: implement step
    })
      .and('the Customer is forwarded to Pick Number', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.PickNumber);
        // TODO: implement step
      });
    when('Mavenir confirms the cart is patched with Essentials', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the cart bundle is a snapshot of Essentials loaded from the gateway', () => {
      // typescript body to translate:
      // expect(cart.bundle?.id).toBe(essentials.id);
      // expect(cart.bundle?.name).toBe(essentials.name);
      // expect(cart.bundle?.description).toBe(essentials.name);
      // expect(cart.bundle?.price).toBe(essentials.price);
      // expect(cart.bundle?.fees).toBe(0);
      // expect(cart.bundle?.totalPrice).toBe(essentials.price);
      // expect(cart.bundle?.features).toEqual([]);
      // expect(cart.bundle?.plan).toBe(essentials);
      // TODO: implement step
    });
  });

  scenario('Change an existing plan', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: essentials, customerWithCart, reloadCart
    given('Essentials is in the Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', { bundleId: essentials.id });
      // TODO: implement step
    });
    when('the Customer selects Data Freedom', () => {
      // typescript body to translate:
      // cart.bundle = dataFreedom;
      // TODO: implement step
    });
    then('My Paradise patches the Mavenir cart with the Data Freedom planId', () => {
      // typescript body to translate:
      // expect(patchCartWithPlanSpy).toHaveBeenCalledWith('cart_cus_1', dataFreedom.id);
      // TODO: implement step
    });
    when('Mavenir confirms the cart is patched with Data Freedom', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway', () => {
      // typescript body to translate:
      // expect(cart.bundle?.id).toBe(dataFreedom.id);
      // expect(cart.bundle?.name).toBe(dataFreedom.name);
      // expect(cart.bundle?.description).toBe(dataFreedom.name);
      // expect(cart.bundle?.price).toBe(dataFreedom.price);
      // expect(cart.bundle?.fees).toBe(0);
      // expect(cart.bundle?.totalPrice).toBe(dataFreedom.price);
      // expect(cart.bundle?.features).toEqual([]);
      // expect(cart.bundle?.plan).toBe(dataFreedom);
      // TODO: implement step
    });
  });

  scenario('Failed to update plan', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Error | undefined;
    // examples: essentials, customerWithCart, reloadCart
    given('the Mavenir cart patch returns an error', async () => {
      // typescript body to translate:
      // cart = await customerWithCart();
      // shoppingCartGateway.seedPatchCartWithPlanError(new Error('Mavenir unavailable'));
      // TODO: implement step
    });
    when('the Customer selects Essentials', () => {
      // typescript body to translate:
      // try { cart.bundle = essentials; } catch (e) { result = e as Error; }
      // TODO: implement step
    });
    then('the plan selection fails', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the cart bundle remains empty', () => {
      // typescript body to translate:
      // expect(cart.bundle).toBeNull();
      // TODO: implement step
    });
  });
});
