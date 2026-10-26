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

## Epic: Load Customer

### Story: Load My Paradise Customer From Midtier And Store In Session

**Story type:** pml-my

**Source**

- Code: `pml-my/src/pages/Protected/hooks/useLoggedUser.ts`
- Run: `.context/sandbox-walkthrough/live.log` L3222–L3225 (`GET /mv/customer` 200); L13639–L13642 (`GET /mv/customer` 400)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                | Note                                                                                                                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `useLoggedUser`       | GET when `session.isLogged` is false (customer not in session). Protected mount: `/onboarding` or `/my`. Reload resets Recoil, so GET runs again. SPA stay with session already loaded skips GET. |
| Terminated            | `response.billing.state === 'terminated'` → `signOut` and terminated-account copy.                                                                                                                |
| GET fail              | `signOut` and *Something went wrong when loading your account*.                                                                                                                                   |
| Onboarding after load | `ensureCustomerFieldsExists` (create cart) is Create Empty Cart, not this hop.                                                                                                                    |
| Sandbox billing       | `state: 'active'`. Terminated is live Mavenir.                                                                                                                                                    |
| Auth                  | Same JWT middleware as Create Customer. Map places Validate Cognito User on Create Customer.                                                                                                      |


#### Background

*Given* the browser session has an ++account token++  
  *And* the ++Cognito user++ has a ++Mavenir customer++ id  
  *And* the ++My Paradise customer++ is not in session

#### Scenario: Load My Paradise Customer From Midtier And Store In Session

*When* the User proceeds to Account Setup or My Paradise  
*Then* My Paradise retrieves the ++Mavenir customer++ through the Midtier  
  *And* My Paradise stores the ++My Paradise customer++ in session

#### Scenario: Billing account is terminated

*Given* the ++Mavenir customer++ billing state is terminated  
*When* the User proceeds to Account Setup or My Paradise  
*Then* My Paradise signs the User out  
  *And* My Paradise shows the terminated-account message

#### Scenario: Load customer fails

*When* the User proceeds to Account Setup or My Paradise  
*Then* My Paradise signs the User out  
  *And* My Paradise shows *Something went wrong when loading your account*

**Flagged.** Sandbox fixture billing is `active`. Headed run L3222–L3225 is 200; L13639–L13642 is 400 later in the same log.

### Story: Get Mavenir Customer and Transform To My Paradise Customer And Return

**Story type:** Midtier

**Source**

- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` · `pml-midtier/src/entities/Mavenir/controllers/customer/utils/buildCustomer/buildCustomer.ts`
- Run: `.context/sandbox-walkthrough/live.log` L3222–L3225 (`GET /mv/customer` 200)

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                | Note                                                                                                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `getCustomer` | `getCustomerRequest` then `buildCustomer`. Paradise: ++identity++, ++address++, subscriptions, metadata, billing, cart. |
| `getCustomerRequest` | Mavenir `GET …/customerDetails/{id}` with ++Mavenir customer++ id on the ++account token++. |
| `buildCustomer` | Maps ++identity++ and ++address++ from contact medium / engaged party. Subscriptions when agreement exists. Billing when account exists. Cart via shoppingCart; none → `null`. |
| Create-time | No agreement → subscriptions none. No account → billing none. No cart → cart none. Email on ++identity++. |
| Sandbox `getCustomer` | Returns onboarding fixture (filled ++identity++ / ++address++, cart with plan). Not ++new PML customer++. |


++new Mavenir customer++ and ++new PML customer++ are in Examples on this file.

#### Background

*Given* Midtier has verified the ++account token++  
  *And* the ++account token++ has a ++Mavenir customer++ id  
  *And* Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)

#### Scenario: Get Mavenir Customer and Transform To My Paradise Customer And Return

*When* Midtier receives a Paradise request to get a ++PML customer++  
*Then* Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++  
  *And* Midtier submits customerDetails to Mavenir  
  *And* Midtier receives the ++Mavenir customer++ ++new Mavenir customer++  
  *And* Midtier maps that ++Mavenir customer++ to a new ++PML customer++  
  *And* Midtier returns the new ++PML customer++

**Flagged.** Sandbox GET returns a filled fixture, not ++new PML customer++. Live `getMetadata` `JSON.parse`s voucher; missing voucher is not this create-time row.

### Story: Get Mavenir Customer

**Story type:** Mavenir

**Source**

- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts`

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                               | Note                                                                                |
| ------------------------------------ | ----------------------------------------------------------------------------------- |
| Mavenir `GET …/customerDetails/{id}` | Returns the ++Mavenir customer++. Id is `custom:customerId` on the ++account token++. |
| Sandbox                              | Fixture customer. No Mavenir call.                                                  |


#### Background

*Given* Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)

#### Scenario: Get Mavenir Customer

*When* Mavenir is asked to get the ++Mavenir customer++  
*Then* Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++
