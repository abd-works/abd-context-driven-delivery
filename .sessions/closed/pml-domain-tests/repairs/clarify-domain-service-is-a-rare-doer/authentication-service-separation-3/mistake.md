# authentication-service-separation-3

- **entry_id:** 1f8158e8
- **artifact:** tests/domain/customer/customer.ts and tests/domain/paradise-mobile/paradise-mobile.ts
- **rule:** authentication-service-separation — Credentials must be a pure form object (field values + validation feedback only); authentication operations (signIn/register/signOut/requestPasswordReset/resetPassword) must live on a distinct AuthenticationService, not on Credentials itself
- **wrong:** Credentials interface carried both the form data/validation AND the auth operations (signIn, register, signOut, requestPasswordReset, resetPassword); paradise-mobile.ts returned Credentials from authentication() instead of AuthenticationService
- **status:** fixed
