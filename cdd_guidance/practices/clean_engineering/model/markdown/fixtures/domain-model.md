---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Bounded Context Model — Paradise Mobile (pml-web)

**Sources / context:** `src/.context/bounded-context-map.md` (read in full); story map `tests/story-map.md`; scenarios `tests/onboard-a-customer/*/*_story.test.md`, `tests/access-my-paradise/*_story.test.md`, `tests/serve-a-subscriber/*/*_story.test.md`; code under `src/<context>/<aggregate>/`. pml-my (`pml-my/src/pages/`) is the reference for public behaviour.

**Extends:** `practices/clean_engineering/templates/class-model.md` — `+` constructor · `------` properties · `----` operations. Every class carries a tactical stereotype.

**Built up epic by epic.** This document grows as each self-care sub-epic is modelled. Sections name what each epic adds; classes already in code are modelled as they are, so the model and the code describe one design. Diagrams: each aggregate's `<aggregate>.drawio` shows the same classes, operations, and relationships.

| Epic | Adds |
|---|---|
| Onboard a Customer | the onboarding aggregates: `AccountCredentials`, `CustomerProfile`, `KycInquiry`, `Plan`, `NumberInventory`, `Portability`, `Sim`, `Onboarding` on the `Subscription`, `Payment`, `AppliedVoucher`, `BillingAccount`, `ProductOrder` |
| Access Selfcare | `AccountCredentials`: temporary password and new password (`PasswordReset`, `TemporaryPassword`); `CustomerProfile`: saving updates (`saveUpdates`, `Identity.withContactDetails`, `Address.missingRequirements`); My Paradise: a completed customer's destination is the dashboard |
| Use My Account | `CustomerProfile`: sending a support request (`sendSupportRequest`, `SupportTicket`); `Subscription`: data usage (`SubscriptionUsage`, `DataAllowance`); `BillingAccount`: the current balance |
| Change My Service | `Subscription`: changing the active line's plan (`changePlan`, the 31-day downgrade wait from `planOrderedOn`) and a port request onto it (`requestLinePortability`); `Plan.oneYear` |
| Pay My Bill | `BillingAccount`: invoices, received payments, saved cards (`Invoice`, `ReceivedPayment`, `PaymentMethod`, `EnteredCard`); `payNow`, `enterNewPaymentMethod`, `chooseDefaultCard`, `removeSavedCard`; `PaymentGateway.charge` (was `chargeUpFront`) |

---

## Customer | custom

**Module:** `src/customer`

> // seam: who the customer is and how they sign in — credentials, profile, and identity check
> // constraint: reach a profile through its signed-in account; change a profile only through its operations

### AccountCredentials

AccountCredentials — the email and password a customer signs in with, and the session token

```
Integrations:
  - → Auth System · Account
    pattern: Anticorruption Layer
    crosses: credentials, validation codes, session tokens, temporary passwords
    integration: CredentialsRepositoryNode (local store stands in for the Auth System)
```

#### **AccountCredentials** <<Aggregate Root>> <<Entity>>

+ AccountCredentials(repository: CredentialsRepository)
------
+ email: string — identity
+ password: string
+ confirmPassword: string
+ requirements: AccountCredentialRequirements
+ token: CredentialsToken | null
+ << composition >> validation: CredentialsValidation
+ << composition >> passwordReset: PasswordReset — *Access Selfcare*
+ isLoggedIn: boolean
+ newPasswordRequired: boolean — *Access Selfcare*; true while a sign-in with a temporary password waits for a new password
----
+ register(): AccountCredentials
	-> CredentialsRepository.create(this)
	-> validation.emailValidationCode()
+ authenticateCredentials(): AccountCredentials
	-> CredentialsRepository.load(this)
	-> passwordReset.matches(password) — *Access Selfcare*: a temporary password asks for a new password instead of issuing a token
+ requestTemporaryPassword(): AccountCredentials — *Access Selfcare*
	-> CredentialsRepository.load(this)
	-> passwordReset.send()
	-> CredentialsRepository.update(stored)
+ setNewPassword(): AccountCredentials — *Access Selfcare*; uses `password` and `confirmPassword` already entered
	-> missingRequirements()
	-> passwordReset.clear()
	-> CredentialsRepository.update(this)
+ signOut(): void
	-> CredentialsRepository.update(this)
+ missingRequirements(): AccountCredentialRequirement[]

**Invariants**

- A token is issued only to a verified account with no new password pending.
- A temporary password signs in once: setting the new password clears it.
- A new password meets the same requirements as registering (letters, number, symbol, length, confirmed).
- `signOut` always leaves the account without a token.

#### **CredentialsValidation** <<Entity>>

+ CredentialsValidation(accountCredentials: AccountCredentials)
------
+ verified: boolean
+ validationCodeWasSent: boolean
+ canActivate: boolean
----
+ emailValidationCode(): void
+ verify(validationCode: ValidationCode): CredentialsValidation
+ resendValidationCode(): void

#### **PasswordReset** <<Entity>> — *Access Selfcare*

+ PasswordReset(accountCredentials: AccountCredentials)
------
+ << composition >> sent: TemporaryPassword[] — the temporary passwords emailed, latest last
+ newPasswordRequired: boolean
----
+ send(): TemporaryPassword — issues a temporary password and emails it to the account's email
+ matches(password: string): boolean — true for the latest unexpired temporary password
+ requireNewPassword(): void
+ clear(): void

**Invariants**

- Only the latest temporary password matches.
- After `clear`, nothing matches and no new password is required.

#### **CredentialsRepository** <<Repository>>

+ CredentialsRepository()
------
+ << aggregation >> accounts: Collection<AccountCredentials>
----
+ new(): AccountCredentials
+ create(accountCredentials: AccountCredentials): AccountCredentials
+ load(accountCredentials: AccountCredentials): AccountCredentials | null
+ update(accountCredentials: AccountCredentials): AccountCredentials

**LERN tiers** (`credentials.drawio`): `CredentialsRepositoryNode` (`credentials.json`), `AccountCredentialsNode`, `AccountCredentialsClient`, `createCredentialsRoutes`; screens `CreateCredentialsView`, `EnterValidationCodeView`, `SignInWithExistingCredentialsView`, and for Access Selfcare `ResetPasswordView` and `SetNewPasswordView`.

---

## Inventory | custom

**Module:** `src/inventory`

> // seam: what can be sold and assigned to a line — catalog plans, MSISDNs, port-ins, and SIMs
> // constraint: the Subscription records each choice on the cart through its own route; nothing in Inventory imports the Subscription

### Plan

#### **Plan** <<Aggregate Root>> <<Entity>>

+ Plan(id: string, name: string, price: number, isSellable: boolean, tag: string | null, features: PlanFeature[])
------
+ id: string — identity
+ name: string
+ price: number
+ tag: string | null — the label its catalog card shows
+ isSellable: boolean — the catalog offers it
+ << composition >> features: PlanFeature[] — View Services lists them under My plan
+ oneYear: boolean — *Change My Service*; a one-year promotional plan ("1Y" in its name), on which a port request asks for a paid plan first
+ roaming: boolean — ordering it opens a roaming ticket

#### **PlanFeature** <<Value Object>>

+ PlanFeature(kind: data | calling | texting, lines: string[])

#### **PlanRepository** <<Repository>>

+ << aggregation >> plans: Collection<Plan> — the catalog
----
+ list(): Plan[] — the sellable plans
+ load(id: string): Plan | null — a sellable plan; an unsellable plan stays in the collection but is never offered

**LERN tiers** (`plans.drawio`): `PlanRepositoryNode` (`plans.json`), `PlanNode`, `PlanClient`, `createPlanRoutes`; `PlanCardView`, `PlanFeaturesView`, `PlanCarouselView`.

### Payment Gateway (in-repo, existing)

#### **PaymentGateway** <<External System>>

Existing in-repo stand-in from onboarding; Pay My Bill reuses it and adds no other.

+ authorize(customerProfile): CardAuthorization | Error
+ status(transactionId): PaymentStatus | Error
+ charge(customerProfile): boolean — *Pay My Bill*; renamed from `chargeUpFront`, which the order's pay-up-front and Pay now both use; false when declined

**LERN tiers:** `OnboardingClient.usage` and the subscription state route carry usage; `BillingAccountClient.load` and a billing-account route carry the balance, and Pay My Bill adds the pay-now, payment-methods, default-card, and remove-card routes on the same billing routes; `UsageView` (`src/revenue/subscription`) and `MyBillsView` (`src/revenue/billing`) paint them, and the self-care frame composes them with `GreetingView` on the dashboard.

---

## My Paradise | custom (epic-wide navigation, not an aggregate)

**Module:** `src/my-paradise`

Not a domain type, so no class block here. Its destination rule, which Access Selfcare extends:

- A signed-in completed customer (`CustomerProfile.done`) goes to the dashboard, `/my`.
- A visitor with no session goes to Sign In, except on landing pages. Sign In, Reset Password, and Set New Password are landing pages.

---

## Event map

| Event | Emitted by | Operation | Consumed by |
|-------|------------|-----------|-------------|
| — | — | — | No domain events cross an aggregate: cross-aggregate work runs in one request on the owner's route. |
