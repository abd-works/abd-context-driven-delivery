# ddd-screen-interface-not-a-domain-object-10

- **entry_id:** 1a4c210a
- **artifact:** tests/domain/profile-kyc/profile-kyc.ts (ProfileKyc, IdentityVerificationService interfaces)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** ProfileKyc modeled as its own screen interface with open(), isShowing(), submitProfile(), failureStateIsShown(). IdentityVerificationService modeled as a separate service with seedOutcome(), waitForCompletion(). Completing a profile is Customer.completeProfile(identity, address). Verifying identity is Customer.verifyIdentity(). These are operations on the Customer aggregate.
- **status:** fixed
