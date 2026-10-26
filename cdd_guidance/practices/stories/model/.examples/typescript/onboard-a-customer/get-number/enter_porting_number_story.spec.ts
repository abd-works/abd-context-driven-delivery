import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import {
  Cart,
  OnboardingStep,
} from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { Portability } from '../../../domain/number/Portability';
import { twilioGateway, PortabilityStatus } from '../../../domain/systems/twilio';
import { storedHeldAvailableNumber } from './examples/available-number.examples';
import { enteredValidPortability, portErrorOutlines } from './examples/portability.examples';
import { customerWithCart, stubBundle, reloadCart } from './examples/cart.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  twilioGateway.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Submit Portability Request', () => {
  let submitPortabilitySpy: MockInstance<typeof shoppingCartGateway.submitPortability>;
  let sendVerificationSpy: MockInstance<typeof twilioGateway.sendVerification>;

  beforeEach(() => {
    submitPortabilitySpy = vi.spyOn(shoppingCartGateway, 'submitPortability');
    sendVerificationSpy = vi.spyOn(twilioGateway, 'sendVerification');
  });

  scenario('Port the number', ({ given, when, then }) => {
    let cart: Cart;
    let result: Portability | Error;

    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
    }).and(`${storedHeldAvailableNumber} is available as a temporary port-in MSISDN`, () => {
      shoppingCartGateway.seedSubmitPortabilityResult(storedHeldAvailableNumber);
      twilioGateway.seedSendResult(PortabilityStatus.Sent);
    });
    when('the Customer enters valid portability and ports their number', async () => {
      result = await cart.line!.port(
        enteredValidPortability.portNumber,
        enteredValidPortability.donorOperator,
        enteredValidPortability.accountNumber,
        enteredValidPortability.userType,
        enteredValidPortability.accountType,
        enteredValidPortability.device,
      );
    });
    then(`My Paradise submits the portability request to Mavenir with the customer's portability details`, () => {
      expect(submitPortabilitySpy).toHaveBeenCalledWith(
        cart.customer.id,
        expect.objectContaining({
          portNumber: enteredValidPortability.portNumber,
          donorOperator: enteredValidPortability.donorOperator,
          accountNumber: enteredValidPortability.accountNumber,
        }),
      );
    }).and('Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number', () => {
      expect(sendVerificationSpy).toHaveBeenCalledWith(
        `+1${enteredValidPortability.portNumber}`,
        cart.customer.id,
      );
    });
    when(`Mavenir assigns ${storedHeldAvailableNumber} as a temporary port-in MSISDN and patches the shopping cart, and Twilio sends the SMS verification`, async () => {
      cart = await reloadCart(cart);
    });
    then('the Customer is forwarded to Verify Ported Number', () => {
      expect(result).toBeInstanceOf(Portability);
      expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
      expect(cart.line?.portability?.portNumber).toBe(enteredValidPortability.portNumber);
      expect(cart.line?.portability?.verified).toBe(false);
      expect(cart.onboardingStep).toBe(OnboardingStep.VerifyPortedNumber);
    });
  });

  scenario('Port the number — SMS verification skipped', ({ given, when, then }) => {
    let cart: Cart;
    let result: Portability | Error;

    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
    }).and('Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send', () => {
      shoppingCartGateway.seedSubmitPortabilityResult(storedHeldAvailableNumber);
      twilioGateway.seedSendResult(PortabilityStatus.RateLimited);
    });
    when('the Customer enters valid portability and ports their number', async () => {
      result = await cart.line!.port(
        enteredValidPortability.portNumber,
        enteredValidPortability.donorOperator,
        enteredValidPortability.accountNumber,
        enteredValidPortability.userType,
        enteredValidPortability.accountType,
        enteredValidPortability.device,
      );
    });
    when('Mavenir processes the portability request and Twilio rate-limits the SMS send', () => {});
    then('portability is stored on the line with verification skipped', () => {
      expect(cart.line?.portability).toBe(result);
      expect(cart.line?.portability?.verified).toBe(true);
      expect(cart.line?.portability?.verificationSkipped).toBe(true);
      expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
    }).and('the Customer is forwarded to Select Sim — no verification step required', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
    });
  });

  portErrorOutlines.forEach(({ example, portNumber, donorOperator, accountNumber, userType, accountType, device, mavenirResult, twilioResult, expectedMessage }) => {
    scenario(`Port the number: ${example}`, ({ given, when, then }) => {
      let cart: Cart;
      let result: Portability | Error;

      given('a My Paradise customer with a Mavenir shopping cart', async () => {
        cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
        if (mavenirResult !== undefined) shoppingCartGateway.seedSubmitPortabilityResult(mavenirResult);
        if (twilioResult !== undefined) twilioGateway.seedSendResult(twilioResult);
      });
      when('the Customer submits portability and ports their number', async () => {
        result = await cart.line!.port(portNumber, donorOperator, accountNumber, userType, accountType, device);
      });
      then(`submit returns error: ${expectedMessage}`, () => {
        expect(result).toBeInstanceOf(Error);
        expect((result as Error).message).toBe(expectedMessage);
        expect(cart.line?.portability).toBeNull();
        expect(cart.onboardingStep).toBe(OnboardingStep.PickNumber);
        if (mavenirResult === undefined) expect(shoppingCartGateway.submitPortabilityCallCount()).toBe(0);
      });
    });
  });
});
