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

## Epic: Support Account Creation

### Story: Fix Orphan Cognito Account

**Story type:** Care

**Source**

- Granola: `.context/granola-notes/weird-stuff.md` L15 · `onboarding-email-verification.png`; `.context/granola-notes/subcription data review` L47–L54; `.context/granola-notes/screenshot-wall.md` L88

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                                             | Note                                                                                                                                                                                                                 |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Granola `subcription data review` L47–L54 | Abandon My Paradise onboarding **before activation** → ++Cognito user++ exists, not linked to an MDE ++Mavenir customer++. Workaround: change email in MDE. No clean delete once activated. Backlog: Cognito↔MDE bind. |
| Granola `weird-stuff.md` L15 · screenshot-wall L88 | Same row. Capture is the Check your email screen.                                                                                                                                                                    |
| Code                                               | No Care / DEP UI in `pml-my` or `pml-midtier`.                                                                                                                                                                       |


#### Background

*Given* the User has clicked Create account with ++account credentials++ ++valid account credentials++  
  *And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++  
  *But* the User has not entered a ++validation code++  
  *And* no ++account token++ is issued

#### Scenario: Fix Orphan Cognito Account

*When* Care is asked to fix the orphan ++Cognito user++  
*Then* Care changes the email in Mavenir DEP  
  *And* Care does not delete the ++Cognito user++

**Flagged.** Granola-only. Workaround is change email in Mavenir DEP. Intended backlog is bind Cognito to Mavenir DEP. No delete after activate. No Care UI in our repos.

### Story: Read False Initial Activation

**Story type:** Care

**Source**

- Granola: `.context/granola-notes/weird-stuff.md` L14 · `01-dep-base-customer.png`; `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L25–L33; `.context/granola-notes/screenshot-wall.md` L87

**Sources / context:** `stories/system-story-strategy.md`, `stories/system-terms.md`, `stories/.context/create-customer-chat-notes.md`

#### Evidence


| Source                          | Note                                                                                                        |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Granola onboarding-flow L32–L33 | Cart before billing → DEP shows Initial Activation. Correct order: customer → billing + card → then orders. |
| `01-dep-base-customer.png`      | DEP customer / account tabs.                                                                                |
| Code                            | Create Empty Cart is a later epic. This hop is Care reading DEP.                                            |


#### Background

*Given* Mavenir has a ++Mavenir customer++  
  *And* that ++Mavenir customer++ has a ++Mavenir shopping cart++  
  *But* that ++Mavenir customer++ has no ++billing account++

#### Scenario: Read False Initial Activation

*When* Care is asked to read the ++Mavenir customer++ in DEP  
*Then* Care sees Initial Activation

**Flagged.** Granola-only. No Care UI in our repos

### Story: Ensure Cart on Customer

**Story type:** pml-my
