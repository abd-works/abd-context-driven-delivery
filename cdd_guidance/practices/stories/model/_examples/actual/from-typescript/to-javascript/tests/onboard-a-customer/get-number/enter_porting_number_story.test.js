/**
 * Epic: Enter Porting Number
 * Orders: 0.0.1.0
 */

import { background, scenario, story } from "../../story-test.js";
import { storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart } from "./examples";

/**
 * Story: Submit Portability Request
 */

story('Submit Portability Request', () => {
  // typescript body to translate:
  // let submitPortabilitySpy: MockInstance<typeof shoppingCartGateway.submitPortability>;
  // let sendVerificationSpy: MockInstance<typeof twilioGateway.sendVerification>;
  //
  // beforeEach(() => {
  //   submitPortabilitySpy = vi.spyOn(shoppingCartGateway, 'submitPortability');
  //   sendVerificationSpy = vi.spyOn(twilioGateway, 'sendVerification');
  // });
  //
  // portErrorOutlines.forEach(({ example, portNumber, donorOperator, accountNumber, userType, accountType, device, mavenirResult, twilioResult, expectedMessage }) => {
  // });
  scenario('Port the number', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Portability | Error;
    // examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle, reloadCart
    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
      // TODO: implement step
    })
      .and('${storedHeldAvailableNumber} is available as a temporary port-in MSISDN', () => {
        // typescript body to translate:
        // shoppingCartGateway.seedSubmitPortabilityResult(storedHeldAvailableNumber);
        // twilioGateway.seedSendResult(PortabilityStatus.Sent);
        // TODO: implement step
      });
    when('the Customer enters valid portability and ports their number', async () => {
      // typescript body to translate:
      // result = await cart.line!.port(
      //   enteredValidPortability.portNumber,
      //   enteredValidPortability.donorOperator,
      //   enteredValidPortability.accountNumber,
      //   enteredValidPortability.userType,
      //   enteredValidPortability.accountType,
      //   enteredValidPortability.device,
      // );
      // TODO: implement step
    });
    then('My Paradise submits the portability request to Mavenir with the customer\'s portability details', () => {
      // typescript body to translate:
      // expect(submitPortabilitySpy).toHaveBeenCalledWith(
      //   cart.customer.id,
      //   expect.objectContaining({
      //     portNumber: enteredValidPortability.portNumber,
      //     donorOperator: enteredValidPortability.donorOperator,
      //     accountNumber: enteredValidPortability.accountNumber,
      //   }),
      // );
      // TODO: implement step
    })
      .and('Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number', () => {
        // typescript body to translate:
        // expect(sendVerificationSpy).toHaveBeenCalledWith(
        //   `+1${enteredValidPortability.portNumber}`,
        //   cart.customer.id,
        // );
        // TODO: implement step
      });
    when('Mavenir assigns ${storedHeldAvailableNumber} as a temporary port-in MSISDN and patches the shopping cart, and Twilio sends the SMS verification', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('the Customer is forwarded to Verify Ported Number', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Portability);
      // expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
      // expect(cart.line?.portability?.portNumber).toBe(enteredValidPortability.portNumber);
      // expect(cart.line?.portability?.verified).toBe(false);
      // expect(cart.onboardingStep).toBe(OnboardingStep.VerifyPortedNumber);
      // TODO: implement step
    });
  });

  scenario('Port the number — SMS verification skipped', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Portability | Error;
    // examples: storedHeldAvailableNumber, enteredValidPortability, customerWithCart, stubBundle
    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
      // TODO: implement step
    })
      .and('Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send', () => {
        // typescript body to translate:
        // shoppingCartGateway.seedSubmitPortabilityResult(storedHeldAvailableNumber);
        // twilioGateway.seedSendResult(PortabilityStatus.RateLimited);
        // TODO: implement step
      });
    when('the Customer enters valid portability and ports their number', async () => {
      // typescript body to translate:
      // result = await cart.line!.port(
      //   enteredValidPortability.portNumber,
      //   enteredValidPortability.donorOperator,
      //   enteredValidPortability.accountNumber,
      //   enteredValidPortability.userType,
      //   enteredValidPortability.accountType,
      //   enteredValidPortability.device,
      // );
      // TODO: implement step
    })
      .and('Mavenir processes the portability request and Twilio rate-limits the SMS send', () => {
        // TODO: implement step
      });
    then('portability is stored on the line with verification skipped', () => {
      // typescript body to translate:
      // expect(cart.line?.portability).toBe(result);
      // expect(cart.line?.portability?.verified).toBe(true);
      // expect(cart.line?.portability?.verificationSkipped).toBe(true);
      // expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
      // TODO: implement step
    })
      .and('the Customer is forwarded to Select Sim — no verification step required', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
        // TODO: implement step
      });
  });

  scenario('Port the number: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: Portability | Error;
    // examples: customerWithCart, stubBundle
    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      // typescript body to translate:
      // cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
      // if (mavenirResult !== undefined) shoppingCartGateway.seedSubmitPortabilityResult(mavenirResult);
      // if (twilioResult !== undefined) twilioGateway.seedSendResult(twilioResult);
      // TODO: implement step
    });
    when('the Customer submits portability and ports their number', async () => {
      // typescript body to translate:
      // result = await cart.line!.port(portNumber, donorOperator, accountNumber, userType, accountType, device);
      // TODO: implement step
    });
    then('submit returns error: ${expectedMessage}', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // expect((result as Error).message).toBe(expectedMessage);
      // expect(cart.line?.portability).toBeNull();
      // expect(cart.onboardingStep).toBe(OnboardingStep.PickNumber);
      // if (mavenirResult === undefined) expect(shoppingCartGateway.submitPortabilityCallCount()).toBe(0);
      // TODO: implement step
    });
  });
});
