/**
 * Epic: Get Order Review
 * Orders: 0.0.3
 */

import { background, scenario, story } from "../story-test.js";
import { seedCustomerCart, loadCart, stubBundle, customerWithCart, reloadCart, enteredChosenAvailableNumber, essentials, dataFreedom } from "./examples";

/**
 * Story: Check The Order
 */

story('Check The Order', () => {
  // typescript body to translate:
  // checkOrderOutlines.forEach(({ example, opts, expectedMsisdn, expectedPortNumber }) => {
  // });
  scenario('Check the order: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: seedCustomerCart, loadCart, stubBundle
    given('the Customer has completed account setup, number, SIM, and profile', () => {
      // typescript body to translate:
      // seedCustomerCart('cus_1', opts);
      // TODO: implement step
    });
    when('My Paradise loads the order state from the Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await loadCart('cus_1');
      // TODO: implement step
    });
    then('the Customer is forwarded to Checkout', () => {
      // typescript body to translate:
      // expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
      // TODO: implement step
    })
      .and('the order summary shows the plan', () => {
        // typescript body to translate:
        // expect(cart.bundle?.plan).toBe(stubBundle.plan);
        // expect(cart.bundle?.name).toBe(stubBundle.name);
        // expect(cart.bundle?.price).toBe(stubBundle.price);
        // TODO: implement step
      })
      .and('the order summary shows the number and SIM', () => {
        // typescript body to translate:
        // expect(cart.line?.msisdn).toBe(expectedMsisdn);
        // expect(cart.line?.simType).toBe('eSIM');
        // if (expectedPortNumber) {
        //   expect(cart.line?.portability?.portNumber).toBe(expectedPortNumber);
        //   expect(cart.line?.portability?.verified).toBe(true);
        // }
        // TODO: implement step
      })
      .and('the order summary shows the profile', () => {
        // typescript body to translate:
        // expect(cart.customer.identity.idNumber).toBe('ID12345');
        // TODO: implement step
      });
  });
});

/**
 * Story: Upgrade To Data Freedom
 */

story('Upgrade To Data Freedom', () => {
  // typescript body to translate:
  // let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;
  //
  // beforeEach(() => {
  //   patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
  // });
  //
  // upgradeOutlines.forEach(({ example, currentPlan, newPlan }) => {
  // });
  scenario('Upgrade plan from review: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: customerWithCart, reloadCart
    given('${currentPlan.name} is in the Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', { bundleId: currentPlan.id });
      // TODO: implement step
    });
    when('My Paradise patches the Mavenir shopping cart with ${newPlan.name}', () => {
      // typescript body to translate:
      // cart.bundle = newPlan;
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with ${newPlan.name} bundleId', () => {
      // typescript body to translate:
      // expect(patchCartWithPlanSpy).toHaveBeenCalledWith(
      //   expect.any(String),
      //   newPlan.id,
      // );
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with ${newPlan.name}', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores ${newPlan.name} as the cart bundle', () => {
      // typescript body to translate:
      // expect(cart.bundle?.plan).toBe(newPlan);
      // TODO: implement step
    });
  });
});

/**
 * Story: Change Plan From Review
 */

story('Change Plan From Review', () => {
  // typescript body to translate:
  // let patchCartWithPlanSpy: MockInstance<typeof shoppingCartGateway.patchCartWithPlan>;
  //
  // beforeEach(() => {
  //   patchCartWithPlanSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithPlan');
  // });
  scenario('Select a different plan from review', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: customerWithCart, reloadCart, enteredChosenAvailableNumber, essentials, dataFreedom
    given('the Customer has opened plan selection from review with Essentials in the cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', {
      //   bundleId: essentials.id,
      //   msisdn: enteredChosenAvailableNumber,
      //   simType: 'eSIM',
      //   idNumber: 'ID12345',
      // });
      // TODO: implement step
    });
    when('My Paradise patches the Mavenir shopping cart with Data Freedom', () => {
      // typescript body to translate:
      // cart.bundle = dataFreedom;
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId', () => {
      // typescript body to translate:
      // expect(patchCartWithPlanSpy).toHaveBeenCalledWith(
      //   expect.any(String),
      //   dataFreedom.id,
      // );
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with Data Freedom', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores Data Freedom as the cart bundle loaded from the gateway', () => {
      // typescript body to translate:
      // expect(cart.bundle?.plan).toBe(dataFreedom);
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
        // TODO: implement step
      });
  });

  scenario('Keep current plan from review', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: customerWithCart, enteredChosenAvailableNumber, essentials
    given('the Customer has opened plan selection from review with Essentials in the cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', {
      //   bundleId: essentials.id,
      //   msisdn: enteredChosenAvailableNumber,
      //   simType: 'eSIM',
      //   idNumber: 'ID12345',
      // });
      // TODO: implement step
    });
    when('the Customer keeps their current plan', () => {
      // TODO: implement step
    });
    then('the cart bundle remains Essentials', () => {
      // typescript body to translate:
      // expect(cart.bundle?.plan).toBe(essentials);
      // TODO: implement step
    })
      .and('the Customer is forwarded to Checkout', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.Checkout);
        // TODO: implement step
      });
  });

  scenario('Plan update fails from review', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Error | undefined;
    // examples: customerWithCart, reloadCart, essentials, dataFreedom
    given('the Customer has opened plan selection from review with Essentials in the cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', { bundleId: essentials.id });
      // shoppingCartGateway.seedPatchCartWithPlanError(new Error('Failed to update new plan choice.'));
      // TODO: implement step
    });
    when('My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error', () => {
      // typescript body to translate:
      // try { cart.bundle = dataFreedom; } catch (e) { result = e as Error; }
      // TODO: implement step
    });
    then('My Paradise shows Failed to update new plan choice.', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the cart bundle remains Essentials', () => {
      // typescript body to translate:
      // expect(cart.bundle?.plan).toBe(essentials);
      // TODO: implement step
    });
  });
});
