---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Payment

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).  
++My Paradise customer++ load, including terminated billing, is on Create Customer (`stories/onboard-a-customer/create-customer/load_customer_story.spec.ts`). Seed a loaded customer as Given.

Payment iframe title and button copy (Time to add your payment, Complete your payment, Checkout, Pay $N and subscribe) is UX — stories assert payment authorization and payment status.

`payUpFront` and maximum payment attempts are Given preconditions on Enter Payment and Authorize Card. GrowthBook is application-layer and is not attached to Cart.

## Epic: Enter Payment

### Story: Enter Payment

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/Checkout/steps/Payment/Payment.tsx` · `pml-my/src/pages/Onboarding/pages/Checkout/steps/Payment/hooks/usePayment.tsx`
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `GET /customer/payment/auth` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `getPaymentIframe` · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/FACIframe.ts`
- Code: `pml-midtier` POST `ccsGateway/fac/cards/spi/auth`
- Granola: `.context/granola-notes/screenshot-wall.md` L64 · `19-payment-hpp.png`
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L537–L593

**Story type:** pml-my

#### Examples

##### payment authorization

| payment authorization | example | transactionId | totalAmount | salesChannel |
| --- | --- | --- | --- | --- |
| payment authorization | stub auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | 1 | ON-BOARDING |

#### Background

*Given* the Customer has completed order review and is on Checkout
  *And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario: Enter Payment

*Given* `payUpFront` is off
  *And* Mavenir CCS authorizes ++payment authorization++ ++stub auth++
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* My Paradise stores ++payment authorization++ ++stub auth++

#### Scenario: Pay upfront

*Given* `payUpFront` is on
  *And* the cart has ++plan++ ++Essentials++
  *And* Mavenir CCS authorizes ++payment authorization++ ++stub auth++
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* My Paradise stores ++payment authorization++ ++stub auth++

#### Scenario: Payment authorization fails to load

*Given* `payUpFront` is off
  *But* Mavenir CCS does not return a payment authorization
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a payment authorization
*Then* the payment authorization cannot be loaded

#### Scenario: FAC authorization timeout

*Given* `payUpFront` is off
  *But* Mavenir does not return a transaction id
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a transaction id
*Then* the payment authorization cannot be loaded

Billing account creation after a completed payment is Place Order (`createBilling`). This story does not place the order.

### Story: Evaluate Payment Flags

**Source**
- Code: `pml-my/src/config/flags.ts` (`PAY_UP_FRONT`, `PAYMENT_ATTEMPTS`) · `pml-my/src/pages/Onboarding/pages/Checkout/steps/Payment/Payment.tsx` · `pml-my/src/pages/Onboarding/pages/Checkout/steps/Payment/hooks/usePayment.tsx`

**Story type:** pml-my

`payUpFront` lives on Cart. Maximum payment attempts is a Given on Authorize Card. These are preconditions, not a GrowthBook operation.

| flag | Given | used by |
| --- | --- | --- |
| `payUpFront` off | Enter Payment | invoice authorization |
| `payUpFront` on | Pay upfront | upfront authorization |
| maximum payment attempts 3 | Card not verified / Maximum payment attempts | Authorize Card |

## Epic: Authorize Card

### Story: Authorize Card

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/Checkout/steps/Payment/hooks/usePayment.tsx` `getPaymentStatus`
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `GET /customer/payment/status/:transactionId` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `getPaymentStatus` / `checkPaymentStatus`
- Code: `pml-midtier` GET `ccsGateway/getTokenizedCard/{customerId}?transactionIdentifier=&salesChannel=ON-BOARDING`
- Code: `pml-midtier` `POST /customer/payment/failed` → Zendesk `cardAdditionFailed`
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L27
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L593–L632

**Story type:** pml-my

#### Examples

##### payment status

| payment status | example | transactionId | status | reason |
| --- | --- | --- | --- | --- |
| payment status | completed auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | completed | APPROVED |
| payment status | failed auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | failed | DECLINED |

#### Scenario: Payment completed

*Given* the Customer has ++payment authorization++ ++stub auth++
  *And* Mavenir CCS has ++payment status++ ++completed auth++
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
*When* Mavenir returns ++payment status++ ++completed auth++
*Then* the payment is authorized
  *And* the payment step does not place the order

#### Scenario: Card not verified

*Given* the Customer has ++payment authorization++ ++stub auth++
  *And* Mavenir CCS has ++payment status++ ++failed auth++
  *And* payment attempts are under the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir
*When* Mavenir returns ++payment status++ ++failed auth++
*Then* the card is not verified
  *And* My Paradise requests a fresh payment authorization from Mavenir

#### Scenario: Maximum payment attempts

*Given* the Customer has ++payment authorization++ ++stub auth++
  *And* Mavenir CCS has ++payment status++ ++failed auth++
  *And* payment attempts equal the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
*When* Mavenir returns ++payment status++ ++failed auth++
*Then* My Paradise records the failed card addition with Zendesk
  *And* the payment step does not place the order

## Epic: Provide Apple Pay Certificate

### Story: Provide Apple Pay Certificate

**Source**
- Code: `pml-midtier/src/entities/Apple/apple.routes.ts` `POST /apple/cert` · `pml-midtier/src/entities/Apple/controller.ts` `getCert`

**Story type:** pml-my

#### Examples

##### Apple Pay certificate

| Apple Pay certificate | example | keyIdentifier |
| --- | --- | --- |
| Apple Pay certificate | Bermuda Apple Pay cert | CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b |

#### Scenario: Provide Apple Pay certificate

*Given* the Apple Pay merchant certificate is available
*When* My Paradise provides the Apple Pay certificate
*Then* My Paradise sends the certificate request to Apple
*When* Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
*Then* My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++

## Epic: Adjust Credit

### Story: Adjust Credit Manually

**Source**
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L30–L36
- Granola: `.context/granola-notes/Inventorty and payment systems.md` L101
- Granola: `.context/granola-notes/weird-stuff.md` L18 · `19-payment-hpp.png`

**Story type:** Care

**Flagged** [Intended] — no automated code path; ambassadors manually adjust credit in Mavenir DEP after My Paradise checkout when pay-upfront or voucher credit was not applied automatically. Intended GWT stays in markdown only.

#### Scenario: Adjust credit for pay-upfront or voucher

*Given* the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++
  *And* the ++Mavenir customer++ has completed onboarding in My Paradise
  *But* the credit adjustment was not applied after checkout
*When* the Care agent manually adjusts the credit amount in Mavenir DEP
*Then* the ++Mavenir customer++ billing account is credited the adjustment amount
