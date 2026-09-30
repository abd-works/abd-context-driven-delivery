---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Sign In With Existing Account

## Examples

### account credentials

Sign-in rows. ++already-registered account credentials++ is the existing account. Password-rule rows stay on Create Account. Executable rows live in `stories/onboard-a-customer/examples/account-credentials.examples.ts`.

| account credentials | example | email | password |
| --- | --- | --- | --- |
| account credentials | already-registered account credentials | [Jeff.anderson@Agilebydesign.com](mailto:Jeff.anderson@Agilebydesign.com) | Stub@12345 |
| account credentials | valid account credentials | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spider-man99p |
| account credentials | wrong password | [Jeff.anderson@Agilebydesign.com](mailto:Jeff.anderson@Agilebydesign.com) | Wrong#Pass1 |
| account credentials | unknown email | [unknown.prospect@example.com](mailto:unknown.prospect@example.com) | Stub@12345 |
| account credentials | unconfirmed sign-in | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | Spider-man99p |
| account credentials | invalid email format | example.prospect | Stub@12345 |

### Cognito user

Sandbox `fetchUserAttributes` always returns `custom:customerId` = `cus_stub_pml_my_001` — source: `stories/onboard-a-customer/create-customer/create_customer_story.spec.md` Evidence, Validate Mavenir Customer in Cognito User Attributes.

| Cognito user | example | account credentials | confirmed | account token | Mavenir customer id |
| --- | --- | --- | --- | --- | --- |
| Cognito user | already-registered Cognito user | already-registered account credentials | yes | none | cus_stub_pml_my_001 |
| Cognito user | unconfirmed Cognito user | unconfirmed sign-in | no | none | none |
| Cognito user | signed-in Cognito user | already-registered account credentials | yes | issued | cus_stub_pml_my_001 |

## Story: Sign In With Existing Account

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/SignIn/pages/SignIn/SignIn.tsx` · `pml-my/src/pages/SignIn/pages/SignIn/hooks/useFormSignIn.tsx` · `pml-my/src/pages/SignIn/config/inputs.ts` · `pml-my/src/services/aws/cognito.ts`
- Run: `.context/sandbox-walkthrough/latest.md` L5–L24 (`/sign-in`)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`

One map node under Create Customer. Enter-credentials enablement and Cognito hops are scenarios / when-then pairs on this story (`domain-operation-story-not-system-hop`). Same live path as `Customer --> Enter Sign In Credentials` under Access Selfcare.

My Paradise authenticates ++account credentials++ through Amplify `signIn` (`username`, `password`) to Cognito. Token issuance is the transform of that same operation. The ++signed-in Cognito user++ is an existing account holder with a ++Mavenir customer++ id.

`AccountCredentials.authenticateAccount()` rejects unmet email-required, email-format, and password-required guards before Cognito. Confirm-password and password-complexity rules stay on Create Account.

### Evidence

| Source | Note |
| --- | --- |
| `cognito.ts` `signIn` | Amplify `signInAws({ username: email, password })`. No midtier URL. |
| `inputs.ts` | Sign-in form validates email required, email format, password required. |
| `useFormSignIn` | `error?.name.includes('NotAuthorizedException')` → `incorrect`. `error?.name.includes('PasswordResetRequiredException')` → `resetRequired`. `response?.nextStep.signInStep === 'CONFIRM_SIGN_UP'` → `confirmRequired`. `response?.nextStep.signInStep === 'CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED'` → `newPassword`. |
| Amplify v6 | Unconfirmed sign-in returns `nextStep.signInStep === 'CONFIRM_SIGN_UP'`. Wrong password and unknown email share ++NotAuthorizedException++ (user enumeration). |

++wrong password++ and ++unknown email++ share the incorrect-credentials Then. ++unconfirmed sign-in++ continues to Confirm Sign Up.

### Scenario: Sign in with already-registered account credentials

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
  *And* the Customer is not signed in
  *And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito authenticates the account and issues an ++account token++
*Then* My Paradise stores ++Cognito user++ ++signed-in Cognito user++
  *And* the Cognito user has the Mavenir customer id

### Scenario: Email format is unmet

*Given* the Customer has ++account credentials++ ++invalid email format++
*When* the Customer authenticates ++account credentials++ ++invalid email format++
*Then* My Paradise does not send a sign-in request to Cognito
  *And* the authentication is rejected
  *And* Cognito does not issue an ++account token++

### Scenario Outline: Authenticate with incorrect account credentials

| example | account credentials |
| --- | --- |
| wrong password | wrong password |
| unknown email | unknown email |

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
  *And* the Customer has ++account credentials++ {example}
*When* the Customer authenticates ++account credentials++ {example}
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++NotAuthorizedException++
*Then* the authentication is rejected
  *And* Cognito does not issue an ++account token++

### Scenario: Authenticate with unconfirmed account

*Given* Cognito has ++Cognito user++ ++unconfirmed Cognito user++
*When* the Customer authenticates ++account credentials++ ++unconfirmed sign-in++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++CONFIRM_SIGN_UP++
*Then* the authentication is rejected as unconfirmed
  *And* Cognito does not issue an ++account token++

### Scenario: Password reset required

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
  *And* Cognito requires a password reset for ++already-registered account credentials++
  *And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++PasswordResetRequiredException++
*Then* the authentication requires a password reset
  *And* Cognito does not issue an ++account token++

### Scenario: New password required

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
  *And* Cognito requires a new password for ++already-registered account credentials++
  *And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++
*Then* the authentication requires a new password
  *And* Cognito does not issue an ++account token++

**Flagged.** `/sign-in/new-password?complete=1` (`NewPassword.tsx`) is live code (`CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED` in `useFormSignIn`) but has no story on the Sign In With Existing Account map — map gap.
