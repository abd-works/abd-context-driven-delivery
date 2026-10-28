from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart


# Epic: Enter Porting Number
# Orders: 0.0.1.0

# Story: Submit Portability Request
with story("Submit Portability Request"):
    # typescript body to translate:
    # let submitPortabilitySpy: MockInstance<typeof shoppingCartGateway.submitPortability>;
    # let sendVerificationSpy: MockInstance<typeof twilioGateway.sendVerification>;
    #
    # beforeEach(() => {
    #   submitPortabilitySpy = vi.spyOn(shoppingCartGateway, 'submitPortability');
    #   sendVerificationSpy = vi.spyOn(twilioGateway, 'sendVerification');
    # });
    #
    # portErrorOutlines.forEach(({ example, portNumber, donorOperator, accountNumber, userType, accountType, device, mavenirResult, twilioResult, expectedMessage }) => {
    # });
        with scenario("Port the number"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Portability | Error;
            # examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart
            with given("a My Paradise customer with a Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
                pass
            with and_("${storedHeldAvailableNumber} is available as a temporary port-in MSISDN"):
                # typescript body to translate:
                # shoppingCartGateway.seedSubmitPortabilityResult(storedHeldAvailableNumber);
                # twilioGateway.seedSendResult(PortabilityStatus.Sent);
                pass
            with when("the Customer enters valid portability and ports their number"):
                # typescript body to translate:
                # result = await cart.line!.port(
                #   enteredValidPortability.portNumber,
                #   enteredValidPortability.donorOperator,
                #   enteredValidPortability.accountNumber,
                #   enteredValidPortability.userType,
                #   enteredValidPortability.accountType,
                #   enteredValidPortability.device,
                # );
                pass
            with then("My Paradise submits the portability request to Mavenir with the customer's portability details"):
                # typescript body to translate:
                # expect(submitPortabilitySpy).toHaveBeenCalledWith(
                #   cart.customer.id,
                #   expect.objectContaining({
                #     portNumber: enteredValidPortability.portNumber,
                #     donorOperator: enteredValidPortability.donorOperator,
                #     accountNumber: enteredValidPortability.accountNumber,
                #   }),
                # );
                pass
            with and_("Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number"):
                # typescript body to translate:
                # expect(sendVerificationSpy).toHaveBeenCalledWith(
                #   `+1${enteredValidPortability.portNumber}`,
                #   cart.customer.id,
                # );
                pass
            with when("Mavenir assigns ${storedHeldAvailableNumber} as a temporary port-in MSISDN and patches the shopping cart, and Twilio sends the SMS verification"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("the Customer is forwarded to Verify Ported Number"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Portability);
                # expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
                # expect(cart.line?.portability?.portNumber).toBe(enteredValidPortability.portNumber);
                # expect(cart.line?.portability?.verified).toBe(false);
                # expect(cart.onboardingStep).toBe(OnboardingStep.VerifyPortedNumber);
                pass
        with scenario("Port the number — SMS verification skipped"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Portability | Error;
            # examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle
            with given("a My Paradise customer with a Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
                pass
            with and_("Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send"):
                # typescript body to translate:
                # shoppingCartGateway.seedSubmitPortabilityResult(storedHeldAvailableNumber);
                # twilioGateway.seedSendResult(PortabilityStatus.RateLimited);
                pass
            with when("the Customer enters valid portability and ports their number"):
                # typescript body to translate:
                # result = await cart.line!.port(
                #   enteredValidPortability.portNumber,
                #   enteredValidPortability.donorOperator,
                #   enteredValidPortability.accountNumber,
                #   enteredValidPortability.userType,
                #   enteredValidPortability.accountType,
                #   enteredValidPortability.device,
                # );
                pass
            with when("Mavenir processes the portability request and Twilio rate-limits the SMS send"):
                pass
            with then("portability is stored on the line with verification skipped"):
                # typescript body to translate:
                # expect(cart.line?.portability).toBe(result);
                # expect(cart.line?.portability?.verified).toBe(true);
                # expect(cart.line?.portability?.verificationSkipped).toBe(true);
                # expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
                pass
            with and_("the Customer is forwarded to Select Sim — no verification step required"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
                pass
        with scenario("Port the number: ${example}"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: Portability | Error;
            # examples: customerWithCart, stubBundle
            with given("a My Paradise customer with a Mavenir shopping cart"):
                # typescript body to translate:
                # cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
                # if (mavenirResult !== undefined) shoppingCartGateway.seedSubmitPortabilityResult(mavenirResult);
                # if (twilioResult !== undefined) twilioGateway.seedSendResult(twilioResult);
                pass
            with when("the Customer submits portability and ports their number"):
                # typescript body to translate:
                # result = await cart.line!.port(portNumber, donorOperator, accountNumber, userType, accountType, device);
                pass
            with then("submit returns error: ${expectedMessage}"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect((result as Error).message).toBe(expectedMessage);
                # expect(cart.line?.portability).toBeNull();
                # expect(cart.onboardingStep).toBe(OnboardingStep.PickNumber);
                # if (mavenirResult === undefined) expect(shoppingCartGateway.submitPortabilityCallCount()).toBe(0);
                pass
