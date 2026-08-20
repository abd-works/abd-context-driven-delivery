# authentication-service-separation-5

- **entry_id:** a3f92c11
- **artifact:** tests/domain/customer/customer.ts and tests/domain/customer/customer.e2e.ts
- **rule:** authentication-service-separation — Credentials must be a pure form object (field values + validation feedback only); authentication operations (authenticate, register, signOut, requestPasswordReset, resetPassword) must live on AuthenticationService which receives a filled Credentials; ParadiseMobile.authentication() returns AuthenticationService not Credentials
- **wrong:** Credentials interface carried both the form data/validation AND the auth operations (signIn, register, signOut, requestPasswordReset, resetPassword); CredentialsE2e mixed form interaction with auth flow execution in the same class
- **status:** fixed
