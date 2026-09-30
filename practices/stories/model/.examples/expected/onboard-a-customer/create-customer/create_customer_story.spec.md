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

## Epic: Create Customer

### Story: Validate Mavenir Customer in Cognito User Attributes

**Story type:** pml-my

**Source**

- Code: `pml-my/src/pages/Protected/utils.ts`
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L32 · `onboarding-email-verification.png`
- Run: `.context/sandbox-walkthrough/live.log` L3222–L3225 (`GET /mv/customer` only — no `POST /mv/customer`)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                        | Note                                                                                                                                     |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `ensureCustomerExists` | Amplify `fetchUserAttributes`. Needs the browser ++account token++. If `custom:customerId` is present, return. No Midtier / Mavenir call. |
| `useLoggedUser` `loadUser`    | Runs `ensureCustomerExists` when Recoil `session.isLogged` is false, then `GET /mv/customer`.                                            |
| Activate                      | `ValidateEmail.tsx` Activate account `to='/onboarding'` → `Protected` mounts.                                                            |
| Sign in                       | `SignIn.tsx` Sign in `to='/my'` → `Protected` mounts.                                                                                    |
| Already signed in             | Cognito `getUser()` is set; Recoil `isLogged` is still false (refresh or first mount). Same `loadUser`.                                  |
| `useRedirectLoggedUser`       | If `getUser()` returns a user, navigate `/my`.                                                                                           |
| Sandbox `fetchUserAttributes` | Always returns `custom:customerId` = `cus_stub_pml_my_001`. Create path never runs.                                                      |
| Granola | Cognito exists before a ++Mavenir customer++. |


#### Background

*Given* the User is in Account Setup  
  *And* Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++

#### Scenario: Cognito User already has a Mavenir Customer id

*Given* the ++Cognito user++ has a ++Mavenir customer++ id  
*When* the User proceeds to Account Setup  
*Then* My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito  
  *And* My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++  
  *And* My Paradise proceeds to load the ++My Paradise customer++ from Midtier

#### Scenario: Cognito User has no Mavenir Customer id

*But* no ++Mavenir customer++ exists for those ++account credentials++  
*When* the User proceeds to Account Setup  
*Then* My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito  
  *And* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++

**Flagged.** Sandbox `fetchUserAttributes` always has a ++Mavenir customer++ id — the no-id scenario is live Amplify / Cognito.

### Story: Submit Create Customer Request to Mid-Tier

**Story type:** pml-my

**Source**

- Code: `pml-my/src/pages/Protected/utils.ts`
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L32 · `onboarding-email-verification.png`
- Run: `.context/sandbox-walkthrough/live.log` L3222–L3225 (`GET /mv/customer` only)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                         | Note                                                                                                                              |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `ensureCustomerExists`         | `POST` `env.midtier.mavenir.customer` with `getAuthorizationHeader()`. Then Store hop writes the id.                              |
| Snackbar                       | *Could not create customer.* when `request` returns `success: false` (any Axios error). My Paradise does not read status or body. |
| `getAuthorizationHeader` throw | `fetchAuthSession` failed. Catch logs only. No POST — no attributes to read without a session.                                    |
| Midtier 409                    | Mavenir email already has a customer (`isErrorActuallyConflict`).                                                                 |
| Midtier Invalid token          | Auth middleware.                                                                                                                  |
| Midtier 504                    | Mavenir has no HTTP response (`axiosHandleError`).                                                                                |
| Midtier other                  | Mavenir `code` / `errorCode` via `axiosHandleError`.                                                                              |


#### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id  
  *And* the browser session has an ++account token++

#### Scenario: Submit Create Customer Request to Mid-Tier

*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++  
*Then* My Paradise adds a ++Mavenir customer++ through the Midtier

#### Scenario: Email already has a Mavenir Customer

*Given* a ++Mavenir customer++ already exists for that email  
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++  
*Then* My Paradise shows *Could not create customer.*

#### Scenario: Invalid Account Token

*Given* the ++account token++ is invalid  
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++ 
*Then* My Paradise shows *Could not create customer.*

#### Scenario: Mavenir is unreachable

*Given* Mavenir has no HTTP response  
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++  
*Then* My Paradise shows *Could not create customer.*

**Flagged.** My Paradise shows the same snackbar for those Givens. Sandbox never POSTs.

### Story: Validate Cognito User

**Story type:** Midtier

**Source**

- Code: `pml-midtier/src/middlewares/Auth/auth.ts` · `pml-midtier/src/services/Cognito/cognito.service.ts`

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                         | Note                                                                                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Auth.getMiddleware`           | Reads `idtoken`. `CognitoService.validateToken`. Writes `credentials.email` and `credentials.customerId` from the decoded token (`custom:customerId`). |
| `CognitoService.validateToken` | `aws-jwt-verify` `CognitoJwtVerifier` (id token, user pool, client id) plus JWKS / `jsonwebtoken`. **Not Amplify.**                                    |
| Failure                        | `Err` `{ type: 'authorization', message: 'Invalid token' }`.                                                                                           |
| Sandbox midtier proxy          | GET/POST `/mv/customer` do not verify JWT.                                                                                                             |
| Create Customer POST           | Uses email from the token. GET Load Customer uses `customerId` from the token. Same middleware on both.                                                |


#### Background

*Given* the User has an ++account token++

#### Scenario: Validate Cognito User

*When* Midtier is asked to validate the ++account token++  
*Then* Midtier verifies the ++account token++  
  *And* Midtier reads the email from the ++account token++
*When* the ++account token++ is invalid  
*Then* Midtier returns "Invalid token"

**Flagged.** Sandbox proxy does not verify JWT. My Paradise `ensureCustomerExists` / `useLoggedUser` do not vary on Invalid token vs other failures.

### Story: Submit Create Mavenir Customer

**Story type:** Midtier

**Source**

- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts`
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L32 · `01-dep-base-customer.png`

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                                      | Note                                                                                                     |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `CustomerController.createCustomer` | `POST` Mavenir `createaccounts` with `createPayload(email)` from the ++account token++. Returns `{ id }`. |
| `createPayload`                             | email, `serviceProviderId` `100000000`, `source` `on-boarding`, contact medium email.                    |
| Conflict                                    | `isErrorActuallyConflict` (Mavenir status includes `409`) → Midtier `409`.                               |
| Sandbox `CustomerController.createCustomer` | Always `201` `{ id: STUB_CUSTOMER_ID }`. My proxy returns `200` `{ id }`.                                |


#### Background

*Given* Midtier has verified the ++account token++  
  *And* the ++account token++ has an email

#### Scenario: Submit Create Mavenir Customer

*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++  
*Then* Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)  
  *And* Midtier submits createaccounts to Mavenir  
  *And* Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id  
  *And* Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id  
  *And* Midtier returns the ++PML customer++ id

#### Scenario: Mavenir customer already exists

*Given* a ++Mavenir customer++ already exists for that email  
*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++  
*Then* Midtier receives a Mavenir createaccounts conflict  
  *And* Midtier maps that conflict to Paradise 409  
  *And* Midtier returns 409

#### Scenario: Mavenir is unreachable

*Given* Mavenir has no HTTP response  
*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++  
*Then* Midtier maps that missing response to Paradise 504  
  *And* Midtier returns 504

**Flagged.** Sandbox create always succeeds.

### Story: Create Customer

**Story type:** Mavenir

**Source**

- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/create.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L70–L73 · `01-dep-base-customer.png`; `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L32

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                          | Note                                                                                                                   |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Mavenir `POST …/createaccounts` | Creates the ++Mavenir customer++. Midtier returns `{ id: data.id }`. DEP labels it Account; we say ++Mavenir customer++. |
| `getAuthHeaders` | Midtier forwards the browser ++account token++ to Mavenir as `idtoken`. |
| Conflict                        | Mavenir status includes `409`.                                                                                         |
| Granola                         | CRM/DEP customer after Cognito confirm.                                                                                |


#### Background

*Given* no ++Mavenir customer++ for that email  
  *And* Mavenir has that ++account token++ on the create request

#### Scenario: Create Customer

*When* Mavenir is asked to create a ++Mavenir customer++ for that email  
*Then* Mavenir creates a ++Mavenir customer++  
  *And* Mavenir returns the ++Mavenir customer++ id

#### Scenario: Email already has a Mavenir Customer

*Given* Mavenir has a ++Mavenir customer++ for that email  
*When* Mavenir is asked to create a ++Mavenir customer++ for that email  
*Then* Mavenir returns a conflict

**Flagged.** Sandbox create always succeeds.

### Story: Store Mavenir Customer Id on Cognito User

**Story type:** pml-my

**Source**

- Code: `pml-my/src/pages/Protected/utils.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L88 · `onboarding-email-verification.png`

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                         | Note                                                                                            |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| `ensureCustomerExists`         | After POST succeeds, Amplify `updateUserAttributes` `{ 'custom:customerId': response.id }`.     |
| Sandbox `updateUserAttributes` | Writes stub `customerId`. Headed run never reaches this because attributes already have the id. |
| Cognito | Stores the attribute on the ++Cognito user++. Does not know Amplify. |


#### Background

*Given* My Paradise has added a ++Mavenir customer++ through the Midtier  
  *And* that add returned a ++Mavenir customer++ id

#### Scenario: Store Mavenir Customer Id on Cognito User

*When* My Paradise has a ++Mavenir customer++ id from the Midtier  
*Then* My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito  
  *And* My Paradise proceeds to load the ++My Paradise customer++ from Midtier

**Flagged.** Sandbox headed run never POSTs, so this hop does not run.
