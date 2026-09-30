---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Verified Profile

Persona and Mavenir hops are `when`/`then` pairs inside Customer Complete Persona Kyc. Actor is **Customer**. Ambassador collection is the second map story.

## Domain terms

- ++Persona inquiry++ — KYC inquiry created by Persona on behalf of My Paradise. Domain record carries `inquiryId` and `verified`.
- ++Persona document++ — Persona government-ID document attached to a ++Persona inquiry++. Carries `expirationDate` after sanitisation.

## Examples

### Persona inquiry

| Persona inquiry | example | inquiryId | status | idNationality | idType | idNumber | expiryDate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Persona inquiry | completed Persona inquiry | inq_test_abc123456 | completed | Bermuda | Driver's License | I1234562 | 15/01/2030 |
| Persona inquiry | failed Persona inquiry | inq_test_xyz789012 | failed |  |  |  |  |

### Persona document

| Persona document | example | documentId | expirationDate |
| --- | --- | --- | --- |
| Persona document | valid Persona document | doc_test_abc123456 | 2030-01-15 |

### identity

| identity | example | name | lastName | preferredName | dateOfBirth | idNationality | idType | idNumber | expiryDate | otherPhoneNumber |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| identity | valid identity | JONATHAN | WICK | Jonathan | 02/09/1964 | Bermuda | Driver's License | I1234562 | 15/01/2030 | +44 1123 4567 |

### address

| address | example | street | complement | city | parish | postalCode | country |
| --- | --- | --- | --- | --- | --- | --- | --- |
| address | valid address | 82 Beaver St |  | New York | NY | NY 10005 | US |

### profile requirement

| profile requirement | example | field | requirement |
| --- | --- | --- | --- |
| profile requirement | name required | name | Please provide a name. |
| profile requirement | last name required | lastName | Please provide a last name. |
| profile requirement | date of birth required | dateOfBirth | Date of Birth is required |
| profile requirement | ID nationality required | idNationality | Please provide the nationality of your ID. |
| profile requirement | ID type required | idType | Please provide the type of your ID. |
| profile requirement | ID number required | idNumber | Please provide an ID Number. |
| profile requirement | expiry required | expiryDate | Please provide the document expiry date. |
| profile requirement | street required | street | An address is required. |
| profile requirement | parish required | parish | Parish is required. |
| profile requirement | postal code required | postalCode | Postal Code is required. |

---

## Story: Customer Complete Persona Kyc

Persona create/read-document and Mavenir patchProfile are hops inside this story.

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/Persona/PersonaPreload.tsx` L19–L22 (`personaRequired = !customer.identity.idNumber`; navigate to checkout when idNumber is present)
- Code: `pml-my/src/pages/Protected/hooks/useStepRedirect.ts`
- Code: `pml-my/src/pages/Onboarding/pages/Persona/PersonaIframe.tsx` L39–L63
- Code: `pml-my/src/pages/Onboarding/pages/Persona/useGetExpiryDate.ts` L8–L22
- Code: `pml-my/src/pages/Onboarding/pages/Profile/utils/mapPersonaData.ts`
- Code: `pml-my/src/pages/Onboarding/pages/Profile/Profile.tsx`
- Code: `pml-my/src/pages/Onboarding/pages/Profile/hooks/useFormUserData/useFormUserData.ts` `patchUserData`
- Code: `pml-midtier/src/entities/Persona/persona.controller.ts` `retrieveDocument`
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/patchAccount.ts` `patchAccountPayload`
- Granola: `.context/granola-notes/screenshot-wall.md` L52 Â· `12-verify-id-persona.png`
- Run: `.context/sandbox-walkthrough/walk-profile-kyc.md` L488–L875
- Run: `.context/sandbox-walkthrough/walk-profile-confirm.md` L84–L484

**Story type:** pml-my

#### Evidence

| Source | Note |
| --- | --- |
| `PersonaPreload` `personaRequired` | `!customer.identity.idNumber` — inquiry required when no ID number. |
| `PersonaPreload` routing | `if (personaPath && !personaRequired) { navigate('../onboarding/checkout') }` — forwards when idNumber exists. |
| Cart `missingOnboardingSteps` | `ProfileKyc` is listed when `!customer.identity.idNumber`; otherwise the next step is Checkout. |
| `PersonaIframe` `<Inquiry>` | Persona SDK pre-fills `emailAddress: customer.identity.email`. |
| `onComplete` | `verified: status === 'completed'`; then `getExpiryDate` and forward to profile. |
| `useGetExpiryDate` | Reads `current-government-id.value.id` and retrieves `{ data: { expirationDate } }`. Empty expiry when no government ID. |
| `mapPersonaData` | Maps Persona fields onto ++identity++ and ++address++. |
| `retrieveDocument` | Persona `GET /documents/:id?include=inquiry`; returns sanitised `expiration-date`. |
| `patchAccountPayload` | `givenName`, `familyName`, `birthDate`, `individualIdentification` (`identificationId`, `identificationType`), contact medium. |

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

#### Scenario: Persona verification required

*But* no idNumber on ++identity++
*When* the Customer validates whether a Persona inquiry is required
*Then* a Persona inquiry is required
  *And* the Customer is on the Profile KYC step

#### Scenario: Persona verification already complete

*Given* the Customer has ++identity++ with an idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* the Persona inquiry is already complete
  *And* the Customer is forwarded to Checkout

**Flagged.** Sandbox fixture always has idNumber — the required path is live Persona only.

#### Scenario: Create a completed Persona inquiry

*Given* the Customer has no idNumber on ++identity++
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
  *And* My Paradise retrieves the Persona document
*When* Persona returns ++Persona inquiry++ ++completed Persona inquiry++
*Then* the Customer has a verified ++Persona inquiry++
  *And* My Paradise maps the inquiry onto ++identity++ ++valid identity++ and ++address++ ++valid address++
  *And* Customer verified stays false until the Customer confirms their identity
*When* Persona returns ++Persona document++ ++valid Persona document++
*Then* ++identity++ expiry date is the ++Persona document++ expiration date

#### Scenario: Persona inquiry not completed

*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*When* Persona returns ++Persona inquiry++ ++failed Persona inquiry++
*Then* the Customer has an unverified ++Persona inquiry++
  *And* ++identity++ and ++address++ stay empty

#### Scenario: No government ID document on inquiry

*Given* the completed ++Persona inquiry++ has no government ID document
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
  *And* My Paradise does not retrieve a Persona document
*When* Persona returns the completed inquiry without a government ID
*Then* ++identity++ expiry date is empty

#### Scenario: Persona errors on inquiry load

*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*When* Persona returns an error
*Then* the Customer has an unverified ++Persona inquiry++
  *And* ++identity++ stays empty

#### Scenario: Document not found

**Flagged.** Sandbox does not call Persona.

*Given* Persona has no ++Persona document++ for that document ID
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns that the document is not found
*Then* ++identity++ expiry date is empty

#### Scenario: Document email mismatch

**Flagged.** Sandbox does not call Persona.

*Given* the ++Persona document++ email does not match the Customer email
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns unauthorized
*Then* ++identity++ expiry date is empty

#### Scenario: Verify later

*Given* the Customer has a ++My Paradise customer++ with no idNumber on ++identity++
*When* the Customer proceeds without a Persona inquiry
*Then* My Paradise does not send an inquiry request to Persona
  *And* no ++Persona inquiry++ is stored
  *And* the Customer is still on the Profile KYC step

**Flagged — Intended.** Sandbox skips the Persona screen (stub identity already has idNumber).

#### Scenario: Enter valid identity and address

*Given* the Customer has a ++My Paradise customer++ in session
*When* the Customer enters ++identity++ ++valid identity++ and ++address++ ++valid address++
*Then* all profile requirements are met
  *And* the Customer can confirm their identity

#### Scenario: Enter identity after a verified Persona inquiry

*Given* the Customer has a verified ++Persona inquiry++ mapped onto ++identity++ ++valid identity++
*When* the Customer enters the mapped ++identity++ and ++address++
*Then* all profile requirements are met
  *And* the ID fields are present on ++identity++

#### Scenario: Re-enter a verified identity

*Given* the Customer has ++identity++ ++valid identity++ already verified
*When* the Customer re-enters ++identity++ ++valid identity++
*Then* the identity is no longer verified
  *And* the Customer can confirm their identity again

#### Scenario Outline: Enter incomplete identity or address

*When* the Customer enters ++identity++ and ++address++ with {field} empty
*Then* {field} is missing
  *And* the Customer cannot confirm their identity

#### Scenario: Confirm identity with a verified Persona inquiry

*Given* the Customer has entered ++identity++ ++valid identity++ and ++address++ ++valid address++
  *And* the Customer has a verified ++Persona inquiry++
*When* the Customer confirms their identity
*Then* My Paradise maps ++identity++ and ++address++ onto the Mavenir engaged party and contact medium
  *And* My Paradise sends the profile patch to Mavenir
*When* Mavenir patches the customer
*Then* the Customer identity is persisted
  *And* the Customer is verified
  *And* the ++Persona inquiry++ is cleared

#### Scenario: Profile requirements unmet

*Given* the Customer has not entered ++identity++ or ++address++
*When* the Customer confirms their identity
*Then* the identity cannot be confirmed
  *And* My Paradise does not send a profile patch to Mavenir

#### Scenario: Customer already exists

*Given* another Mavenir customer already has ++identity++ idNumber I1234562
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
  *And* the identity cannot be confirmed because a customer with that information already exists

#### Scenario: Mavenir profile patch error

*Given* Mavenir returns a profile patch error
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
  *And* the identity cannot be confirmed

---

## Story: Collect Identity With Brand Amassador

Ambassador collection is off-system. Intended GWT only — skipped in the acceptance spec.

**Source**
- Granola: `.context/granola-notes/screenshot-wall.md` L54 Â· `14-verify-options-ambassador.png`
- Run: `.context/sandbox-walkthrough/walk-profile-kyc.md` L663–L755

#### Scenario: Collect identity with Brand Ambassador

*Given* the Customer is choosing how to verify their ID
*When* the Customer asks a Brand Ambassador to verify their ID
*Then* the Ambassador will be in touch to proceed with verification
  *And* the Ambassador collects the Customer's ++identity++ documents over WhatsApp
  *And* the Customer proceeds to enter identity in My Paradise

**Flagged — Intended.** WhatsApp collection is a manual off-system process. Sandbox Contact me navigates to `/my`.

**Flagged.** No Mavenir shopping-cart `verified` characteristic in Get Verified Profile. Place Order `submitOrderFlag` is a different hop.
