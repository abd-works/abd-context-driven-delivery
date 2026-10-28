/**
 * Epic: Get Sim
 * Orders: 0.0.6
 */

import { background, scenario, story } from "../story-test.js";
import { reloadCart, customerReadyToChooseSim, enteredValidIccid, expectedValidIccid, enteredIccidWithSpaces, enteredInvalidIccid, customerWaitingForPsim } from "./examples";

/**
 * Story: Choose Esim
 */

story('Choose Esim', () => {
  // typescript body to translate:
  // let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
  //
  // beforeEach(() => {
  //   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  // });
  scenario('Choose eSIM', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: reloadCart, customerReadyToChooseSim
    given('no SIM type is on the line', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim();
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // typescript body to translate:
      // cart.line!.selectSim(SimType.Esim);
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with SIM type eSIM', () => {
      // typescript body to translate:
      // expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Esim);
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type eSIM', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores eSIM on the line', () => {
      // typescript body to translate:
      // expect(cart.line?.simType).toBe(SimType.Esim);
      // TODO: implement step
    })
      .but('the line has no ICCID', () => {
        // typescript body to translate:
        // expect(cart.line?.iccid).toBeNull();
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
        // TODO: implement step
      });
  });

  scenario('Choose eSIM — already on the line', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: customerReadyToChooseSim
    given('the line already has SIM type eSIM', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim({ simType: SimType.Esim });
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // typescript body to translate:
      // cart.line!.selectSim(SimType.Esim);
      // TODO: implement step
    });
    then('My Paradise skips the cart patch', () => {
      // typescript body to translate:
      // expect(patchCartWithSimSpy).not.toHaveBeenCalled();
      // TODO: implement step
    });
  });

  scenario('Choose eSIM — cart patch fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: void | Error;
    // examples: reloadCart, customerReadyToChooseSim
    given('Mavenir returns an error on cart patch', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim();
      // shoppingCartGateway.seedPatchCartWithSimError(new Error('Failed to select your sim'));
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // typescript body to translate:
      // result = cart.line!.selectSim(SimType.Esim);
      // TODO: implement step
    });
    then('the SIM selection fails', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the line has no SIM type', () => {
      // typescript body to translate:
      // expect(cart.line?.simType).toBeNull();
      // TODO: implement step
    })
      .and('the line has no ICCID', () => {
        // typescript body to translate:
        // expect(cart.line?.iccid).toBeNull();
        // TODO: implement step
      });
  });
});

/**
 * Story: Request a Paradise Sim Card
 */

story('Request a Paradise Sim Card', () => {
  // typescript body to translate:
  // let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
  //
  // beforeEach(() => {
  //   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  // });
  scenario('Request a Paradise SIM card', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: reloadCart, customerReadyToChooseSim
    given('no SIM type is on the line and no ICCID is on the line', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim();
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // typescript body to translate:
      // cart.line!.selectSim(SimType.Psim);
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with SIM type pSIM', () => {
      // typescript body to translate:
      // expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim);
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores pSIM on the line', () => {
      // typescript body to translate:
      // expect(cart.line?.simType).toBe(SimType.Psim);
      // TODO: implement step
    })
      .but('the line has no ICCID', () => {
        // typescript body to translate:
        // expect(cart.line?.iccid).toBeNull();
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
        // TODO: implement step
      });
  });

  scenario('Request a Paradise SIM card — already on the line', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: customerReadyToChooseSim
    given('the line already has SIM type pSIM', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim({ simType: SimType.Psim });
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // typescript body to translate:
      // cart.line!.selectSim(SimType.Psim);
      // TODO: implement step
    });
    then('My Paradise skips the cart patch', () => {
      // typescript body to translate:
      // expect(patchCartWithSimSpy).not.toHaveBeenCalled();
      // TODO: implement step
    });
  });

  scenario('Request a Paradise SIM card — cart patch fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: void | Error;
    // examples: reloadCart, customerReadyToChooseSim
    given('Mavenir returns an error on cart patch', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim();
      // shoppingCartGateway.seedPatchCartWithSimError(new Error('Failed to select your sim'));
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // typescript body to translate:
      // result = cart.line!.selectSim(SimType.Psim);
      // TODO: implement step
    });
    then('the SIM selection fails', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the line has no SIM type', () => {
      // typescript body to translate:
      // expect(cart.line?.simType).toBeNull();
      // TODO: implement step
    })
      .and('the line has no ICCID', () => {
        // typescript body to translate:
        // expect(cart.line?.iccid).toBeNull();
        // TODO: implement step
      });
  });
});

/**
 * Story: Enter Existing Sim
 */

story('Enter Existing Sim', () => {
  // typescript body to translate:
  // let validateIccidSpy: MockInstance<typeof mavenirMsisdnGateway.validateIccid>;
  // let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
  //
  // beforeEach(() => {
  //   validateIccidSpy = vi.spyOn(mavenirMsisdnGateway, 'validateIccid');
  //   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  // });
  scenario('Enter existing SIM', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: reloadCart, enteredValidIccid, expectedValidIccid, customerReadyToChooseSim
    given('Mavenir has valid ICCID available in inventory', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      // cart = await customerReadyToChooseSim();
      // TODO: implement step
    });
    when('the Customer attaches valid ICCID', () => {
      // typescript body to translate:
      // cart.line!.attachIccid(enteredValidIccid);
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {
      // typescript body to translate:
      // expect(validateIccidSpy).toHaveBeenCalledWith(enteredValidIccid);
      // TODO: implement step
    })
      .and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {
        // typescript body to translate:
        // expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim, enteredValidIccid);
        // TODO: implement step
      });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores pSIM and valid ICCID on the line', () => {
      // typescript body to translate:
      // expect(cart.line?.simType).toBe(SimType.Psim);
      // TODO: implement step
    })
      .and('the line has valid ICCID', () => {
        // typescript body to translate:
        // expect(cart.line?.iccid).toBe(expectedValidIccid);
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
        // TODO: implement step
      });
  });

  scenario('ICCID contains spaces', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: void | Error;
    // examples: enteredIccidWithSpaces, customerReadyToChooseSim
    given('the Customer has ICCID with spaces', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim();
      // TODO: implement step
    });
    when('the Customer attaches ICCID with spaces', () => {
      // typescript body to translate:
      // try { cart.line!.attachIccid(enteredIccidWithSpaces); } catch (e) { result = e as Error; }
      // TODO: implement step
    });
    then('the ICCID format is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // expect((result as Error).message).toBe('Please enter a valid iccid');
      // TODO: implement step
    })
      .and('My Paradise does not query inventory or patch the cart', () => {
        // typescript body to translate:
        // expect(validateIccidSpy).not.toHaveBeenCalled();
        // expect(patchCartWithSimSpy).not.toHaveBeenCalled();
        // TODO: implement step
      });
  });

  scenario('Inventory rejects ICCID', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: void | Error;
    // examples: enteredInvalidIccid, customerReadyToChooseSim
    given('Mavenir does not have invalid ICCID available in inventory', async () => {
      // typescript body to translate:
      // cart = await customerReadyToChooseSim();
      // TODO: implement step
    });
    when('the Customer attaches invalid ICCID', () => {
      // typescript body to translate:
      // try { cart.line!.attachIccid(enteredInvalidIccid); } catch (e) { result = e as Error; }
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID', () => {
      // typescript body to translate:
      // expect(validateIccidSpy).toHaveBeenCalledWith(enteredInvalidIccid);
      // TODO: implement step
    })
      .and('My Paradise does not patch the cart', () => {
        // typescript body to translate:
        // expect(patchCartWithSimSpy).not.toHaveBeenCalled();
        // TODO: implement step
      })
      .and('the ICCID is rejected', () => {
        // typescript body to translate:
        // expect(result).toBeInstanceOf(Error);
        // expect((result as Error).message).toBe('Invalid ICCID.');
        // TODO: implement step
      });
  });
});

/**
 * Story: Activate Sim
 */

story('Activate Sim', () => {
  // typescript body to translate:
  // let validateIccidSpy: MockInstance<typeof mavenirMsisdnGateway.validateIccid>;
  // let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
  // let createPsimDeliveredOrderSpy: MockInstance<typeof portalGateway.createPsimDeliveredOrder>;
  //
  // beforeEach(() => {
  //   validateIccidSpy = vi.spyOn(mavenirMsisdnGateway, 'validateIccid');
  //   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
  //   createPsimDeliveredOrderSpy = vi.spyOn(portalGateway, 'createPsimDeliveredOrder');
  // });
  scenario('Activate Sim', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: reloadCart, enteredValidIccid, expectedValidIccid, customerWaitingForPsim
    given('Mavenir has valid ICCID available in inventory', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      // cart = await customerWaitingForPsim();
      // TODO: implement step
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      // typescript body to translate:
      // cart.line!.activateSim(enteredValidIccid);
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {
      // typescript body to translate:
      // expect(validateIccidSpy).toHaveBeenCalledWith(enteredValidIccid);
      // TODO: implement step
    })
      .and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {
        // typescript body to translate:
        // expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim, enteredValidIccid);
        // TODO: implement step
      })
      .and('My Paradise sends the pSIM delivered order to Mavenir', () => {
        // typescript body to translate:
        // expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
        // TODO: implement step
      });
    when('Mavenir creates the product order and clears waiting pSIM', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores valid ICCID on the line', () => {
      // typescript body to translate:
      // expect(cart.line?.simType).toBe(SimType.Psim);
      // expect(cart.line?.iccid).toBe(expectedValidIccid);
      // TODO: implement step
    });
  });

  scenario('waiting pSIM is absent', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Error | object;
    // examples: enteredValidIccid, customerWaitingForPsim
    given('Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      // cart = await customerWaitingForPsim();
      // const mavenirCustomer = portalGateway.read(cart.customer.id);
      // if (!(mavenirCustomer instanceof Error)) mavenirCustomer.waitingPsim = null;
      // TODO: implement step
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      // typescript body to translate:
      // result = cart.line!.activateSim(enteredValidIccid);
      // TODO: implement step
    });
    then('the pSIM delivered order is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
      // TODO: implement step
    });
  });

  scenario('waiting pSIM already completed', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Error | object;
    // examples: enteredValidIccid, customerWaitingForPsim
    given('Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
      // cart = await customerWaitingForPsim();
      // const mavenirCustomer = portalGateway.read(cart.customer.id);
      // if (!(mavenirCustomer instanceof Error)) mavenirCustomer.waitingPsim = WaitingPsim.Cleared;
      // TODO: implement step
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      // typescript body to translate:
      // result = cart.line!.activateSim(enteredValidIccid);
      // TODO: implement step
    });
    then('the pSIM delivered order is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
      // TODO: implement step
    });
  });
});
