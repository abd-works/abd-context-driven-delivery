import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { type Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { SimType } from '../../../domain/subscription/Subscription';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { mavenirMsisdnGateway } from '../../../domain/systems/mavenir/msisdn-gateway';
import { WaitingPsim } from '../../../domain/systems/mavenir/portal-gateway';
import { reloadCart } from '../get-number/examples/cart.examples';
import { enteredValidIccid, expectedValidIccid, enteredIccidWithSpaces, enteredInvalidIccid } from './examples/iccid.examples';
import { customerReadyToChooseSim, customerWaitingForPsim } from './examples/sim-cart.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  mavenirMsisdnGateway.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Choose Esim', () => {
  let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;

  beforeEach(() => {
    patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  });

  scenario('Choose eSIM', ({ given, when, then }) => {
    let cart: Cart;

    given('no SIM type is on the line', async () => {
      cart = await customerReadyToChooseSim();
    });
    when('the Customer selects eSIM', () => {
      cart.line!.selectSim(SimType.Esim);
    });
    then('My Paradise sends the patch cart request to Mavenir with SIM type eSIM', () => {
      expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Esim);
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type eSIM', async () => {
      cart = await reloadCart(cart);
    });
    then('My Paradise stores eSIM on the line', () => {
      expect(cart.line?.simType).toBe(SimType.Esim);
    }).but('the line has no ICCID', () => {
      expect(cart.line?.iccid).toBeNull();
    }).and('the Customer is forwarded to Verify ID', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
    });
  });

  scenario('Choose eSIM — already on the line', ({ given, when, then }) => {
    let cart: Cart;

    given('the line already has SIM type eSIM', async () => {
      cart = await customerReadyToChooseSim({ simType: SimType.Esim });
    });
    when('the Customer selects eSIM', () => {
      cart.line!.selectSim(SimType.Esim);
    });
    then('My Paradise skips the cart patch', () => {
      expect(patchCartWithSimSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Choose eSIM — cart patch fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: void | Error;

    given('Mavenir returns an error on cart patch', async () => {
      cart = await customerReadyToChooseSim();
      shoppingCartGateway.seedPatchCartWithSimError(new Error('Failed to select your sim'));
    });
    when('the Customer selects eSIM', () => {
      result = cart.line!.selectSim(SimType.Esim);
    });
    then('the SIM selection fails', () => {
      expect(result).toBeInstanceOf(Error);
    });
    when('My Paradise reloads the shopping cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the line has no SIM type', () => {
      expect(cart.line?.simType).toBeNull();
    }).and('the line has no ICCID', () => {
      expect(cart.line?.iccid).toBeNull();
    });
  });
});

// ---------------------------------------------------------------------------

story('Request a Paradise Sim Card', () => {
  let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;

  beforeEach(() => {
    patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  });

  scenario('Request a Paradise SIM card', ({ given, when, then }) => {
    let cart: Cart;

    given('no SIM type is on the line and no ICCID is on the line', async () => {
      cart = await customerReadyToChooseSim();
    });
    when('the Customer requests a Paradise SIM card', () => {
      cart.line!.selectSim(SimType.Psim);
    });
    then('My Paradise sends the patch cart request to Mavenir with SIM type pSIM', () => {
      expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim);
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM', async () => {
      cart = await reloadCart(cart);
    });
    then('My Paradise stores pSIM on the line', () => {
      expect(cart.line?.simType).toBe(SimType.Psim);
    }).but('the line has no ICCID', () => {
      expect(cart.line?.iccid).toBeNull();
    }).and('the Customer is forwarded to Verify ID', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
    });
  });

  scenario('Request a Paradise SIM card — already on the line', ({ given, when, then }) => {
    let cart: Cart;

    given('the line already has SIM type pSIM', async () => {
      cart = await customerReadyToChooseSim({ simType: SimType.Psim });
    });
    when('the Customer requests a Paradise SIM card', () => {
      cart.line!.selectSim(SimType.Psim);
    });
    then('My Paradise skips the cart patch', () => {
      expect(patchCartWithSimSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Request a Paradise SIM card — cart patch fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: void | Error;

    given('Mavenir returns an error on cart patch', async () => {
      cart = await customerReadyToChooseSim();
      shoppingCartGateway.seedPatchCartWithSimError(new Error('Failed to select your sim'));
    });
    when('the Customer requests a Paradise SIM card', () => {
      result = cart.line!.selectSim(SimType.Psim);
    });
    then('the SIM selection fails', () => {
      expect(result).toBeInstanceOf(Error);
    });
    when('My Paradise reloads the shopping cart', async () => {
      cart = await reloadCart(cart);
    });
    then('the line has no SIM type', () => {
      expect(cart.line?.simType).toBeNull();
    }).and('the line has no ICCID', () => {
      expect(cart.line?.iccid).toBeNull();
    });
  });
});

// ---------------------------------------------------------------------------

story('Enter Existing Sim', () => {
  let validateIccidSpy: MockInstance<typeof mavenirMsisdnGateway.validateIccid>;
  let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;

  beforeEach(() => {
    validateIccidSpy = vi.spyOn(mavenirMsisdnGateway, 'validateIccid');
    patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  });

  scenario('Enter existing SIM', ({ given, when, then }) => {
    let cart: Cart;

    given('Mavenir has valid ICCID available in inventory', async () => {
      mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      cart = await customerReadyToChooseSim();
    });
    when('the Customer attaches valid ICCID', () => {
      cart.line!.attachIccid(enteredValidIccid);
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {
      expect(validateIccidSpy).toHaveBeenCalledWith(enteredValidIccid);
    }).and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {
      expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim, enteredValidIccid);
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID', async () => {
      cart = await reloadCart(cart);
    });
    then('My Paradise stores pSIM and valid ICCID on the line', () => {
      expect(cart.line?.simType).toBe(SimType.Psim);
    }).and('the line has valid ICCID', () => {
      expect(cart.line?.iccid).toBe(expectedValidIccid);
    }).and('the Customer is forwarded to Verify ID', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
    });
  });

  scenario('ICCID contains spaces', ({ given, when, then }) => {
    let cart: Cart;
    let result: void | Error;

    given('the Customer has ICCID with spaces', async () => {
      cart = await customerReadyToChooseSim();
    });
    when('the Customer attaches ICCID with spaces', () => {
      try { cart.line!.attachIccid(enteredIccidWithSpaces); } catch (e) { result = e as Error; }
    });
    then('the ICCID format is rejected', () => {
      expect(result).toBeInstanceOf(Error);
      expect((result as Error).message).toBe('Please enter a valid iccid');
    }).and('My Paradise does not query inventory or patch the cart', () => {
      expect(validateIccidSpy).not.toHaveBeenCalled();
      expect(patchCartWithSimSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Inventory rejects ICCID', ({ given, when, then }) => {
    let cart: Cart;
    let result: void | Error;

    given('Mavenir does not have invalid ICCID available in inventory', async () => {
      cart = await customerReadyToChooseSim();
    });
    when('the Customer attaches invalid ICCID', () => {
      try { cart.line!.attachIccid(enteredInvalidIccid); } catch (e) { result = e as Error; }
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID', () => {
      expect(validateIccidSpy).toHaveBeenCalledWith(enteredInvalidIccid);
    }).and('My Paradise does not patch the cart', () => {
      expect(patchCartWithSimSpy).not.toHaveBeenCalled();
    }).and('the ICCID is rejected', () => {
      expect(result).toBeInstanceOf(Error);
      expect((result as Error).message).toBe('Invalid ICCID.');
    });
  });
});

// ---------------------------------------------------------------------------

story('Activate Sim', () => {
  let validateIccidSpy: MockInstance<typeof mavenirMsisdnGateway.validateIccid>;
  let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
  let createPsimDeliveredOrderSpy: MockInstance<typeof portalGateway.createPsimDeliveredOrder>;

  beforeEach(() => {
    validateIccidSpy = vi.spyOn(mavenirMsisdnGateway, 'validateIccid');
    patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
    createPsimDeliveredOrderSpy = vi.spyOn(portalGateway, 'createPsimDeliveredOrder');
  });

  scenario('Activate Sim', ({ given, when, then }) => {
    let cart: Cart;

    given('Mavenir has valid ICCID available in inventory', async () => {
      mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      cart = await customerWaitingForPsim();
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      cart.line!.activateSim(enteredValidIccid);
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {
      expect(validateIccidSpy).toHaveBeenCalledWith(enteredValidIccid);
    }).and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {
      expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim, enteredValidIccid);
    }).and('My Paradise sends the pSIM delivered order to Mavenir', () => {
      expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
    });
    when('Mavenir creates the product order and clears waiting pSIM', async () => {
      cart = await reloadCart(cart);
    });
    then('My Paradise stores valid ICCID on the line', () => {
      expect(cart.line?.simType).toBe(SimType.Psim);
      expect(cart.line?.iccid).toBe(expectedValidIccid);
    });
  });

  scenario('waiting pSIM is absent', ({ given, when, then }) => {
    let cart: Cart;
    let result: Error | object;

    given('Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic', async () => {
      mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      cart = await customerWaitingForPsim();
      const mavenirCustomer = portalGateway.read(cart.customer.id);
      if (!(mavenirCustomer instanceof Error)) mavenirCustomer.waitingPsim = null;
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      result = cart.line!.activateSim(enteredValidIccid);
    });
    then('the pSIM delivered order is rejected', () => {
      expect(result).toBeInstanceOf(Error);
      expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
    });
  });

  scenario('waiting pSIM already completed', ({ given, when, then }) => {
    let cart: Cart;
    let result: Error | object;

    given('Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false', async () => {
      mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      cart = await customerWaitingForPsim();
      const mavenirCustomer = portalGateway.read(cart.customer.id);
      if (!(mavenirCustomer instanceof Error)) mavenirCustomer.waitingPsim = WaitingPsim.Cleared;
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      result = cart.line!.activateSim(enteredValidIccid);
    });
    then('the pSIM delivered order is rejected', () => {
      expect(result).toBeInstanceOf(Error);
      expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
    });
  });
});
