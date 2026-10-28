from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import internalTestPlan, purchasablePlansExamples, essentials, customerWithCart, reloadCart


# Epic: Get Onboarding Plan
# Orders: 0.0.2

# Story: Load Plan Catalog
with story("Load Plan Catalog"):
        with scenario("Load plan catalog"):
            # typescript body to translate:
            # let plans: Plan[];
            # examples: internalTestPlan, purchasablePlansExamples
            with given("the plan catalog is available"):
                # typescript body to translate:
                # await planRepository.seed([...purchasablePlansExamples, internalTestPlan]);
                pass
            with when("My Paradise loads the plan catalog"):
                # typescript body to translate:
                # plans = await planRepository.list();
                pass
            with then("the catalog includes Essentials, Data Freedom, Ace, and Atlas"):
                # typescript body to translate:
                # expect(plans.map(p => p.name)).toEqual(
                #   expect.arrayContaining(['Essentials', 'Data Freedom', 'Ace', 'Atlas']),
                # );
                pass
            with and_("Internal Test Plan PROMO is excluded from the catalog"):
                # typescript body to translate:
                # expect(plans.every(p => p.isSellable)).toBe(true);
                pass

# Story: Choose Onboarding Plan
with story("Choose Onboarding Plan"):
    # typescript body to translate:
    # let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;
    #
    # beforeEach(() => {
    #   patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
    # });
        with scenario("Select a plan"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: essentials, customerWithCart, reloadCart
            with given("no plan is in the Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await customerWithCart();
                pass
            with when("the Customer selects Essentials"):
                # typescript body to translate:
                # cart.bundle = essentials;
                pass
            with then("My Paradise patches the Mavenir cart with the Essentials planId"):
                # typescript body to translate:
                # expect(patchCartWithPlanSpy).toHaveBeenCalledWith('cart_cus_1', essentials.id);
                pass
            with and_("the Customer is forwarded to Pick Number"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.PickNumber);
                pass
            with when("Mavenir confirms the cart is patched with Essentials"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the cart bundle is a snapshot of Essentials loaded from the gateway"):
                # typescript body to translate:
                # expect(cart.bundle?.id).toBe(essentials.id);
                # expect(cart.bundle?.name).toBe(essentials.name);
                # expect(cart.bundle?.description).toBe(essentials.name);
                # expect(cart.bundle?.price).toBe(essentials.price);
                # expect(cart.bundle?.fees).toBe(0);
                # expect(cart.bundle?.totalPrice).toBe(essentials.price);
                # expect(cart.bundle?.features).toEqual([]);
                # expect(cart.bundle?.plan).toBe(essentials);
                pass
        with scenario("Change an existing plan"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: essentials, customerWithCart, reloadCart
            with given("Essentials is in the Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', { bundleId: essentials.id });
                pass
            with when("the Customer selects Data Freedom"):
                # typescript body to translate:
                # cart.bundle = dataFreedom;
                pass
            with then("My Paradise patches the Mavenir cart with the Data Freedom planId"):
                # typescript body to translate:
                # expect(patchCartWithPlanSpy).toHaveBeenCalledWith('cart_cus_1', dataFreedom.id);
                pass
            with when("Mavenir confirms the cart is patched with Data Freedom"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway"):
                # typescript body to translate:
                # expect(cart.bundle?.id).toBe(dataFreedom.id);
                # expect(cart.bundle?.name).toBe(dataFreedom.name);
                # expect(cart.bundle?.description).toBe(dataFreedom.name);
                # expect(cart.bundle?.price).toBe(dataFreedom.price);
                # expect(cart.bundle?.fees).toBe(0);
                # expect(cart.bundle?.totalPrice).toBe(dataFreedom.price);
                # expect(cart.bundle?.features).toEqual([]);
                # expect(cart.bundle?.plan).toBe(dataFreedom);
                pass
        with scenario("Failed to update plan"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Error | undefined;
            # examples: essentials, customerWithCart, reloadCart
            with given("the Mavenir cart patch returns an error"):
                # typescript body to translate:
                # cart = await customerWithCart();
                # shoppingCartGateway.seedPatchCartWithPlanError(new Error('Mavenir unavailable'));
                pass
            with when("the Customer selects Essentials"):
                # typescript body to translate:
                # try { cart.bundle = essentials; } catch (e) { result = e as Error; }
                pass
            with then("the plan selection fails"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                pass
            with when("My Paradise reloads the shopping cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the cart bundle remains empty"):
                # typescript body to translate:
                # expect(cart.bundle).toBeNull();
                pass
