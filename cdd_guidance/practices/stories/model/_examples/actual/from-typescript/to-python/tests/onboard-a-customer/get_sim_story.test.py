from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import reloadCart, customerReadyToChooseSim, enteredValidIccid, expectedValidIccid, enteredIccidWithSpaces, enteredInvalidIccid, customerWaitingForPsim


# Epic: Get Sim
# Orders: 0.0.6

# Story: Choose Esim
with story("Choose Esim"):
    # typescript body to translate:
    # let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
    #
    # beforeEach(() => {
    #   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
    # });
        with scenario("Choose eSIM"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: reloadCart, customerReadyToChooseSim
            with given("no SIM type is on the line"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim();
                pass
            with when("the Customer selects eSIM"):
                # typescript body to translate:
                # cart.line!.selectSim(SimType.Esim);
                pass
            with then("My Paradise sends the patch cart request to Mavenir with SIM type eSIM"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Esim);
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with SIM type eSIM"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores eSIM on the line"):
                # typescript body to translate:
                # expect(cart.line?.simType).toBe(SimType.Esim);
                pass
            with but_("the line has no ICCID"):
                # typescript body to translate:
                # expect(cart.line?.iccid).toBeNull();
                pass
            with and_("the Customer is forwarded to Verify ID"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
                pass
        with scenario("Choose eSIM — already on the line"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: customerReadyToChooseSim
            with given("the line already has SIM type eSIM"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim({ simType: SimType.Esim });
                pass
            with when("the Customer selects eSIM"):
                # typescript body to translate:
                # cart.line!.selectSim(SimType.Esim);
                pass
            with then("My Paradise skips the cart patch"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).not.toHaveBeenCalled();
                pass
        with scenario("Choose eSIM — cart patch fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: void | Error;
            # examples: reloadCart, customerReadyToChooseSim
            with given("Mavenir returns an error on cart patch"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim();
                # shoppingCartGateway.seedPatchCartWithSimError(new Error('Failed to select your sim'));
                pass
            with when("the Customer selects eSIM"):
                # typescript body to translate:
                # result = cart.line!.selectSim(SimType.Esim);
                pass
            with then("the SIM selection fails"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                pass
            with when("My Paradise reloads the shopping cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the line has no SIM type"):
                # typescript body to translate:
                # expect(cart.line?.simType).toBeNull();
                pass
            with and_("the line has no ICCID"):
                # typescript body to translate:
                # expect(cart.line?.iccid).toBeNull();
                pass

# Story: Request a Paradise Sim Card
with story("Request a Paradise Sim Card"):
    # typescript body to translate:
    # let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
    #
    # beforeEach(() => {
    #   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
    # });
        with scenario("Request a Paradise SIM card"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: reloadCart, customerReadyToChooseSim
            with given("no SIM type is on the line and no ICCID is on the line"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim();
                pass
            with when("the Customer requests a Paradise SIM card"):
                # typescript body to translate:
                # cart.line!.selectSim(SimType.Psim);
                pass
            with then("My Paradise sends the patch cart request to Mavenir with SIM type pSIM"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim);
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with SIM type pSIM"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores pSIM on the line"):
                # typescript body to translate:
                # expect(cart.line?.simType).toBe(SimType.Psim);
                pass
            with but_("the line has no ICCID"):
                # typescript body to translate:
                # expect(cart.line?.iccid).toBeNull();
                pass
            with and_("the Customer is forwarded to Verify ID"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
                pass
        with scenario("Request a Paradise SIM card — already on the line"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: customerReadyToChooseSim
            with given("the line already has SIM type pSIM"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim({ simType: SimType.Psim });
                pass
            with when("the Customer requests a Paradise SIM card"):
                # typescript body to translate:
                # cart.line!.selectSim(SimType.Psim);
                pass
            with then("My Paradise skips the cart patch"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).not.toHaveBeenCalled();
                pass
        with scenario("Request a Paradise SIM card — cart patch fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: void | Error;
            # examples: reloadCart, customerReadyToChooseSim
            with given("Mavenir returns an error on cart patch"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim();
                # shoppingCartGateway.seedPatchCartWithSimError(new Error('Failed to select your sim'));
                pass
            with when("the Customer requests a Paradise SIM card"):
                # typescript body to translate:
                # result = cart.line!.selectSim(SimType.Psim);
                pass
            with then("the SIM selection fails"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                pass
            with when("My Paradise reloads the shopping cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the line has no SIM type"):
                # typescript body to translate:
                # expect(cart.line?.simType).toBeNull();
                pass
            with and_("the line has no ICCID"):
                # typescript body to translate:
                # expect(cart.line?.iccid).toBeNull();
                pass

# Story: Enter Existing Sim
with story("Enter Existing Sim"):
    # typescript body to translate:
    # let validateIccidSpy: MockInstance<typeof mavenirMsisdnGateway.validateIccid>;
    # let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
    #
    # beforeEach(() => {
    #   validateIccidSpy = vi.spyOn(mavenirMsisdnGateway, 'validateIccid');
    #   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
    # });
        with scenario("Enter existing SIM"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: reloadCart, enteredValidIccid, expectedValidIccid, customerReadyToChooseSim
            with given("Mavenir has valid ICCID available in inventory"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
                # cart = await customerReadyToChooseSim();
                pass
            with when("the Customer attaches valid ICCID"):
                # typescript body to translate:
                # cart.line!.attachIccid(enteredValidIccid);
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with valid ICCID"):
                # typescript body to translate:
                # expect(validateIccidSpy).toHaveBeenCalledWith(enteredValidIccid);
                pass
            with and_("My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim, enteredValidIccid);
                pass
            with when("Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores pSIM and valid ICCID on the line"):
                # typescript body to translate:
                # expect(cart.line?.simType).toBe(SimType.Psim);
                pass
            with and_("the line has valid ICCID"):
                # typescript body to translate:
                # expect(cart.line?.iccid).toBe(expectedValidIccid);
                pass
            with and_("the Customer is forwarded to Verify ID"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.ProfileKyc);
                pass
        with scenario("ICCID contains spaces"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: void | Error;
            # examples: enteredIccidWithSpaces, customerReadyToChooseSim
            with given("the Customer has ICCID with spaces"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim();
                pass
            with when("the Customer attaches ICCID with spaces"):
                # typescript body to translate:
                # try { cart.line!.attachIccid(enteredIccidWithSpaces); } catch (e) { result = e as Error; }
                pass
            with then("the ICCID format is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect((result as Error).message).toBe('Please enter a valid iccid');
                pass
            with and_("My Paradise does not query inventory or patch the cart"):
                # typescript body to translate:
                # expect(validateIccidSpy).not.toHaveBeenCalled();
                # expect(patchCartWithSimSpy).not.toHaveBeenCalled();
                pass
        with scenario("Inventory rejects ICCID"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: void | Error;
            # examples: enteredInvalidIccid, customerReadyToChooseSim
            with given("Mavenir does not have invalid ICCID available in inventory"):
                # typescript body to translate:
                # cart = await customerReadyToChooseSim();
                pass
            with when("the Customer attaches invalid ICCID"):
                # typescript body to translate:
                # try { cart.line!.attachIccid(enteredInvalidIccid); } catch (e) { result = e as Error; }
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID"):
                # typescript body to translate:
                # expect(validateIccidSpy).toHaveBeenCalledWith(enteredInvalidIccid);
                pass
            with and_("My Paradise does not patch the cart"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).not.toHaveBeenCalled();
                pass
            with and_("the ICCID is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect((result as Error).message).toBe('Invalid ICCID.');
                pass

# Story: Activate Sim
with story("Activate Sim"):
    # typescript body to translate:
    # let validateIccidSpy: MockInstance<typeof mavenirMsisdnGateway.validateIccid>;
    # let patchCartWithSimSpy: MockInstance<typeof shoppingCartGateway.patchCartWithSim>;
    # let createPsimDeliveredOrderSpy: MockInstance<typeof portalGateway.createPsimDeliveredOrder>;
    #
    # beforeEach(() => {
    #   validateIccidSpy = vi.spyOn(mavenirMsisdnGateway, 'validateIccid');
    #   patchCartWithSimSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithSim');
    #   createPsimDeliveredOrderSpy = vi.spyOn(portalGateway, 'createPsimDeliveredOrder');
    # });
        with scenario("Activate Sim"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: reloadCart, enteredValidIccid, expectedValidIccid, customerWaitingForPsim
            with given("Mavenir has valid ICCID available in inventory"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
                # cart = await customerWaitingForPsim();
                pass
            with when("the Customer activates the SIM with valid ICCID"):
                # typescript body to translate:
                # cart.line!.activateSim(enteredValidIccid);
                pass
            with then("My Paradise sends the ICCID inventory request to Mavenir with valid ICCID"):
                # typescript body to translate:
                # expect(validateIccidSpy).toHaveBeenCalledWith(enteredValidIccid);
                pass
            with and_("My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID"):
                # typescript body to translate:
                # expect(patchCartWithSimSpy).toHaveBeenCalledWith(cart.customer.id, SimType.Psim, enteredValidIccid);
                pass
            with and_("My Paradise sends the pSIM delivered order to Mavenir"):
                # typescript body to translate:
                # expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
                pass
            with when("Mavenir creates the product order and clears waiting pSIM"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores valid ICCID on the line"):
                # typescript body to translate:
                # expect(cart.line?.simType).toBe(SimType.Psim);
                # expect(cart.line?.iccid).toBe(expectedValidIccid);
                pass
        with scenario("waiting pSIM is absent"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Error | object;
            # examples: enteredValidIccid, customerWaitingForPsim
            with given("Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
                # cart = await customerWaitingForPsim();
                # const mavenirCustomer = portalGateway.read(cart.customer.id);
                # if (!(mavenirCustomer instanceof Error)) mavenirCustomer.waitingPsim = null;
                pass
            with when("the Customer activates the SIM with valid ICCID"):
                # typescript body to translate:
                # result = cart.line!.activateSim(enteredValidIccid);
                pass
            with then("the pSIM delivered order is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
                pass
        with scenario("waiting pSIM already completed"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Error | object;
            # examples: enteredValidIccid, customerWaitingForPsim
            with given("Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableIccids([enteredValidIccid]);
                # cart = await customerWaitingForPsim();
                # const mavenirCustomer = portalGateway.read(cart.customer.id);
                # if (!(mavenirCustomer instanceof Error)) mavenirCustomer.waitingPsim = WaitingPsim.Cleared;
                pass
            with when("the Customer activates the SIM with valid ICCID"):
                # typescript body to translate:
                # result = cart.line!.activateSim(enteredValidIccid);
                pass
            with then("the pSIM delivered order is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect(createPsimDeliveredOrderSpy).toHaveBeenCalledWith(cart.customer.id);
                pass
