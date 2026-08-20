# authentication-service-separation-4

- **entry_id:** 1bdb72de
- **artifact:** tests/domain/customer/customer.e2e.ts
- **rule:** authentication-service-separation — CredentialsE2e must only implement the form object contract; auth flow operations belong on AuthenticationServiceE2e which receives a filled Credentials and drives the session operation
- **wrong:** CredentialsE2e implemented signIn(), register(), signOut(), requestPasswordReset(), resetPassword() — mixing form interaction with auth flow execution in the same class
- **status:** fixed
