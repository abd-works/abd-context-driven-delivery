/**
 * Epic: Verify Ported Number
 * Orders: 0.0.1.2
 */

import { background, scenario, story } from "../../story-test.js";
import { enteredValidPortability, validPortingSmscode, customerWithCartAndPortability, mismatchPortingSmscode } from "./examples";

/**
 * Story: Check Port Verification
 */

story('Check Port Verification', () => {
  // typescript body to translate:
  // let checkVerificationSpy: MockInstance<typeof twilioGateway.checkVerification>;
  //
  // beforeEach(() => {
  //   checkVerificationSpy = vi.spyOn(twilioGateway, 'checkVerification');
  // });
  scenario('Enter porting SMS code', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: PortabilityVerification | Error;
    // examples: enteredValidPortability, validPortingSmscode, customerWithCartAndPortability
    given('the Customer submitted portability and Twilio sent an SMS to the port number', async () => {
      // typescript body to translate:
      // cart = await customerWithCartAndPortability();
      // TODO: implement step
    })
      .and('Twilio is ready to confirm the SMS code as valid', () => {
        // typescript body to translate:
        // twilioGateway.seedCheckResult(true);
        // TODO: implement step
      });
    when('the Customer enters verification code ${validPortingSmscode}', async () => {
      // typescript body to translate:
      // result = await cart.line!.portability!.verify(validPortingSmscode);
      // TODO: implement step
    });
    then('My Paradise sends the verification check to Twilio with the port number and code', () => {
      // typescript body to translate:
      // expect(checkVerificationSpy).toHaveBeenCalledWith(
      //   `+1${enteredValidPortability.portNumber}`,
      //   validPortingSmscode,
      // );
      // TODO: implement step
    });
    when('Twilio creates a verification check (verificationChecks.create)', () => {
      // TODO: implement step
    });
    then('Twilio returns approved and the Customer is forwarded to Select Sim', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(PortabilityVerification);
      // expect((result as PortabilityVerification).verified).toBe(true);
      // expect(cart.line?.portability?.verified).toBe(true);
      // expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
      // TODO: implement step
    });
  });

  scenario('Verify with unusable porting SMS code', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: PortabilityVerification | Error;
    // examples: enteredValidPortability, mismatchPortingSmscode, customerWithCartAndPortability
    given('the Customer submitted portability and has an incorrect verification code', async () => {
      // typescript body to translate:
      // cart = await customerWithCartAndPortability();
      // twilioGateway.seedCheckResult(false);
      // TODO: implement step
    });
    when('the Customer enters verification code ${mismatchPortingSmscode}', async () => {
      // typescript body to translate:
      // result = await cart.line!.portability!.verify(mismatchPortingSmscode);
      // TODO: implement step
    });
    then('My Paradise sends the verification check to Twilio', () => {
      // typescript body to translate:
      // expect(checkVerificationSpy).toHaveBeenCalledWith(
      //   `+1${enteredValidPortability.portNumber}`,
      //   mismatchPortingSmscode,
      // );
      // TODO: implement step
    });
    when('Twilio creates a verification check and returns a non-approved status', () => {
      // TODO: implement step
    });
    then('the verification is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(PortabilityVerification);
      // expect((result as PortabilityVerification).verified).toBe(false);
      // TODO: implement step
    });
  });

  scenario('Resend porting SMS code', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let sendVerificationSpy: MockInstance<typeof twilioGateway.sendVerification>;
    // let result: PortabilityStatus | Error;
    // examples: enteredValidPortability, customerWithCartAndPortability
    given('the Customer submitted portability and Twilio sent an SMS to the port number', async () => {
      // typescript body to translate:
      // cart = await customerWithCartAndPortability();
      // sendVerificationSpy = vi.spyOn(twilioGateway, 'sendVerification');
      // TODO: implement step
    });
    when('the Customer requests a new verification code', async () => {
      // typescript body to translate:
      // result = await cart.line!.portability!.resend();
      // TODO: implement step
    });
    then('My Paradise SMSes a porting verification code via Twilio', () => {
      // typescript body to translate:
      // expect(sendVerificationSpy).toHaveBeenCalledWith(
      //   `+1${enteredValidPortability.portNumber}`,
      //   cart.customer.id,
      // );
      // TODO: implement step
    });
    when('Twilio sends the SMS verification', () => {
      // TODO: implement step
    });
    then('the resend is confirmed', () => {
      // typescript body to translate:
      // expect(result).toBe(PortabilityStatus.Sent);
      // TODO: implement step
    });
  });
});
