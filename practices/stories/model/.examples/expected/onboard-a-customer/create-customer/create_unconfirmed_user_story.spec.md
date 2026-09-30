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

## Epic: Create Unconfirmed User

### Story: Enter Account Credentials

**Story type:** pml-my

**Source**

- Code: `pml-my/src/pages/SignUp/steps/CreateAccount/hooks/useFormSignUp.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L21–L26 · `onboarding-email-verification.png`
- Run: `.context/sandbox-walkthrough/live.log` L2–L3217 (`/sign-up/`)

#### Examples

##### Account credential requirements


| account credential requirements | example | field | requirement |
| --- | --- | --- | --- |
| account credential requirements | email required | email | Email is required |
| account credential requirements | email format | email | Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com) |
| account credential requirements | password letters | password | Password must contain uppercase and lowercase letters |
| account credential requirements | password number | password | Password must have at least one number |
| account credential requirements | password symbol | password | Password must have at least one symbol |
| account credential requirements | password length | password | Length must be greater than 8 characters |
| account credential requirements | confirm required | confirmPassword | Confirm Password is required |
| account credential requirements | confirm mismatch | confirmPassword | Passwords don't match |


**Intended:** displayed requirements in black, including Email is required. Live Create Account currently leaves the email helper empty on display.

Account credentials examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).


| account credentials | example | unmet | Create account |
| --- | --- | --- | --- |
| account credentials | valid account credentials | | enabled |
| account credentials | Paradise Mobile account credentials | | enabled |
| account credentials | invalid password letters | Password must contain uppercase and lowercase letters | disabled |
| account credentials | invalid password number | Password must have at least one number | disabled |
| account credentials | invalid password symbol | Password must have at least one symbol | disabled |
| account credentials | invalid password length | Length must be greater than 8 characters | disabled |
| account credentials | invalid confirm required | Confirm Password is required | disabled |
| account credentials | invalid confirm mismatch | Passwords don't match | disabled |
| account credentials | invalid email required | Email is required | disabled |
| account credentials | invalid email format | Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com) | disabled |


#### Background

*Given* the plan catalog contains purchasable plans  
  *And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

#### Scenario Outline: Enter new account credentials

##### Steps

*When* the User proceeds to create an account from the Paradise Mobile website  
*Then* the User can enter ++account credentials++  
  *And* ++account credential requirements++ are shown in black (Email is required, password rules)  
  *And* the Create account operation is disabled  
  *And* the User can Sign in  
  *And* the User can go Back  
  *And* the User can open Service Agreement, Terms and Conditions, and Privacy Policy  
*When* the User validates ++account credentials++ {example}  
*Then* ++account credentials++ are validated continuously as the User types  
  *And* unmet ++account credential requirements++ {unmet} are red with ✖  
  *And* the Create account button is {Create account}  
*When* the User clicks on Create account  
*Then* the system creates an unconfirmed Cognito user routing through Amplify to Cognito  
  *And* the User is forwarded to check their email

#### Scenario: Paradise Mobile email

**Intended:** title goes blue when a `@paradisemobile.com` email is entered (++account credentials++ · ++Paradise Mobile account credentials++).

*When* the User enters ++account credentials++ ++Paradise Mobile account credentials++  
*Then* the Create Account title is blue

#### Scenario: Email already registered

*Given* ++account credentials++ ++already-registered account credentials++ are already registered  
*When* the User registers ++account credentials++ ++already-registered account credentials++  
  *Then* Email shows the already-registered error

### Story: Create Unconfirmed Cognito User

**Story type:** Cognito

**Source**

- Code: `pml-my/src/services/aws/cognito.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L21–L26 · `onboarding-email-verification.png`; `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L33
- Run: `.context/sandbox-walkthrough/live.log` L3216–L3218 (`/sign-up/` click Create account → `/validate-email`)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                                                                                                               | Note                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `pml-my/src/pages/SignUp/steps/CreateAccount/hooks/useFormSignUp.ts`                                                 | My Paradise `signUp` → Amplify. No midtier URL.                                                      |
| `pml-my/src/services/aws/cognito.ts` `signUp`                                                                        | Cognito `Auth.signUp` with email attributes.                                                         |
| Sandbox `cognito.stub.ts` `signUp` | Always succeeds (`CONFIRM_SIGN_UP`). Does not throw ++UsernameExistsException++. |
| `useFormSignUp` `usernameExists`                                                                                     | Maps `error.name` containing `UsernameExists` to the email helper.                                   |
| `Form.tsx` / `inputs.ts`                                                                                             | Copy *Email is already registered.* Other Amplify errors stay on `errors.request` and are not shown. |
| AWS Cognito `signUp`                                                                                                 | `UsernameExistsException` when the username is already in the pool.                                  |
| Midtier `POST /cognito/signup`                                                                                       | Exists; requires voucher. Create Account does not call it.                                           |
| `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L33 · `onboarding-email-verification.png` | Cognito exists before a ++Mavenir customer++. |
| `.context/sandbox-walkthrough/live.log` L3216–L3218                                                                  | Click **Create account** (`disabled: false`) → NAV `/validate-email`.                                |


Account credentials examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++

#### Scenario: Create Unconfirmed Cognito User

*When* Cognito is asked to register ++account credentials++ ++valid account credentials++  
*Then* Cognito creates ++Cognito user++ ++unconfirmed Cognito user++  
  *And* Cognito emails a ++validation code++ for those ++account credentials++  
  *But* no ++account token++ is issued  
  *But* no ++Mavenir customer++ exists for those ++account credentials++

#### Scenario: Email already registered in Cognito

*Given* ++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++  
*When* Cognito is asked to register ++account credentials++ ++already-registered account credentials++  
*Then* Cognito returns ++UsernameExistsException++  
  *And* Cognito does not create another ++Cognito user++ for those ++account credentials++

**Flagged.** Sandbox `signUp` always succeeds — UsernameExistsException is live Cognito / Amplify, not the stub.

#### Scenario: Cognito register fails with another error

**Flagged.** Amplify can fail with names other than UsernameExistsException. My Paradise only maps `error.name` containing `UsernameExists`. Other errors sit on `errors.request`; Create Account does not show them.
