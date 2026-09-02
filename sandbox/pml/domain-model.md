---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

<!-- Sources / context: `pml-domain/domain` (interfaces; adapters `*.e2e.ts` / `*.http.ts` sit beside them) -->
# Customer — abstract base

Abstract base extended by both **Prospect** and **Subscriber**. Stories never interact with Customer directly.

## **Customer** <<Abstract>> <<Entity>>

+ Customer(...)
------
+ id: string
+ << composition >> identity: Identity
+ << composition >> address: Address
+ << composition >> accountCredentials: AccountCredentials | null
+ kycVerified: boolean

## **Identity** <<Entity>>

+ Identity(...)
------
+ email: string
+ name: string
+ lastName: string
+ fullName: string
+ preferredName: string
+ expiryDate: string
+ dateOfBirth: string
+ idNationality: string
+ idNumber: string
+ idType: string
+ otherPhoneNumber: string

## **Address** <<Entity>>

+ Address(...)
------
+ street: string
+ complement: string
+ city: string
+ parish: string
+ postalCode: string
+ country: string

## **AccountCredentials**

Customer credentials — form values, validation, and session operations. Set properties, then `validate()` or a commit (`register` / `signIn` / `verifyEmail`). Format errors live under `errors`; `canSubmit` is false until `validate()` has been called.

+ AccountCredentials(...)
------
+ email: string
+ password: string
+ confirmPassword: string
+ verificationCode: string
+ << composition >> errors: AccountCredentialsErrors
+ canSubmit: boolean
+ federatedSignInOptions: string[]
+ passwordResetConfirmation: string | null
+ resendMessage: string | null
----
+ validate(): void
+ register(): void
+ verifyEmail(): void
+ resendVerificationCode(): void
+ signIn(): void
+ loadSignIn(): void
+ signOut(): void
+ requestPasswordReset(): void
+ resetPassword(): void

## **AccountCredentialsErrors**

+ AccountCredentialsErrors(...)
------
+ email: string | null
+ password: PasswordRuleStatus[]
+ confirmPassword: string | null
+ verificationCode: string | null
+ register: string | null
+ signIn: string | null

## **PasswordRuleStatus**

+ PasswordRuleStatus(...)
------
+ rule: string
+ met: boolean
+ indicator: 'pending' | 'met' | 'unmet'

## **AccountCredentialsRepository** <<Repository>>

+ AccountCredentialsRepository(...)
------
+ << aggregation >> accountCredentials: AccountCredentials
----
+ load(): AccountCredentials


# Plan — catalog

Sellable plans selected during onboarding and referenced by subscription bundles.

## **Plan** <<Aggregate Root>> <<Entity>>

+ Plan(...)
------
+ id: string
+ name: string
+ description: string
+ price: number
+ fees: number
+ totalPrice: number
+ << composition >> features: Feature[]
+ isSellable: boolean

## **Feature**

+ Feature(...)
------
+ text: string[]
+ icon: string

## **PlanFilter**

+ PlanFilter(...)
------
+ isSellable: boolean

## **Collection** <<type>>

Keyed read-only collection shape for repository/catalog surfaces.

+ Collection(...)
------
----
+ get(key: string): T | undefined
+ has(key: string): boolean
+ keys(): string[]
+ values(): T[]

### Catalog page `plan/catalog/` — browse/select surface

## **CatalogPage**

+ CatalogPage(...)
------
----
+ select(plan: Plan): AccountCredentials
+ clearSelection(): void

## **PlanRepository** <<Repository>>

+ PlanRepository(...)
------
----
+ seed(items: Plan[]): void
+ getPlans(): Collection<Plan>
+ getAvailablePlans(): Collection<Plan>
+ findAvailable(filter: PlanFilter): Plan[]
+ findById(planId: string): Plan


# Prospect — onboarding

A customer during onboarding — from account creation through checkout.

## **Prospect** <<Aggregate Root>> <<Entity>> extends Customer

+ Prospect(...)
------
+ << association >> paymentMethod: PaymentMethod | null
+ << composition >> cart: Cart
+ << association >> verification: IdentityVerification | null
+ << association >> profile: KycProfile | null
+ verificationFailure: string | null
+ << association >> onboardingStep: OnboardingStep
----
+ isAtOnboardingStep(step: OnboardingStep): boolean
+ verifyIdentity(): IdentityVerification
+ submitKycProfile(): void

## **Voucher**

+ Voucher(...)
------
+ code: string

## **ProspectRepository** <<Repository>>

+ ProspectRepository(...)
------
+ << aggregation >> prospect: Prospect
----
+ load(accountCredentials: AccountCredentials): Prospect
+ seed(fixture: ProspectSeed): Prospect
+ save(prospect: Prospect): void

## **MsisdnInventory** <<Domain Service>>

Cart.loadAvailableNumbers, submitNumber, and submitPort delegate here.

+ MsisdnInventory(...)
------
----
+ seed(items: string[]): void
+ findAvailable(): string[]
+ reserve(msisdn: string, previousMsisdn: string | null): void

## **OnboardingStep** <<type>>

	// CreateAccount | ValidateEmail | SelectPlan | PickNumber | SelectSim | ProfileKyc | Checkout | Done

### Cart `prospect/cart/` — invariant of Prospect

## **Cart** <<Entity>>

+ Cart(...)
------
+ id: string
+ << association >> plan: Plan | null
+ msisdn?: string
+ simType?: SimType
+ iccid?: string
+ << composition >> portingInfo: PortingInfo | null
+ << association >> msisdnInventory: MsisdnInventory
+ availableNumbers: string[]
+ canContinue: boolean
+ iccidError: string | null
----
+ loadAvailableNumbers(): void
+ validate(): void
+ submitNumber(): void
+ submitPort(): void
+ selectPlan(): void
+ submitSim(): void
+ checkout(): void
+ pay(): Order

## **PortingInfo**

+ PortingInfo(...)
------
+ donorOperator?: string
+ accountNumber?: string
+ portNumber?: string
+ userType?: string
+ accountType?: string
+ device?: string
+ verified?: boolean

## **Order** <<Entity>>

+ Order(...)
------
+ id: string
+ number: string
+ << association >> plan: Plan
+ msisdn: string
+ << association >> portingInfo: PortingInfo | null
+ simType: SimType
+ iccid: string
+ << association >> identity: Identity
+ << association >> voucher: Voucher | null
+ payUpFront: boolean
+ status: string
+ verified: boolean
+ headline: string
+ summary: string | null
+ simInfo: string | null
+ invoiceInfo: string | null
+ orderError: string | null
+ paymentError: string | null
+ contactUsHref: string | null

### KycProfile `prospect/profile-kyc/`

## **KycProfile**

+ KycProfile(...)
------
+ << association >> identity: Identity
+ << association >> address: Address
----

## **ProfileKyc**

+ ProfileKyc(...)
------
+ << association >> profile: ProfileFormData | null
+ verificationFailure: string | null
----
+ submitProfile(): void

## **IdentityVerification**

+ IdentityVerification(...)
------
+ verified: boolean
+ inquiryId: string
+ fields?: Record<string, unknown>


# Subscriber — selfcare

A customer after successful checkout, with subscriptions and selfcare surfaces.
Invoice, PaymentMethod, and PaymentReceipt live in this package. There is no Billing type — invoices hang on Subscriber.

## **Subscriber** <<Aggregate Root>> <<Entity>> extends Customer

+ Subscriber(...)
------
+ << association >> paymentMethod: PaymentMethod | null
+ << aggregation >> subscriptions: Subscription[]
+ << aggregation >> invoices: Invoice[]
+ << association >> dashboard: DashboardPage | null
+ << association >> support: SupportPage | null
+ feedbackSubject: string
+ feedbackMessage: string
----
+ loadInvoices(): void
+ loadDashboard(): void
+ loadSupport(): void
+ submitFeedback(): FeedbackReceipt
+ loadProfile(): void
+ saveProfile(): void

## **SubscriberRepository** <<Repository>>

+ SubscriberRepository(...)
------
+ << aggregation >> subscriber: Subscriber
----
+ seed(subscriber: Subscriber, extras?: SubscriberSeedExtras): Subscriber
+ load(): Subscriber
+ save?(subscriber: Subscriber): void

## **Subscription** <<Entity>>

+ Subscription(...)
------
+ id: string
+ number: string
+ simtype: SimType
+ status: string
+ << composition >> bundle: SubscriptionBundle
+ usage?: { local: { used: number; quota: number } }
----
+ changePlan(plan: Plan): PlanChangeConfirmation
+ linePortability(): LinePortability
+ leavePorting(): string | null

## **LinePortability**

+ LinePortability(...)
------
+ donorOperator?: string
+ accountNumber?: string
+ portNumber?: string
+ userType?: string
+ accountType?: string
+ device?: string
+ verified?: boolean
+ explanation: string | null
+ portNumberError: string | null
+ error: string | null
+ canSubmit: boolean
----
+ validate(): void
+ submit(): void

## **SubscriptionBundle**

+ SubscriptionBundle(...)
------
+ id: string
+ name: string
+ description: string
+ fees: number
+ price: number
+ totalPrice: number
+ << composition >> features: SubscriptionFeature[]
----

## **SubscriptionFeature**

+ SubscriptionFeature(...)
------
+ text: string[]
+ icon: string
+ disabled?: boolean

## **PlanChangeConfirmation**

+ PlanChangeConfirmation(...)
------
+ termsAccepted: boolean
+ canConfirm: boolean
+ summary: string | null
+ catalogHeading: string | null
+ infoMessage: string | null
+ error: string | null
----
+ validate(): void
+ confirm(): void
+ goBack(): void

## **DashboardPage**

+ DashboardPage(...)
------
+ usedLabel: string
+ quotaLabel: string
+ << association >> latestInvoice: Invoice | null
+ billsHeading: string

## **SupportPage**

+ SupportPage(...)
------
+ helpPrompt: string
+ feedbackPrompt: string
+ knowledgeBasePrompt: string

## **FeedbackReceipt**

+ FeedbackReceipt(...)
------
+ message: string
+ << association >> customer: Customer

## **Invoice** <<Entity>>

+ Invoice(...)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string
+ << association >> subscriber: Subscriber | null
----
+ pay(): PaymentReceipt

## **PaymentMethod** <<Entity>>

+ PaymentMethod(...)
------
+ id: string
+ status: string
+ brand: string
+ lastFourDigits: string
+ termsAccepted: boolean
+ canUpdate: boolean
----
+ validate(): void
+ update(): void

## **PaymentReceipt**

+ PaymentReceipt(...)
------
+ message: string


# ParadiseMobile — application handle

Top-level application handle. Stories obtain all domain objects from here.

## **ParadiseMobile**

+ ParadiseMobile(...)
------
----
+ accountCredentialsRepository(): AccountCredentialsRepository
+ catalogPage(): CatalogPage
+ planRepository(): PlanRepository
+ prospectRepository(): ProspectRepository
+ subscriberRepository(): SubscriberRepository
+ msisdnInventory(): MsisdnInventory
+ close(): void

## **Config**

+ Config(...)
------
+ connected: Connection
+ application: Application
+ mode: Mode

