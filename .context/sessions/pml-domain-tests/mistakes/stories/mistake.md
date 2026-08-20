# stories

- **entry_id:** c9d4e812
- **artifact:** tests/onboard-a-customer/sign-up-create-account/sign_up_create_account_story.ts + tests/domain/customer/customer.e2e.ts
- **rule:** Stories — capture-all-scenarios-not-just-happy-path; trace client-side validation (react-hook-form, PasswordRules, MUI helperText) during acceptance-test codification; ask during specification whether to cover all scenarios or main path only
- **wrong:** 'Sign Up — Create Account' was codified with only the positive path (submit valid email + password → Cognito signUp → redirect to /validate-email). Missed the interactive client-side validation the Create Account form actually implements: react-hook-form mode:'all' shows email format errors in helperText while the address is still being typed and clears them once valid; PasswordRules checklist (src/components/Form/components/PasswordRules) switches each rule from neutral bullet → red ✖ while typing a non-conforming password → green ✓ as each regex is satisfied. Did not inspect the JavaScript validation layer when building the story — inferred behavior from the happy-path GWT in cdd-sketch.md/scenario.md only. Also did not ask during specification whether to capture all scenarios vs main path only.
- **status:** open
