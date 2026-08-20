# ddd-service-should-be-aggregate-operation-2

- **entry_id:** 5e809e0e
- **artifact:** tests/domain/customer/customer.ts (AuthenticationService interface)
- **rule:** (ddd) service-should-be-aggregate-operation
- **wrong:** AuthenticationService has granular UI methods (fillEmail, fillPassword, fillConfirmPassword, submitRegistration, fillOtp, submitEmailVerification) that are page-level interactions, not domain operations. These belong on a Credentials domain object — Credentials should have behavior for validation, submission, and password rules, not a service that drives form fields.
- **status:** open
