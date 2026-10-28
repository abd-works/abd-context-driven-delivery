from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import seedCustomerCart, loadCart, stubBundle, customerWithCart, reloadCart, enteredChosenAvailableNumber, essentials, dataFreedom


# Epic: Get Order Review
# Orders: 0.0.3

# Story: Check The Order
with story("Check The Order"):
    # typescript body to translate:
    # checkOrderOutlines.forEach(({ example, opts, expectedMsisdn, expectedPortNumber }) => {
    # });
        with scenario("Check the order: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: seedCustomerCart, loadCart, stubBundle
            with given("the Customer has completed account setup, number, SIM, and profile"):
                # typescript body to translate:
                # seedCustomerCart('cus_1', opts);
                pass
            with when("My Paradise loads the order state from the Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await loadCart('cus_1');
                pass
            with then("the Customer is forwarded to Checkout"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
                pass
            with and_("the order summary shows the plan"):
                # typescript body to translate:
                # expect(cart.bundle?.plan).toBe(stubBundle.plan);
                # expect(cart.bundle?.name).toBe(stubBundle.name);
                # expect(cart.bundle?.price).toBe(stubBundle.price);
                pass
            with and_("the order summary shows the number and SIM"):
                # typescript body to translate:
                # expect(cart.line?.msisdn).toBe(expectedMsisdn);
                # expect(cart.line?.simType).toBe('eSIM');
                # if (expectedPortNumber) {
                #   expect(cart.line?.portability?.portNumber).toBe(expectedPortNumber);
                #   expect(cart.line?.portability?.verified).toBe(true);
                # }
                pass
            with and_("the order summary shows the profile"):
                # typescript body to translate:
                # expect(cart.customer.identity.idNumber).toBe('ID12345');
                pass

# Story: Upgrade To Data Freedom
with story("Upgrade To Data Freedom"):
    # typescript body to translate:
    # let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;
    #
    # beforeEach(() => {
    #   patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
    # });
    #
    # upgradeOutlines.forEach(({ example, currentPlan, newPlan }) => {
    # });
        with scenario("Upgrade plan from review: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: customerWithCart, reloadCart
            with given("${currentPlan.name} is in the Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', { bundleId: currentPlan.id });
                pass
            with when("My Paradise patches the Mavenir shopping cart with ${newPlan.name}"):
                # typescript body to translate:
                # cart.bundle = newPlan;
                pass
            with then("My Paradise sends the patch cart request to Mavenir with ${newPlan.name} bundleId"):
                # typescript body to translate:
                # expect(patchCartWithPlanSpy).toHaveBeenCalledWith(
                #   expect.any(String),
                #   newPlan.id,
                # );
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with ${newPlan.name}"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores ${newPlan.name} as the cart bundle"):
                # typescript body to translate:
                # expect(cart.bundle?.plan).toBe(newPlan);
                pass

# Story: Change Plan From Review
with story("Change Plan From Review"):
    # typescript body to translate:
    # let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;
    #
    # beforeEach(() => {
    #   patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
    # });
        with scenario("Select a different plan from review"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: customerWithCart, reloadCart, enteredChosenAvailableNumber, essentials, dataFreedom
            with given("the Customer has opened plan selection from review with Essentials in the cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', {
                #   bundleId: essentials.id,
                #   msisdn: enteredChosenAvailableNumber,
                #   simType: 'eSIM',
                #   idNumber: 'ID12345',
                # });
                pass
            with when("My Paradise patches the Mavenir shopping cart with Data Freedom"):
                # typescript body to translate:
                # cart.bundle = dataFreedom;
                pass
            with then("My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId"):
                # typescript body to translate:
                # expect(patchCartWithPlanSpy).toHaveBeenCalledWith(
                #   expect.any(String),
                #   dataFreedom.id,
                # );
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with Data Freedom"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores Data Freedom as the cart bundle loaded from the gateway"):
                # typescript body to translate:
                # expect(cart.bundle?.plan).toBe(dataFreedom);
                pass
            with and_("the Customer is forwarded to Checkout"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
                pass
        with scenario("Keep current plan from review"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: customerWithCart, enteredChosenAvailableNumber, essentials
            with given("the Customer has opened plan selection from review with Essentials in the cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', {
                #   bundleId: essentials.id,
                #   msisdn: enteredChosenAvailableNumber,
                #   simType: 'eSIM',
                #   idNumber: 'ID12345',
                # });
                pass
            with when("the Customer keeps their current plan"):
                pass
            with then("the cart bundle remains Essentials"):
                # typescript body to translate:
                # expect(cart.bundle?.plan).toBe(essentials);
                pass
            with and_("the Customer is forwarded to Checkout"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
                pass
        with scenario("Plan update fails from review"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Error | undefined;
            # examples: customerWithCart, reloadCart, essentials, dataFreedom
            with given("the Customer has opened plan selection from review with Essentials in the cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', { bundleId: essentials.id });
                # shoppingCartGateway.seedPatchCartWithPlanError(new Error('Failed to update new plan choice.'));
                pass
            with when("My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error"):
                # typescript body to translate:
                # try { cart.bundle = dataFreedom; } catch (e) { result = e as Error; }
                pass
            with then("My Paradise shows Failed to update new plan choice."):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                pass
            with when("My Paradise reloads the shopping cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the cart bundle remains Essentials"):
                # typescript body to translate:
                # expect(cart.bundle?.plan).toBe(essentials);
                pass
