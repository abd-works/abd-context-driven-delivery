---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Examples

### Cognito user


| Cognito user | example | account credentials | example | confirmed | account token | Mavenir customer id |
| --- | --- | --- | --- | --- | --- | --- |
| Cognito user | unconfirmed Cognito user | account credentials | valid account credentials | no | none | none |
| Cognito user | confirmed Cognito user | account credentials | valid account credentials | yes | none | none |
| Cognito user | Cognito user with account token | account credentials | valid account credentials | yes | issued | none |


### Mavenir customer

Stored on Mavenir after createaccounts. **new Mavenir customer** is the almost-empty create-time customer. Later stories add rows.


| Mavenir customer | example | id | agreement | account | shopping cart |
| --- | --- | --- | --- | --- | --- |
| Mavenir customer | new Mavenir customer | from createaccounts | none | none | none |


#### Contact medium

How Mavenir reaches the customer: email, phone, and street on the contact characteristic. Midtier reads email and address from the customer’s contact medium.


| Mavenir customer | example | emailAddress | phoneNumber | street1 | street2 | city | stateOrProvince | postCode | country |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mavenir customer | new Mavenir customer | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | | | | | | | |


#### Engaged party

The person on a Consumer Mavenir customer: names, birth date, identification. Empty at create.


| Mavenir customer | example | givenName | familyName | preferredGivenName | birthDate | identification |
| --- | --- | --- | --- | --- | --- | --- |
| Mavenir customer | new Mavenir customer | | | | | none |


### PML customer

Paradise response after Midtier maps new Mavenir customer. Session form is My Paradise customer.


| PML customer | example | subscriptions | billing | cart | metadata id | verified |
| --- | --- | --- | --- | --- | --- | --- |
| PML customer | new PML customer | none | none | none | new Mavenir customer id | no |


#### Identity


| PML customer | example | email | name | lastName | fullName | preferredName | dateOfBirth | expiryDate | idNationality | idNumber | idType | otherPhoneNumber |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PML customer | new PML customer | [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com) | | | | | | | | | | |


#### Address

Empty address on the PML customer at create. Midtier still returns the address object.


| PML customer | example | street | complement | city | parish | postalCode | country |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PML customer | new PML customer | | | | | | |

## Epic: Verify Account

### Story: Enter Validation Code

**Story type:** pml-my

**Source**

- Code: `pml-my/src/pages/ValidateEmail/ValidateEmail.tsx`
- Granola: `.context/granola-notes/screenshot-wall.md` L21–L26 · `onboarding-email-verification.png`; `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L29
- Run: `.context/sandbox-walkthrough/live.log` L3218–L3219 (`/validate-email`)

++account credentials++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Examples

##### validation code


| validation code | example | code |
| --- | --- | --- |
| validation code | valid validation code | 123456 |
| validation code | mismatch validation code | 000000 |
| validation code | expired validation code | 111111 |
| validation code | attempts exceeded validation code | 222222 |



| validation code | example | helper |
| --- | --- | --- |
| validation code | mismatch validation code | Hmm. That code didn't work. |
| validation code | expired validation code | Hmm. That code didn't work. |
| validation code | attempts exceeded validation code | Attempts limit exceeded. Please try again later. |


**Intended:** mismatch and expired share *Hmm. That code didn't work.* Live sandbox `confirmSignUp` currently accepts any code.

#### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++  
  *And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

#### Scenario: Enter validation code

*When* the User proceeds to check their email  
*Then* the User sees the code was sent to *[Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com)*  
  *And* the User can enter a ++validation code++ in Enter Validation Code  
  *And* the User can Resend  
  *And* the User can Close  
  *And* the Activate account operation is disabled  
*When* the User enters a ++validation code++ ++valid validation code++  
*Then* the Activate account operation is enabled  
*When* the User clicks Activate account  
*Then* the system confirms the ++Cognito user++ routing through Amplify to Cognito  
  *And* the User is forwarded to onboarding

#### Scenario Outline: Activate with unusable validation code

##### Steps

*When* the User clicks Activate account with ++validation code++ {scenario}  
*Then* Enter Validation Code shows helper text {helper}

#### Scenario: Resend validation code

*When* the User clicks Resend  
*Then* the system emails a new ++validation code++ routing through Amplify to Cognito  
  *And* the User sees *We sent you a new code. Please check your email.*  
  *And* Resend waits 60 seconds before it can be used again

### Story: Confirm Cognito User

**Story type:** Cognito

**Source**

- Code: `pml-my/src/services/aws/cognito.ts` · `pml-my/src/pages/ValidateEmail/useFormActivateAccount.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L21–L26 · `onboarding-email-verification.png`; `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L29
- Run: `.context/sandbox-walkthrough/live.log` L3218–L3226 (`/validate-email` → `/my` → `GET /mv/customer` → `/onboarding`)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                                              | Note                                                                                                                                         |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `useFormActivateAccount`                            | After Activate, `confirmSignUp` then `signIn`. Confirm is this hop; tokens are Issue Account Token.                                          |
| `cognito.ts` `confirmSignUp`                        | Amplify `confirmSignUp` with username = email and `confirmationCode`. No midtier URL.                                                        |
| `ValidateEmail.tsx`                                 | Maps `ExpiredCode` and `CodeMismatch` to *Hmm. That code didn't work.* `exceeded` → *Attempts limit exceeded. Please try again later.*       |
| Sandbox `cognito.stub.ts` `confirmSignUp`           | Accepts any code. Sets `currentEmail` (session) without `signIn`.                                                                            |
| AWS Cognito `confirmSignUp`                         | `CodeMismatchException`, `ExpiredCodeException`, `LimitExceededException`.                                                                   |
| Midtier `POST /cognito/signup`                      | Not on this path.                                                                                                                            |
| `.context/sandbox-walkthrough/live.log` L3218–L3226 | Headed run NAV `/validate-email` then `/my` without an Activate click (`useRedirectLoggedUser` + stub `getUser`). Confirm was not exercised. |


++validation code++ examples are on Enter Validation Code.

#### Examples


| validation code | example | error |
| --- | --- | --- |
| validation code | mismatch validation code | CodeMismatchException |
| validation code | expired validation code | ExpiredCodeException |
| validation code | attempts exceeded validation code | LimitExceededException |


#### Background

*Given* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

#### Scenario: Confirm Cognito User

*When* Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++  
*Then* Cognito confirms the ++Cognito user++  
  *But* no ++account token++ is issued  
  *But* no ++Mavenir customer++ exists for those ++account credentials++

#### Scenario Outline: Confirm with unusable validation code

##### Steps

*When* Cognito is asked to confirm the user with ++validation code++ {scenario}  
*Then* Cognito returns {error}  
  *And* Cognito does not confirm the ++Cognito user++

**Flagged.** Sandbox `confirmSignUp` accepts any code — those exceptions are live Cognito / Amplify, not the stub.

### Story: Issue Account Token To Browser Session

**Story type:** Cognito

**Source**

- Code: `pml-my/src/pages/ValidateEmail/useFormActivateAccount.ts` · `pml-my/src/services/aws/cognito.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L21–L26 · `onboarding-email-verification.png`
- Run: `.context/sandbox-walkthrough/live.log` L3218–L3226

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                                    | Note                                                                                |
| ----------------------------------------- | ----------------------------------------------------------------------------------- |
| `useFormActivateAccount`                  | After `confirmSignUp` succeeds, `signIn(account)` with Recoil email and password.   |
| `cognito.ts` `signIn`                     | Amplify `signIn` with username = email.                                             |
| `cognito.ts` `getAuthorizationHeader`     | Amplify `fetchAuthSession({ forceRefresh: true })` for later Midtier `idtoken`.     |
| Sandbox `cognito.stub.ts` `confirmSignUp` | Sets `currentEmail` on confirm, so `getUser` is already signed in without `signIn`. |
| Sandbox `signIn`                          | Sets `currentEmail`. Always succeeds.                                               |
| Midtier                                   | Not on this path. Tokens are Cognito via Amplify.                                   |


++account credentials++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Background

*Given* Cognito has a ++Cognito user++ ++confirmed Cognito user++

#### Scenario: Issue Account Token To Browser Session

*When* Cognito is asked to authenticate ++account credentials++ ++valid account credentials++  
*Then* Cognito issues an ++account token++ for the ++Cognito user++  
  *But* no ++Mavenir customer++ exists for those ++account credentials++

**Flagged.** Sandbox `confirmSignUp` already leaves a session, so this hop is skipped on the headed run. Unconfirmed `signIn` (UserNotConfirmedException) is Sign In With Existing Account.
