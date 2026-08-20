# separate-concerns

- **entry_id:** df92e741
- **artifact:** tests/onboard-a-customer/profile-kyc.e2e.ts
- **rule:** separate-concerns — selecting a SIM is a cart operation that lands the prospect on Profile & KYC; completing KYC is prospect.verifyIdentity(); do not drive KYC through cartRepository + identityVerificationService.waitForCompletion() or mention verify-id routes
- **wrong:** Fail scenario (and siblings) went eSIM → KYC by calling cartRepository.current().selectSim then a top-level waitForCompletion(), then reloaded the prospect. The hop from SIM selection to identity verification was a hidden route change, not a named prospect operation.
- **status:** open
