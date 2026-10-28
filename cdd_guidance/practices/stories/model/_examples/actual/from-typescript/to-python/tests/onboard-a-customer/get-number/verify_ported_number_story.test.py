from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import enteredValidPortability, validPortingSmscode, customerWithCartAndPortability, mismatchPortingSmscode


# Epic: Verify Ported Number
# Orders: 0.0.1.2

# Story: Check Port Verification
with story("Check Port Verification"):
    # typescript body to translate:
    # let checkVerificationSpy: MockInstance<typeof twilioGateway.checkVerification>;
    #
    # beforeEach(() => {
    #   checkVerificationSpy = vi.spyOn(twilioGateway, 'checkVerification');
    # });
        with scenario("Enter porting SMS code"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: PortabilityVerification | Error;
            # examples: enteredValidPortability, validPortingSmscode, customerWithCartAndPortability
            with given("the Customer submitted portability and Twilio sent an SMS to the port number"):
                # typescript body to translate:
                # cart = await customerWithCartAndPortability();
                pass
            with and_("Twilio is ready to confirm the SMS code as valid"):
                # typescript body to translate:
                # twilioGateway.seedCheckResult(true);
                pass
            with when("the Customer enters verification code ${validPortingSmscode}"):
                # typescript body to translate:
                # result = await cart.line!.portability!.verify(validPortingSmscode);
                pass
            with then("My Paradise sends the verification check to Twilio with the port number and code"):
                # typescript body to translate:
                # expect(checkVerificationSpy).toHaveBeenCalledWith(
                #   `+1${enteredValidPortability.portNumber}`,
                #   validPortingSmscode,
                # );
                pass
            with when("Twilio creates a verification check (verificationChecks.create)"):
                pass
            with then("Twilio returns approved and the Customer is forwarded to Select Sim"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(PortabilityVerification);
                # expect((result as PortabilityVerification).verified).toBe(true);
                # expect(cart.line?.portability?.verified).toBe(true);
                # expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
                pass
        with scenario("Verify with unusable porting SMS code"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: PortabilityVerification | Error;
            # examples: enteredValidPortability, mismatchPortingSmscode, customerWithCartAndPortability
            with given("the Customer submitted portability and has an incorrect verification code"):
                # typescript body to translate:
                # cart = await customerWithCartAndPortability();
                # twilioGateway.seedCheckResult(false);
                pass
            with when("the Customer enters verification code ${mismatchPortingSmscode}"):
                # typescript body to translate:
                # result = await cart.line!.portability!.verify(mismatchPortingSmscode);
                pass
            with then("My Paradise sends the verification check to Twilio"):
                # typescript body to translate:
                # expect(checkVerificationSpy).toHaveBeenCalledWith(
                #   `+1${enteredValidPortability.portNumber}`,
                #   mismatchPortingSmscode,
                # );
                pass
            with when("Twilio creates a verification check and returns a non-approved status"):
                pass
            with then("the verification is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(PortabilityVerification);
                # expect((result as PortabilityVerification).verified).toBe(false);
                pass
        with scenario("Resend porting SMS code"):
            # typescript body to translate:
            # let cart: Cart;
            # let sendVerificationSpy: MockInstance<typeof twilioGateway.sendVerification>;
            # let result: PortabilityStatus | Error;
            # examples: enteredValidPortability, customerWithCartAndPortability
            with given("the Customer submitted portability and Twilio sent an SMS to the port number"):
                # typescript body to translate:
                # cart = await customerWithCartAndPortability();
                # sendVerificationSpy = vi.spyOn(twilioGateway, 'sendVerification');
                pass
            with when("the Customer requests a new verification code"):
                # typescript body to translate:
                # result = await cart.line!.portability!.resend();
                pass
            with then("My Paradise SMSes a porting verification code via Twilio"):
                # typescript body to translate:
                # expect(sendVerificationSpy).toHaveBeenCalledWith(
                #   `+1${enteredValidPortability.portNumber}`,
                #   cart.customer.id,
                # );
                pass
            with when("Twilio sends the SMS verification"):
                pass
            with then("the resend is confirmed"):
                # typescript body to translate:
                # expect(result).toBe(PortabilityStatus.Sent);
                pass
