import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import { PortabilityVerification, PortabilityStatus } from '../../../domain/systems/twilio';
import { twilioGateway } from '../../../domain/systems/twilio';
import { enteredValidPortability } from './examples/portability.examples';
import { validPortingSmscode, mismatchPortingSmscode } from './examples/porting-sms-code.examples';
import { customerWithCartAndPortability } from './examples/cart.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  twilioGateway.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

// Flagged: Live porting-2fa is off. SMS step is not mounted in the live sandbox.
story('Check Port Verification', () => {
  let checkVerificationSpy: MockInstance<typeof twilioGateway.checkVerification>;

  beforeEach(() => {
    checkVerificationSpy = vi.spyOn(twilioGateway, 'checkVerification');
  });

  scenario('Enter porting SMS code', ({ given, when, then }) => {
    let cart: Cart;
    let result: PortabilityVerification | Error;

    given('the Customer submitted portability and Twilio sent an SMS to the port number', async () => {
      cart = await customerWithCartAndPortability();
    }).and('Twilio is ready to confirm the SMS code as valid', () => {
      twilioGateway.seedCheckResult(true);
    });
    when(`the Customer enters verification code ${validPortingSmscode}`, async () => {
      result = await cart.line!.portability!.verify(validPortingSmscode);
    });
    then('My Paradise sends the verification check to Twilio with the port number and code', () => {
      expect(checkVerificationSpy).toHaveBeenCalledWith(
        `+1${enteredValidPortability.portNumber}`,
        validPortingSmscode,
      );
    });
    when('Twilio creates a verification check (verificationChecks.create)', () => {});
    then('Twilio returns approved and the Customer is forwarded to Select Sim', () => {
      expect(result).toBeInstanceOf(PortabilityVerification);
      expect((result as PortabilityVerification).verified).toBe(true);
      expect(cart.line?.portability?.verified).toBe(true);
      expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
    });
  });

  scenario('Verify with unusable porting SMS code', ({ given, when, then }) => {
    let cart: Cart;
    let result: PortabilityVerification | Error;

    given('the Customer submitted portability and has an incorrect verification code', async () => {
      cart = await customerWithCartAndPortability();
      twilioGateway.seedCheckResult(false);
    });
    when(`the Customer enters verification code ${mismatchPortingSmscode}`, async () => {
      result = await cart.line!.portability!.verify(mismatchPortingSmscode);
    });
    then('My Paradise sends the verification check to Twilio', () => {
      expect(checkVerificationSpy).toHaveBeenCalledWith(
        `+1${enteredValidPortability.portNumber}`,
        mismatchPortingSmscode,
      );
    });
    when('Twilio creates a verification check and returns a non-approved status', () => {});
    then('the verification is rejected', () => {
      expect(result).toBeInstanceOf(PortabilityVerification);
      expect((result as PortabilityVerification).verified).toBe(false);
    });
  });

  scenario('Resend porting SMS code', ({ given, when, then }) => {
    let cart: Cart;
    let sendVerificationSpy: MockInstance<typeof twilioGateway.sendVerification>;
    let result: PortabilityStatus | Error;

    given('the Customer submitted portability and Twilio sent an SMS to the port number', async () => {
      cart = await customerWithCartAndPortability();
      sendVerificationSpy = vi.spyOn(twilioGateway, 'sendVerification');
    });
    when('the Customer requests a new verification code', async () => {
      result = await cart.line!.portability!.resend();
    });
    then('My Paradise SMSes a porting verification code via Twilio', () => {
      expect(sendVerificationSpy).toHaveBeenCalledWith(
        `+1${enteredValidPortability.portNumber}`,
        cart.customer.id,
      );
    });
    when('Twilio sends the SMS verification', () => {});
    then('the resend is confirmed', () => {
      expect(result).toBe(PortabilityStatus.Sent);
    });
  });
});
