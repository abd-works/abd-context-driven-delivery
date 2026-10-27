---
fidelity: [model]
artifact: [ce-domain-model]
format: md
---

**Sources / context:** `stories/story-map.md` (Create Customer, Sign In With Existing Account, Create Empty Cart, Get New Number, Get Ported Number, Verify Ported Number, Get Available Premium Numbers, Reserve Premium Msisdn Resource, Patch Cart With Premium Number, Get Catalog, Get Plan On Cart, Get Sim: Evaluate Esim Flag, Choose a Sim, Check Esim Compatibility, Continue To Sim Choice, Get Esim, Get Paradise Sim Card (Request a Paradise Sim Card through Store Sim Type in Session), Get Existing Iccid (Enter Existing Sim through Store Sim Type And Iccid), Activate Sim From Almost There (Activate Sim through Patch Account), Complete Persona Kyc — Validate Persona Inquiry through Map Persona Inquiry To Profile And Store In Session, Verify Later, Patch Mavenir Customer, Get Applied Voucher, Get Data Freedom Upgrade, Get Review Plan, Enter Payment, Evaluate Payment Flags, Load Customer, Request Payment Authorization, Authorize Card, Read Tokenized Card, Provide Apple Pay Certificate, Create Billing Account, Create Product Order, Redeem Voucher, Apply Credit, View Order Result, Create Order Ticket); `stories/onboard-a-customer/create-customer/story-scenarios.md`; `stories/onboard-a-customer/sign-in-with-existing-account/story-scenarios.md`; `stories/onboard-a-customer/create-empty-cart/story-scenarios.md`; `stories/onboard-a-customer/get-number/story-scenarios.md` (Get New Number, Get Ported Number, Verify Ported Number); `stories/onboard-a-customer/get-premium-number/story-scenarios.md` (Get Available Premium Numbers, Reserve Premium Msisdn Resource, Patch Cart With Premium Number); `stories/onboard-a-customer/get-onboarding-plan/story-scenarios.md` (Get Catalog, Get Plan On Cart); `stories/onboard-a-customer/get-sim/story-scenarios.md` (Evaluate Esim Flag, Choose a Sim, Check Esim Compatibility, Continue To Sim Choice, Get Esim, Get Paradise Sim Card — Request a Paradise Sim Card through Store Sim Type in Session, Get Existing Iccid — Enter Existing Sim through Store Sim Type And Iccid, Activate Sim From Almost There — Activate Sim through Patch Account); `stories/onboard-a-customer/get-verified-profile/story-scenarios.md` (Complete Persona Kyc — Validate Persona Inquiry through Map Persona Inquiry To Profile And Store In Session; Verify Later; Patch Mavenir Customer — Enter Profile And Identity through Store My Paradise Customer In Session); `stories/onboard-a-customer/get-applied-voucher/story-scenarios.md` (Submit Apply Voucher Request; Get Vouchera Voucher and Patch Mavenir Customer; Validate Voucher; Patch Mavenir Customer; Store Vouchera Voucher on My Paradise Customer in Session); `stories/onboard-a-customer/get-order-review/story-scenarios.md` (Get Data Freedom Upgrade — Upgrade To Data Freedom, Query Product Offerings, List Product Offerings, Patch Cart With Plan, Patch Shopping Cart; Get Review Plan — Change Plan From Review, Query Product Offerings, List Product Offerings, Patch Cart With Plan, Patch Shopping Cart); `stories/onboard-a-customer/get-payment/story-scenarios.md` (Enter Payment; Evaluate Payment Flags — Evaluate PAY_UP_FRONT, Evaluate PAYMENT_ATTEMPTS; Load Customer — Load My Paradise Customer From Midtier And Store In Session; Get Mavenir Customer and Transform To My Paradise Customer And Return; Get Mavenir Customer; Request Payment Authorization; Authorize Card; Read Tokenized Card Midtier; Read Tokenized Card Mavenir; Provide Apple Pay Certificate); `stories/onboard-a-customer/place-order/story-scenarios.md` (Create Billing Account; Create Product Order; View Order Result; Create Order Ticket); `stories/onboard-a-customer/get-voucher-credit/story-scenarios.md` (Submit Redeem Voucher Request to Vouchera; Redeem Voucher; Submit Apply Credit Request to Mavenir; Apply Credit on Mavenir Customer); `stories/onboard-a-customer/story-scenarios.md`; `stories/system-terms.md` (++PersonaInquiry++, ++PersonaDocument++, ++Voucher++, ++VoucherRedemption++, ++MavenirCreditAdjustment++, ++PaymentIframe++, ++PaymentCharge++, ++PaymentStatus++, ++ApplePayCertificate++, ++MavenirBillingAccount++, ++MavenirProductOrder++, ++Ticket++); `.context/bounded-context-map.md`; `deprecated/domain/.context/domain-model.md`

Check The Order is display-only: Order Review displays existing Customer, Cart (including `bundle`), and Voucher; no new types.

Get Review Plan reuses `PlanRepository.list` and `Cart.pickPlan`. Keep current plan, edit Plan, and Checkout forward are navigation. Same-plan Select is existing no-patch. Flagged failure is `CartErrors.patch`.

Enter Payment is `# Payments` `Payment.enter` wrapping ++PaymentIframe++ and composing ++PaymentCharge++. Authorize Card is FAC `FAC.create` then `read` on that wrap. Provide Apple Pay Certificate is `Apple.read` in `# Payments`. GrowthBook `PAY_UP_FRONT` / `PAYMENT_ATTEMPTS` / `ROAMING_PLAN_TICKET` live on the existing Cart system type. Load Customer is `CustomerRepository.load`. Checkout is `Cart.checkout` (read tokenized card). Create Billing Account is `# Billing` `Billing.create`. Create Product Order is `Cart.createOrder` (POST `/customer/order` with no body). When cook, Redeem Voucher is `Vouchera.redeem`; when cook after redeem, Apply Credit is `PortalGateway.applyCredit`. Then `Cart.storeOrderResult`. View Order Result when allSet else View Almost There. Create Order Ticket is `# Care` `CaseRepository.open` → `Zendesk.create`. Plan.bypassVerified is dataFreedom essentials trial.

# Customer

Slow-changing party: who the person is. Identity, Address, Credentials. Map: Customer · Customer (Authentication · Account lives here). One Paradise *Customer*. Confirm-ID catalog lives in `# KYC`. Persona inquiry / documents live in `# Care`. Shopping cart lives in `# Cart`. Inventory: `# Plans`, `# Numbers and SIMs`, `# Porting`. Card auth lives in `# Payments`. Billing account lives in `# Billing`. Billed line, usage, Alchera live in `# Subscription`. Tickets and cases live in `# Care`.

Paradise *Customer* (++MyParadiseCustomer++ in session, ++PMLCustomer++ on Midtier). Mavenir *MavenirCustomer* (DEP; createaccounts / customerDetails). Midtier maps between them. Create-time Paradise: email on *Identity*, empty *Address*, verified false. `Customer.confirmIdentity` patches the party after KYC. Confirm-ID rows are `ProfileRequirements` in `# KYC`. Inquiry and documents are `# Care`. Payment iframe / Apple Pay / PaymentStatus live in `# Payments`.

## Paradise

### **Customer** <<Aggregate Root>> <<Entity>>

+ Customer(accountCredentials: AccountCredentials)
	// canonical form: new Customer(accountCredentials)
	// id, identity, and address are derived from accountCredentials when not passed
	// repository passes explicit id / identity / address when Mavenir has richer data
------
+ id: string
	// derived from accountCredentials.customerId when not passed
	// empty string when credentials have no customer id
+ verified: boolean
	// persisted KYC on the party
	// always false after ProfileRequirements.mapInquiry / storeFailedInquiry
	// flips true on confirmIdentity when PersonaInquiry.verified
	// Cart.storeOrderResult overwrites from order-body verified
	// order-body verified is Midtier verifiedResponse = KYC | Portability.portNumber | Plan.bypassVerified
	// fail Cart.storeOrderResult does not write verified
+ << composition >> identity: Identity
	// derived from accountCredentials.email when not passed
+ << composition >> address: Address
	// empty Address when not passed
+ << association >> accountCredentials: AccountCredentials
	// required constructor argument; own aggregate, not composed
+ << association >> cart: Cart | null
	// from Cart
	// 0..1
	// set by CartRepository.find / create
+ << association >> billing: Billing | null
	// from Billing
	// 0..1
	// Mavenir customer.account[0]
+ << association >> subscriptions: Subscription[]
	// from Subscription
	// 0..*
	// each line is one Subscription after cook
+ << association >> personaInquiry: PersonaInquiry | null
	// from Care
	// 0..1
----
+ confirmIdentity(): Customer
	-> ProfileRequirements.missing
	-> PortalGateway.patchProfile
	// AccountToken already on the wrap
	// maps Identity / Address onto EngagedParty + ContactMedium
	// uses Customer.personaInquiry internally
	// Customer.verified from PersonaInquiry.verified when the inquiry is present
	// always true on the happy path
	// inquiryId on Mavenir from PersonaInquiry.inquiryId when present
	// duplicate Identity.idNumber or patch failure throws CustomerException with operation confirmIdentity
	// auto-apply voucher after success is Cart.applyVoucher

### **CustomerRepository** <<Repository>>

+ CustomerRepository(...)
------
+ << aggregation >> customers: Collection<Customer>
+ << association >> midtierCustomerService: MidtierCustomerService
----
+ create(accountCredentials: AccountCredentials): Customer | null
	-> AccountCredentials.verified
	-> MidtierCustomerService.create
	// existing CognitoUser.customerId: returns null without MidtierCustomerService.create
	// missing CognitoUser.customerId: submits Create Customer Request to Midtier
	// failure throws CustomerException with operation create, AccountCredentials and cause
	// returns the new Customer; Cart.setupAccount stores its id on the Cognito user
+ load(accountCredentials: AccountCredentials): Customer
	-> MidtierCustomerService.read
	-> AccountCredentials.signOut
	// failure throws CustomerException with operation load, AccountCredentials and cause
	// terminated billing or load failure signs out

### **MidtierCustomerService** <<Service>>

My Paradise HTTP boundary to Midtier. Midtier validates the account token and forwards customer operations to Mavenir.

+ MidtierCustomerService(...)
------
----
+ validate(accountToken: AccountToken): string | Error
	// Midtier validates the JWT and returns its Cognito email claim
+ create(accountToken: AccountToken): string | Error
+ read(accountToken: AccountToken): MavenirCustomer | Error

### **CustomerException** <<Exception>>

One typed Customer failure carrying enough domain context for callers to handle and report repository and aggregate failures safely.

+ CustomerException(...)
------
+ operation: CustomerOperation
+ accountCredentials: AccountCredentials
+ message: string
+ cause: Error

### **Identity** <<Entity>>

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

### **Address** <<Entity>>

+ Address(...)
------
+ street: string
+ complement: string
+ city: string
+ parish: string
+ postalCode: string
+ country: string


### **AccountCredentials** <<Aggregate Root>> <<Entity>>

Paradise wrap of ++CognitoUser++. Own aggregate: constructed through `AccountRepository.newAccount()`. Auth operations live on this object and persist through the wired repository. `verified` is Cognito confirmed / unconfirmed.

+ AccountCredentials(emailOrCognitoUser: string | CognitoUser)
	// from CognitoUser: email and verified come from the user; do not re-pass them
	// from email: password, confirmPassword, validationCode, verified optional
------
+ email: string
	// from CognitoUser.email when constructed from CognitoUser
+ password: string
+ confirmPassword: string
+ validationCode: string
+ verified: boolean
	// from CognitoUser.confirmed when constructed from CognitoUser
+ token: AccountToken | null
	// derived from CognitoUser.accountToken
+ customerId: string | null
	// derived from CognitoUser.customerId
+ validationCodeWasSent: boolean
	// true when CognitoUser.validationCodeSentAt is set
+ canActivate: boolean
	// true when a validation code has been sent
+ isUpdatable: boolean
+ isPersistable: boolean
	// true when missingRequirements is empty
+ resendMessage: string | null
+ << composition >> errors: AccountCredentialsErrors
+ << composition >> requirements: AccountCredentialRequirements
+ <<represents>> CognitoUser
----
+ missingRequirements(): AccountCredentialRequirement[]
	// when AccountCredentials are updated
	// empty: credentials meet all requirements
	// otherwise the unmet AccountCredentialRequirement rows
+ register(): void
	-> AccountRepository.persistNewAccount
	// missingRequirements must be empty
	// already-registered email fails
	// writes CognitoUser onto these credentials; verified stays false until activate
+ activate(validationCode: ValidationCode): void
	-> AccountRepository.confirmAccount
	-> AccountRepository.authenticateAccount
	// requires validationCodeWasSent
	// unusable ValidationCode fails
	// reads CognitoUser.confirmed into verified
	// signs in after confirmation
+ authenticateAccount(): void
	-> AccountRepository.authenticateAccount
	// email required, email format, and password required must be met — otherwise no Cognito call
	// existing account holder signs in
	// writes signed-in CognitoUser, account token, and customerId onto these credentials
	// wrong password and unknown email fail with the same NotAuthorizedException
	// unconfirmed account returns CONFIRM_SIGN_UP
+ resendValidationCode(): void
	-> AccountRepository.resendAccountCode
	// throws ValidationCodeResendWaitException when 60 seconds have not elapsed
+ signOut(): void
	-> AmplifyService.signOut
+ storeCustomerId(customerId: string): CognitoUser
	-> AmplifyService.updateUserAttributes
	// failure throws CustomerException with operation storeCustomerId, these AccountCredentials and cause

### **AccountRepository** <<Repository>>

Wraps the Cognito agent. Credentials exist before a Customer. `newAccount` is the canonical constructor: it returns AccountCredentials with the repository wired so register / activate / authenticateAccount / resendValidationCode persist.

+ AccountRepository(...)
------
+ << aggregation >> accountCredentials: Collection<AccountCredentials>
+ << association >> amplifyService: AmplifyService
----
+ newAccount(credentials?: AccountCredentials): AccountCredentials
	// constructs AccountCredentials('') when none given
	// wires the repository onto the returned aggregate
+ persistNewAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
	-> AmplifyService.signUp
	// called by AccountCredentials.register
+ confirmAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
	-> AmplifyService.confirmSignUp
	// called by AccountCredentials.activate
+ authenticateAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
	-> AmplifyService.signIn
	// called by AccountCredentials.authenticateAccount and by activate after confirm
	// unverified: no AccountToken
	// wrong password or unknown email fails
+ resendAccountCode(accountCredentials: AccountCredentials): CognitoUser | null
	-> AmplifyService.resendSignUpCode
	// called by AccountCredentials.resendValidationCode

### **AccountCredentialsErrors**

Commit failures after `AccountCredentials.register` / `activate` / `AccountRepository.authenticateAccount`. Field rules are `missingRequirements()`.

+ AccountCredentialsErrors(...)
------
+ register: string | null
+ signIn: string | null
+ validationCode: string | null

### **ValidationCodeResendWaitException** <<Exception>>

Thrown by `AccountCredentials.resendValidationCode` when the 60-second wait has not elapsed. No Cognito call is made.

+ ValidationCodeResendWaitException(...)
------
+ availableAt: Date

### **AccountCredentialRequirement**

One requirement (field + rule).

+ AccountCredentialRequirement(...)
------
+ field: string
+ requirement: string

### **AccountCredentialRequirements**

Catalog of rules. `missingRequirements()` returns the unmet subset.

+ AccountCredentialRequirements(...)
------
+ emailRequired: AccountCredentialRequirement
+ emailFormat: AccountCredentialRequirement
+ passwordRequired: AccountCredentialRequirement
+ passwordLetters: AccountCredentialRequirement
+ passwordNumber: AccountCredentialRequirement
+ passwordSymbol: AccountCredentialRequirement
+ passwordLength: AccountCredentialRequirement
+ confirmRequired: AccountCredentialRequirement
+ confirmMismatch: AccountCredentialRequirement

### **AmplifyService** <<Service>> <<System>>

AWS Amplify Auth in My Paradise. Talks to Cognito. Not a hosted record store.

+ AmplifyService(...)
------
----
+ signUp(email: string, password: string): CognitoUser | Error
+ signIn(email: string, password: string): CognitoUser | Error
+ confirmSignUp(email: string, validationCode: ValidationCode): CognitoUser | Error
+ resendSignUp(email: string): ValidationCodeSend | Error
+ signOut(): void
+ fetchUserAttributes(email: string): CognitoUser | Error
	// My Paradise reads the Mavenir customer id from Cognito user attributes through Amplify
+ getUser(email: string): CognitoUser | null

### **CognitoUser** <<System>> <<Entity>>

Cognito confirmed status is `confirmed`; Paradise reads it as `AccountCredentials.verified`. `AccountCredentials` `<<represents>>` this type.

+ CognitoUser(...)
------
+ email: string
+ confirmed: boolean
+ customerId: string | null
+ validationCodeSentAt: Date | null
+ << association >> accountToken: AccountToken | null

### **AccountToken** <<System>>

+ AccountToken(...)
------
+ email: string
+ customerId: string | null

### **ValidationCode** <<System>>

+ ValidationCode(...)
------
+ code: string

### **ValidationCodeSend** <<System>>

Timestamped record of every initial or repeated validation-code send performed by Amplify.

+ ValidationCodeSend(...)
------
+ code: string
+ sentAt: Date
+ kind: initial | resend

## Mavenir

### **MavenirCustomer** <<Aggregate Root>> <<Entity>>

+ MavenirCustomer(...)
------
+ id: string
+ << association >> productOrder: MavenirProductOrder | null
	// from Subscription
+ << association >> billingAccount: MavenirBillingAccount | null
	// from Billing
+ phoneVerified: boolean
	// always phone_verified
+ waitingPsim: string | null
	// 'true' | 'false' | absent
	// true when pSIM no iccid via patchWaitingPsim
+ done: string | null
	// 'true' | absent
+ inquiryId: string | null
	// inquiryID
	// from PersonaInquiry.inquiryId when present
+ voucher: Voucher | null
	// JSON-encoded Voucher characteristic
	// Cart.applyVoucher writes this
	// absent after Cart.removeVoucher
+ << association >> shoppingCart: MavenirShoppingCart | null
+ << composition >> contactMedium: ContactMedium
+ << composition >> engagedParty: EngagedParty

### **PortalGateway** <<Service>> <<System>>

Mavenir `portalGateway`. Party create / read / profile. Cart, catalog, billing, and order slices live on the same service in their modules.

+ PortalGateway(...)
------
----
+ create(email: string): MavenirCustomer | Error
	// email already in Mavenir fails
+ read(id: string): MavenirCustomer | Error
	// deliverPsim validates waitingPsim from this read
+ patchPhoneVerified(mavenirCustomerId: string): MavenirCustomer | Error
	// always writes phone_verified true
	// when Twilio approved
+ patchWaitingPsim(mavenirCustomerId: string, waitingPsim: boolean): MavenirCustomer | Error
	// true when pSIM no iccid (createOrder)
	// false after deliverPsim
+ patchProfile(mavenirCustomer: MavenirCustomer, engagedParty: EngagedParty, contactMedium: ContactMedium): MavenirCustomer | Error
	// EngagedParty names + birthDate + individualIdentification.validated
	// ContactMedium street + city + stateOrProvince + postCode + phoneNumber
	// contact country always Bermuda
	// inquiryID when mavenirCustomer.inquiryId is present
	// individualIdentification.identificationId already on another MavenirCustomer: conflict
	// invalid AccountToken fails
+ patchVoucher(mavenirCustomer: MavenirCustomer, voucher: Voucher): MavenirCustomer | Error
	// JSON-encoded Voucher as voucher characteristic
+ removeVoucher(mavenirCustomer: MavenirCustomer): MavenirCustomer | Error
	// removes voucher characteristic
+ patchDone(mavenirCustomerId: string): MavenirCustomer | Error
	// always writes done 'true'
	// Billing.createBilling / applyCredit live in # Billing
	// createOrder lives in # Subscription

### **ContactMedium**

+ ContactMedium(...)
------
+ emailAddress: string
+ phoneNumber: string
+ street1: string
+ street2: string
+ city: string
+ stateOrProvince: string
+ postCode: string
+ country: string
	// always Bermuda

### **EngagedParty**

+ EngagedParty(...)
------
+ givenName: string
+ familyName: string
+ preferredGivenName: string
	// preferredName when present; otherwise givenName
+ birthDate: string
+ << composition >> individualIdentification: IndividualIdentification

### **IndividualIdentification**

+ IndividualIdentification(...)
------
+ identificationId: string
	// Identity.idNumber
+ identificationType: string
	// Identity.idType
+ issuingAuthority: string
	// Identity.idNationality
+ validated: boolean
	// Customer.verified
+ endDateTime: string
	// Identity.expiryDate

# KYC

Identity verification catalog. Map: Identity Verification · Inquiry. Confirm-ID rows (`ProfileRequirement` / `ProfileRequirements`) live here. `Customer.verified` (persisted KYC) stays on the party. Persona *inquiry* and *document* types live in `# Care`. `ProfileRequirements.mapInquiry` / `storeFailedInquiry` write Identity / Address on the party.

## Paradise

### **ProfileRequirement**

One required Identity / Address field row (`field`, `requirement`).

+ ProfileRequirement(...)
------
+ field: string
+ requirement: string

### **ProfileRequirements**

Catalog of required Identity / Address rows. Optional preferredName, otherPhoneNumber, complement, city, country are not in this catalog. Persona does not create these rows. `mapInquiry` copies a `# Care` ++PersonaInquiry++ onto the party's Identity / Address; `missing` then lists which catalog rows are still unmet.

+ ProfileRequirements(...)
------
+ nameRequired: ProfileRequirement
+ lastNameRequired: ProfileRequirement
+ dateOfBirthRequired: ProfileRequirement
+ idNationalityRequired: ProfileRequirement
+ idTypeRequired: ProfileRequirement
+ idNumberRequired: ProfileRequirement
+ expiryRequired: ProfileRequirement
+ streetRequired: ProfileRequirement
+ parishRequired: ProfileRequirement
+ postalCodeRequired: ProfileRequirement
----
+ missing(identity: Identity, address: Address): ProfileRequirement[]
	// when Identity / Address are updated
	// empty: Confirm ID may proceed
	// otherwise the unmet ProfileRequirement rows
+ validateInquiry(identity: Identity): string
	// Identity.idNumber
	// absent: inquiry required
	// present: already complete
+ mapInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer
	// maps PersonaInquiry onto Identity / Address
	// expiryDate from PersonaDocument or empty
	// PersonaInquiry.verified from status completed
	// Customer.verified stays false
	// failed inquiry: PersonaInquiry.verified false; Identity / Address may stay empty
+ storeFailedInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer
	// create failed
	// no field map
	// PersonaInquiry.verified false
	// Customer.verified stays false

# Cart

Paradise Cart is the customer's selection. `CartRepository` talks to `PortalGateway` to read and write ++MavenirShoppingCart++. Cart does not know the shopping cart. Empty at create (no items). Create-time Mavenir cart: *MavenirCustomer* id, lineCount 1, empty cartItem, ON-BOARDING *Channel*. Midtier returns `{ id }`. Paradise Cart with no items is `{ id }`. *Get Plan On Cart* (`Cart.pickPlan`) **composes** a *Bundle* snapshot; that Bundle **associates** to the catalog *Plan* in `# Plans`. Number lock/reserve/search live in `# Numbers and SIMs`. Cart **links** `# Porting` *Portability* (association only; donor / account / SMS live on Porting). Selected *Voucher* lives on Cart until cook (`Cart.applyVoucher` / `removeVoucher`); cook writes *VoucherRedemption* on `# Subscription`. Payment is on the cart (`Cart.checkout`). `Cart.createOrder` writes *MavenirProductOrder* (lives on `# Subscription` after cook) via `PortalGateway.createProductOrder`. After the card is approved, `# Billing` creates the party's billing account, then `Cart.createOrder`. After *Get Plan On Cart*, Paradise Cart carries `bundle`. After *Get New Number* / *Get Premium Number*, Paradise Cart carries `msisdn` on `Line`. After *Get Ported Number*, Paradise Cart's `Line` carries `msisdn` (temporary) and **links** `portability` in `# Porting`. After *Get Sim* stories, `Line` carries `simType` / `iccid`.

## Paradise

### **Cart** <<Aggregate Root>> <<Entity>>

+ Cart(...)
------
+ << association >> customer: Customer
+ id: string
+ << composition >> line: Line
+ << composition >> bundle: Bundle | null
	// snapshot of selected Plan
	// set by Cart.pickPlan
	// catalog Plan changes do not rewrite this snapshot
+ << association >> portability: Portability | null
	// link to Porting
	// set by Cart.bringNumber
	// details and SMS live on Portability
+ << association >> voucher: Voucher | null
	// selected code until cook
	// null until applyVoucher
	// always null after removeVoucher
	// cook reads this code for Vouchera.redeem
+ << association >> growthBook: GrowthBook
	// flags Cart consults (sim, pay-up-front, attempts, roaming ticket)
+ defaultPayment: boolean
	// always true after storeOrderResult
+ orderSuccess: boolean | null
	// success from Store Order Result
+ payUpFront: boolean | null
	// stored when present
	// null on fail
----
+ onboardingStep: OnboardingStep
	// derived property recalculated from current Cart and Customer state on access
	// first step in missingOnboardingSteps; Done when none are missing
+ missingOnboardingSteps: OnboardingStep[]
	// derived property recalculated from Cart bundle, number/portability, SIM and Customer identity/billing
	// preserves journey order so returning customers resume at the earliest incomplete step
+ setupAccount(): Customer | null
	-> CustomerRepository.create
	// existing Cognito customer id: CustomerRepository.load through Midtier
	// missing Cognito customer id: CustomerRepository.create through Midtier, then AccountCredentials.storeCustomerId
+ pickPlan(plan: Plan): Cart | CartErrors    //applyPlan
	-> PortalGateway.patchBundle
	// copies Plan onto Cart.bundle
	// Cart.bundle.plan is that Plan
	// first Select writes bundle onto empty cart
	// later Select replaces bundle
	// Get Data Freedom Upgrade is later Select
	// Get Review Plan is later Select
	// when the same Plan is already on cart: no patch
	// when portability is present: portability.planSelected is the Plan name
	// when patch fails: CartErrors.patch
+ pickNumber(availableNumber: AvailableNumber): Cart | CartErrors
	-> MsisdnInventoryRepository.reserve
	-> PortalGateway.patchMsisdn
	// previousId is always the current msisdn
	// portin is always false
	// premium selected id uses the same patchMsisdn hop
	// portability stays null
	// when reserve fails: CartErrors.reserve
	// when patch fails: CartErrors.patch
+ bringNumber(portability: Portability): Cart | CartErrors
	-> MsisdnInventoryRepository.list
	-> MsisdnInventoryRepository.reserve
	-> PortalGateway.patchPortability
	// always list size 1
	// previousId is always the current msisdn
	// portin is always true
	// msisdn is always the reserved temporary number
	// when reserve fails: CartErrors.reserve
	// when patch fails: CartErrors.patch
	// when portability fails: CartErrors.portability
	// when porting-2fa is off: no SMS
	// when porting-2fa is on: Twilio after patch
	// Portability.verified is false
	// Line.portability is the link to that Portability
+ applyVoucher(code: string): Cart | VoucherErrors
	-> Vouchera.read
	-> PortalGateway.patchVoucher
	// POST /customer/voucher
	// sets Cart.voucher
	// skip when voucher is present
	// auto-apply after Customer.confirmIdentity
	// session storage clear after auto-apply is intended
	// trial voucher requires a trial plan on cart
	// trial without trial plan: VoucherErrors.trial (500)
	// unknown code: VoucherErrors.invalid
	// expired: VoucherErrors.expired
	// redeemed: VoucherErrors.redeemed
	// intended: expired and redeemed are typed; live 400 has no body
	// other request failure: VoucherErrors.request
	// auto-apply rejection: VoucherErrors.notWorking
+ removeVoucher(): Cart | VoucherErrors
	-> PortalGateway.removeVoucher
	// DELETE /customer/voucher
	// voucher always null after success
+ checkout(payment: Payment): Cart | PaymentErrors
	-> FAC.read
	-> createOrder
	// payment is on the cart (Authorize Card)
	// Payment is not on the order
	// always GET /customer/payment/status/:transactionId
	// when completed: PortalGateway.createBilling on the Customer then Cart.createOrder
	// when failed and attempts under PAYMENT_ATTEMPTS: PaymentErrors.unverified; Payment.enter again
	// when failed and attempts equal PAYMENT_ATTEMPTS: Payment.recordFailed then Cart.createOrder
+ createOrder(customer: Customer): Cart
	-> PortalGateway.createProductOrder
	-> CaseRepository.open
	-> storeOrderResult
	// writes MavenirProductOrder (lives on Subscription after cook)
	// always POST /customer/order
	// no body
	// Redeem Voucher when cook: Vouchera.redeem writes VoucherRedemption on Subscription
	// Apply Credit when cook: Billing / PortalGateway.applyCredit
	// Create Order Ticket: CaseRepository.open in # Care
	// Then hop Store Order Result
+ storeOrderResult(customer: Customer, success: boolean, payUpFront: boolean | null, verified: boolean): Cart
	// always defaultPayment true
	// orderSuccess = success
	// payUpFront stored when present; null on fail
	// success: overwrite Customer.verified from order-body verified
	// order-body verified is Midtier verifiedResponse = KYC | Portability.portNumber | Plan.bypassVerified
	// fail: does not write verified
	// Then View Order Result when allSet else View Almost There
	// banners: orderUnprocessed / paymentUnverified / SimBanner iccidRequired

### **OnboardingStep** <<type>>

Cart-module constants. Not open strings.

	OnboardingStep.SelectPlan
	OnboardingStep.PickNumber
	OnboardingStep.VerifyPortedNumber
	OnboardingStep.SelectSim
	OnboardingStep.ProfileKyc
	OnboardingStep.Checkout
	OnboardingStep.Done

### **Bundle** <<Entity>>

Snapshot of a `# Plans` *Plan* at pick time. Part of the Cart aggregate. PortalGateway cart read maps the Mavenir bundle cartItem onto `Cart.bundle` (`id`, `name`, `description`, `price`, `fees`, `totalPrice`, `features`). `id` is *Plan.id*. Catalog *Plan* changes do not rewrite a cart that already has a bundle.

+ Bundle(...)
------
+ id: string
	// Plan.id
+ name: string
+ description: string
+ price: number
+ fees: number
+ totalPrice: number
+ features
	// copied at pick time
+ << association >> plan: Plan
	// from Plans
	// where this snapshot came from
	// not composed; catalog Plan stays in Plans

### **GrowthBook** <<System>>

Flags Cart consults. Get Sim: `DISABLE_ESIM` / `DISABLE_PSIM`. `Cart.checkout` / `Payment.enter` read `PAY_UP_FRONT` and `PAYMENT_ATTEMPTS` from this type (Payment does not own GrowthBook). `Cart.createOrder` reads `PAY_UP_FRONT` and `ROAMING_PLAN_TICKET`. No Paradise types. No repository.

+ GrowthBook(...)
------
+ DISABLE_ESIM: string
	// disable-esim
+ DISABLE_PSIM: string
	// disable-psim
+ PAY_UP_FRONT: string
	// pay-up-front
	// when off: invoicePayment
	// when on: upfrontPayment
+ PAYMENT_ATTEMPTS: string
	// payment-attempts
	// always 3 on the scenario
	// live default is always 1
+ ROAMING_PLAN_TICKET: string
	// roaming-plan-ticket
----
+ evaluate(key: string): boolean
	// DISABLE_ESIM or DISABLE_PSIM or PAY_UP_FRONT or ROAMING_PLAN_TICKET
	// esimFlagOn / esimFlagOff / psimFlagOn / psimFlagOff
	// when DISABLE_ESIM is true: wizard starts at physical SIM
	// when DISABLE_PSIM is true: hide pSIM card and dialog Nope
	// Flagged: live also hides Yay
	// when PAY_UP_FRONT is off: invoicePayment Time to add your payment
	// when PAY_UP_FRONT is on: upfrontPayment Complete your payment
+ value(key: string): number
	// always PAYMENT_ATTEMPTS
	// always 3 on the scenario
	// live default is always 1



### **CartRepository** <<Repository>>

Owns `Collection<Cart>`. Associates to `PortalGateway` to read and create ++MavenirShoppingCart++. Cart itself has no shopping-cart edge. The Customer already holds AccountCredentials.

+ CartRepository(...)
------
+ << aggregation >> carts: Collection<Cart>
+ << association >> portalGateway: PortalGateway
+ << association >> customerRepository: CustomerRepository
----
+ load(customer: Customer): Cart | null
	-> PortalGateway.read
	// always sets Customer.cart when a Cart exists
	// customer.id is always the MavenirCustomer id
	// when none: null
	// when Mavenir is unreachable: throws CartException with operation load, Customer and cause
+ create(customer: Customer): Cart
	-> PortalGateway.create
	// always sets Customer.cart
	// customer.id is always the MavenirCustomer id
	// when find is null
	// never when a cart already exists for that Customer
	// when a Cart already exists or Mavenir is unreachable: throws CartException with operation create, Customer and cause

### **CartException** <<Exception>>

+ CartException(...)
------
+ operation: CartOperation
+ customer: Customer
+ message: string
+ cause: Error

## System

### **Voucher** <<System>> <<Entity>>

Wrap target. Vouchera ++Voucher++. No Paradise types. Cart wraps the selected code until cook.

+ Voucher(...)
------
+ code: string
+ campaign: string
+ expired: boolean
+ redeemed: boolean
+ discount.percent_off: number
+ discount.amount_off: number
+ metadata.planIds
+ metadata.trial: boolean
+ metadata.trialDays: number
+ metadata.trialData

### **Vouchera** <<Service>> <<System>>

Vouchera builds the ++Voucher++. Vouchera GET /vouchers/{code}. `read` is catalog `Voucher.apply` through `VoucherRepository.get`. `redeem` is Subscription cook and returns `# Subscription` *VoucherRedemption*.

+ Vouchera(...)
------
----
+ read(code: string): Voucher | Error
	// unknown code: none
+ redeem(code: string, redeemerIdentifier: string, orderAmount: number): VoucherRedemption
	// Redeem Voucher
	// always POST vouchers/{code}/redeem
	// cook only
	// planIds match: orderAmount totalPrice then hop Apply Credit
	// no planIds: orderAmount 0.00 then cook
	// planIds miss: skip redeem then cook
	// flagged 5xx: success false; cook continues
	// writes Subscription.voucherRedemption

## Mavenir

**Flagged.** Flush ++MavenirShoppingCart++ against mid-tier: run `app-sandbox/mid-tier` through the app it points at, capture the live shoppingCart create/read/patch body, and replace these fields with that record. Paradise currently keeps `{ id }` at create, `bundle` after pickPlan, `msisdn` after pick, and `msisdn` plus ++portability++ after bring. After *Verify Ported Number*, Paradise `portability.verified` is always true; Mavenir `phone_verified` is always true. After *Choose Esim*, Paradise `Line.simType` is SimType.Esim; Mavenir writes `SIM_TYPE` eSIM. After *Request a Paradise Sim Card*, Paradise `Line.simType` is SimType.Psim; Mavenir writes `SIM_TYPE` pSIM without `ICCID`. After *Enter Existing Sim*, Paradise `Line.simType` is SimType.Psim and `iccid`; Mavenir writes `SIM_TYPE` pSIM and `ICCID` on the existing bundle cartItem. After *Activate Sim From Almost There*, Paradise `Line` still carries SimType.Psim and `iccid`; Mavenir productOrderFromCart then waitingPsim false. Flagged later: `reserveIccid` / `kv_IMSI1` (checkout). Story cites reserve; onboarding PATCH cart does not.

### **MavenirShoppingCart** <<Aggregate Root>> <<Entity>>

Wrap target. Empty at create (no cart items). Mavenir shoppingCart create: MavenirCustomer id, lineCount 1, empty cartItem, serviceProviderId, ON-BOARDING channel. *Get Plan On Cart* writes the bundle cartItem. *Get Data Freedom Upgrade* replaces that bundle. *Get Review Plan* replaces that bundle. Patch writes the MSISDN *ProductCharacteristic* and, on bring, ++portability++ characteristics. *Get Esim* writes the `SIM_TYPE` *ProductCharacteristic* (`'eSIM'`). *Get Paradise Sim Card* writes `SIM_TYPE` (`'pSIM'`); no ICCID characteristic. *Get Existing Iccid* writes `SIM_TYPE` (`'pSIM'`) and `ICCID` on the existing bundle cartItem. *Activate Sim From Almost There* PATCH shoppingCart billing then POST productOrderFromCart; SIM_TYPE `'pSIM'` and ICCID already on bundle. The wrap does not know Cart.

+ MavenirShoppingCart(...)
------
+ id: string
+ customerId: string
+ lineCount: number
+ serviceProviderId: string
+ cartItem: bundle
	// Get Plan On Cart writes the bundle
	// Get Data Freedom Upgrade replaces the bundle
	// Get Review Plan replaces the bundle
	// always a bundle when patching MSISDN, ++portability++, SIM_TYPE, or ICCID
	// bundle cartItem already present for pickSim and pickIccid
+ << composition >> productCharacteristic: ProductCharacteristic
+ << composition >> channel: Channel

### **PortalGateway** <<Service>> <<System>>

Mavenir `portalGateway` shopping cart.

+ PortalGateway(...)
------
----
----
+ read(mavenirCustomerId: string): MavenirShoppingCart | Error
	// when none for that MavenirCustomer: none
+ create(mavenirCustomerId: string): MavenirShoppingCart | Error
	// always lineCount 1, empty cartItem, ON-BOARDING channel
	// never when a cart already exists for that MavenirCustomer
+ patchBundle(mavenirCustomerId: string, bundleId: string): MavenirShoppingCart | Error
	-> PortalGateway.list
	// always fetches the catalog bundle
	// always builds the bundle cartItem
	// always PATCH shopping cart
	// first Select writes bundle onto empty cart
	// later Select replaces bundle
	// Get Data Freedom Upgrade is later Select
	// Get Review Plan is later Select
	// when portability is present: planName is the bundle name
+ patchMsisdn(mavenirCustomerId: string, msisdn: string): MavenirShoppingCart | Error
	// always writes MSISDN ProductCharacteristic on the bundle cartItem
	// premium ++MSISDN++ is the same MSISDN ProductCharacteristic (no premium variant)
+ patchPortability(mavenirCustomerId: string, msisdn: string, characteristics: ProductCharacteristic[]): MavenirShoppingCart | Error
	// always writes MSISDN and ++portability++ ProductCharacteristic rows on the bundle cartItem
+ patchSimType(mavenirCustomerId: string, simType: string): MavenirShoppingCart | Error
	// always writes SIM_TYPE ProductCharacteristic on the bundle cartItem
	// Get Esim: value always 'eSIM'
	// Get Paradise Sim Card: value always 'pSIM'
	// no ICCID characteristic
	// bundle cartItem already present
+ patchIccid(mavenirCustomerId: string, iccid: string): MavenirShoppingCart | Error
	// always writes SIM_TYPE 'pSIM' and ICCID on the existing bundle cartItem
	// no sim-resource reserve
+ createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error
	// PATCH shoppingCart billing (pre-cook) then POST productOrderFromCart
	// SIM_TYPE 'pSIM' and ICCID already on bundle
	// Create Product Order cook
+ patchSubmitOrder(mavenirCustomerId: string): MavenirShoppingCart | Error
	// always writes submitOrder true on the bundle cartItem
	// when unverified no bypass no portability

### **ProductCharacteristic**

MSISDN, ++portability++, SIM_TYPE, and ICCID characteristics on the bundle cartItem.

+ ProductCharacteristic(...)
------
+ name: string
+ value: string

### **Channel**

ON-BOARDING channel on shoppingCart create.

+ Channel(...)
------
+ id: string
+ name: string
+ role: string


# Plans

Paradise *Plan* `<<represents>>` ++MavenirProductOffering++. Get Catalog is the onboarding catalog map: Midtier lists Mavenir product offerings through `PortalGateway` and maps them to Paradise *Plan* (`PlanRepository.list`). Get Plan On Cart copies that *Plan* onto Cart as a *Bundle* snapshot (`Cart.pickPlan`); *Bundle.plan* is the catalog *Plan*. Get Data Freedom Upgrade uses the same catalog map (`PlanRepository.list`) and the same snapshot write (`Cart.pickPlan`). Get Review Plan uses the same catalog map (`PlanRepository.list`) and the same snapshot write (`Cart.pickPlan`). Catalog *Plan* stays in this module. Midtier maps; it is not a type.

## Paradise

### **Plan** <<Aggregate Root>> <<Entity>>

Paradise *Plan* `<<represents>>` ++MavenirProductOffering++.

+ Plan(...)
------
+ id: string
+ name: string
	// after Midtier map
+ price: number
+ isSellable: boolean
+ bypassVerified: boolean
	// dataFreedom essentials trial
+ <<represents>> MavenirProductOffering

### **PlanRepository** <<Repository>>

Maps `PortalGateway` catalog rows to Paradise *Plan*. Midtier maps; it is not a type.

+ PlanRepository(...)
------
+ << aggregation >> plans: Collection<Plan>
+ << association >> portalGateway: PortalGateway
----
+ list(): Plan[]
	-> PortalGateway.list
	// Midtier maps
	// Get Data Freedom Upgrade uses the same list
	// Get Review Plan uses the same list
	// valid bundle ids: essentials, dataFreedom, ace, atlas, hiddenPromo
	// isBundle in live
	// isSellable when price > 0
	// hiddenPromo not sellable
	// name without the PROMO token
	// list order: price descending
	// Ace Best value is presentation

## Mavenir

### **MavenirProductOffering** <<System>> <<Entity>>

++product offering++ in the Mavenir catalog. Plan `<<represents>>` this type. No composition from Plan.

+ MavenirProductOffering(...)
------
+ id: string
+ name: string
+ isBundle: boolean
+ productOfferingPrice
+ bundledProductOffering

### **PortalGateway** <<Service>> <<System>>

Mavenir `portalGateway` catalog. `productOfferings/100000000?channelName=CRM`.

+ PortalGateway(...)
------
----
+ list(): MavenirProductOffering[]
	// always service provider 100000000
	// always channelName CRM

# Numbers and SIMs

Inventory · Number & SIM. `Line` hops here (`getNumbers` / `attachIccid` / `reserveNumber`). Selected `msisdn` / `simType` / `iccid` stay on `Line`.

## Paradise

### **MsisdnInventoryRepository** <<Repository>>

Paradise collection of ++AvailableNumber++. Mavenir builds the wrap target. List locks five resources when picking a new number (category always `standard`), or one when bringing a number; listing premium inventory category is always `premium`. Reserve moves locked to reserved and may release a previous reserved id. Premium selected id uses the same locked-to-reserved hop; `portin` is false (same as `pickNumber`). Category is on list. When `portin`, Mavenir marks the reserved resource `kv_tempNumber`.

+ MsisdnInventoryRepository(...)
------
+ << aggregation >> availableNumbers: Collection<AvailableNumber>
+ << association >> inventoryGateway: InventoryGateway
----
+ list(size: number, category: string): AvailableNumber[]
	-> InventoryGateway.list
	// always size 5 when picking a new number
	// always size 1 when bringing a number
	// new-number category always standard
	// listing premium inventory category always premium
	// always available to locked
+ search(searchTerm: SearchTerm): AvailableNumber[]
	-> InventoryGateway.search
	// when SearchTerm.converted is the pattern
	// always available to locked
+ reserve(id: string, previousId: string | null, portin: boolean): void | Error
	-> InventoryGateway.reserve
	// always locked to reserved
	// premium selected id: always locked to reserved
	// premium portin always false
	// category is always on list
	// when previousId is present, previousId must go reserved to available
	// when portin: kv_tempNumber

### **IccidInventoryRepository** <<Repository>>

Paradise collection of ++AvailableSim++. Mavenir builds the wrap target. Available only. Empty or not-available is miss. No reserve this epic.

+ IccidInventoryRepository(...)
------
+ << aggregation >> availableSims: Collection<AvailableSim>
+ << association >> inventoryGateway: InventoryGateway
----
+ read(id: string): AvailableSim | Error
	-> InventoryGateway.read
	// available only
	// empty or not-available is miss

### **AvailableNumber**

Paradise *AvailableNumber* `<<represents>>` ++MavenirMsisdnResource++.

+ AvailableNumber(...)
------
+ id: string
+ <<represents>> MavenirMsisdnResource

### **AvailableSim**

Paradise *AvailableSim* `<<represents>>` ++MavenirSimResource++.

+ AvailableSim(...)
------
+ id: string
+ <<represents>> MavenirSimResource

### **SearchTerm**

+ SearchTerm(...)
------
+ input: string
+ converted: string
----
+ convert(): string
	// when input is letters, converted is always keypad digits

## Mavenir

### **MavenirMsisdnResource** <<System>> <<Entity>>

Wrap target. ++MSISDN++ resource in Mavenir inventory.

+ MavenirMsisdnResource(...)
------
+ id: string
+ resourceStatus: string
	// always available, locked, or reserved

### **InventoryGateway** <<Service>> <<System>>

Mavenir `inventoryGateway` (`.../msisdn/resource`, `.../sim/resource`).

+ InventoryGateway(...)
------
----
+ list(size: number, category: string): MavenirMsisdnResource[]
	// always size 5 when picking a new number
	// always size 1 when bringing a number
	// new-number category always standard
	// listing premium inventory category always premium
	// always available to locked
+ search(pattern: string): MavenirMsisdnResource[]
	// always available to locked
+ reserve(id: string, previousId: string | null, portin: boolean): void | Error
	// always locked to reserved
	// premium selected id: always locked to reserved
	// premium portin always false
	// category is always on list
	// when previousId is present, previousId must go reserved to available
	// when portin: kv_tempNumber
+ read(id: string): MavenirSimResource | Error
	// GET sim resource
	// when none: none
	// when not-available: none

### **MavenirSimResource** <<System>> <<Entity>>

++SIM++ resource in Mavenir inventory.

+ MavenirSimResource(...)
------
+ id: string
+ resourceStatus: string
	// available passes

# Porting

Inventory · Porting. Cart **links** *Portability*. Details and Twilio SMS live here.

## Paradise

### **Portability** <<Aggregate Root>> <<Entity>>

Donor / account / device / verified live here. Cart **links** this type (`<< association >>`). `planSelected` is the cart bundle name.

+ Portability(...)
------
+ donorOperator: string
+ portNumber: string
+ accountNumber: string | null
+ userType: string
+ accountType: string
+ device: string
+ planSelected: string
	// always the cart bundle name
+ verified: boolean
	// false after Cart.bringNumber
	// true after Portability.verify
----
+ verify(portingSmsCode: PortingSmsCode): Portability | PortingErrors
	-> TwilioService.check
	-> PortalGateway.patchPhoneVerified
	// always Twilio check against portNumber
	// verified is always true after success
	// when Twilio is not approved: PortingErrors.portingSmsCode; verified stays false
	// when no portNumber: fails
+ resendSms(): void
	-> TwilioService.start
	// always Twilio send to portNumber
	// waits 30 seconds before another resend
	// when no portNumber: fails

### **TwilioService** <<Service>> <<System>>

Twilio Verify. Port-in SMS.

+ TwilioService(...)
------
----
+ start(portNumber: string): void
+ check(portNumber: string, portingSmsCode: PortingSmsCode): void | Error

### **PortingSmsCode** <<System>>

+ PortingSmsCode(...)
------
+ code: string

### **PortingErrors**

Commit failures after `Portability.verify`.

+ PortingErrors(...)
------
+ portingSmsCode: string | null

# Payments

Card authorisation on the cart. Nico: Payments (FAC / PowerTranz). Tokenized method, hosted iframe, Apple Pay merchant cert. Charge copy reads Cart.bundle / Cart.voucher / Cart.portability. `Cart.checkout` reads PaymentStatus. After the card is approved, `# Billing` creates the party's billing account and points `defaultPaymentMethod` at that token.

## Paradise

### **Payment** <<Aggregate Root>> <<Entity>>

+ Payment(...)
------
+ paymentAttempts: number
	// always compared to GrowthBook PAYMENT_ATTEMPTS
+ <<represents>> PaymentIframe
	// always null until enter
	// always html + transactionId after GET /customer/payment/auth
+ << composition >> paymentCharge: PaymentCharge
+ << composition >> paymentErrors: PaymentErrors
----
+ enter(cart: Cart): Payment | PaymentErrors
	-> GrowthBook.evaluate
	-> GrowthBook.value
	-> FAC.create
	// always GET /customer/payment/auth (Authorize Card)
	// always sets Payment.paymentIframe from html + transactionId
	// when PAY_UP_FRONT is off: invoicePayment title Time to add your payment; submit Checkout
	// when PAY_UP_FRONT is on: upfrontPayment title Complete your payment; submit Pay $N and subscribe
	// chargedValue is always Plan.price minus Cart.voucher discount; floor always 0
	// when flag on and no portability.portNumber and not trial voucher and chargedValue > 0: heads-up charged upfront
	// when flag on and chargedValue <= 0 and voucher discount >= 0: heads-up add credit
	// when load fails: PaymentErrors.load
	// PAYMENT_ATTEMPTS is always 3 on the scenario; live default is always 1
+ recordFailed(): Payment | PaymentErrors
	// always POST /customer/payment/failed with transactionId
	// always Then Cart.createOrder

### **PaymentErrors**

Commit failures after `Payment.enter` / `Cart.checkout` (card). Billing-account create is `# Billing` on the Customer.

+ PaymentErrors(...)
------
+ load: string | null
	// always Failed to load — It's not you, it's me. Please refresh the page.
+ unverified: string | null
	// always We are unable to verify your card at this time.
	// when attempts under PAYMENT_ATTEMPTS

### **PaymentCharge**

Invoice vs upfront copy plus charged amount. From GrowthBook `PAY_UP_FRONT` plus Cart.bundle, Cart.portability, and Cart.voucher.

+ PaymentCharge(...)
------
+ title: string
	// when invoicePayment: Time to add your payment
	// when upfrontPayment: Complete your payment
+ submit: string
	// when invoicePayment: Checkout
	// when upfrontPayment: Pay $N and subscribe
+ chargedValue: number
	// always Plan.price minus Cart.voucher discount; floor always 0
	// table submit Pay $55 is leftover copy
	// FAC SPI auth TotalAmount $1 is FAC.create, not this chargedValue

## System

### **PaymentIframe** <<System>> <<Entity>>

Wrap target. FAC hosted payment page. No Paradise types.

+ PaymentIframe(...)
------
+ html: string
+ transactionId: string

### **FAC** <<Service>> <<System>>

FAC CCS builds the ++PaymentIframe++. Midtier maps; it is not a type. POST `fac/cards/spi/auth`; GET `getTokenizedCard`.

+ FAC(...)
------
----
+ create(customer: Customer): PaymentIframe | Error
	// Request Payment Authorization
	// Authorize Card (Mavenir)
	// always GET /customer/payment/auth
	// always POST fac/cards/spi/auth
	// stubAuth fixture: transactionId, TotalAmount 1, ON-BOARDING
	// returns html + transactionId
	// FAC timeout 3s no TransactionId: Error 504
+ read(customer: Customer, transactionId: string): PaymentStatus | Error
	// Read Tokenized Card Midtier + Mavenir
	// always GET /customer/payment/status/:transactionId
	// always GET getTokenizedCard
	// completed: status completed, reason APPROVED
	// failed: status failed, reason DECLINED; Midtier 504
	// optional 15s poll is Midtier retry, not a type

### **PaymentStatus** <<System>> <<Entity>>

Outcome of a tokenized-card read. No Paradise types. No repository.

+ PaymentStatus(...)
------
+ status: string
	// completed | failed
+ reason: string
	// APPROVED | DECLINED

### **ApplePayCertificate** <<System>> <<Entity>>

Wrap target. Apple / DigiCert BM domain certificate Midtier serves. No Paradise types.

+ ApplePayCertificate(...)
------
+ keyIdentifier: string
	// bmApplePayCert serial CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b
	// live JSON wraps serial in []
+ certificate: string
	// always certificates.bm whitespace stripped

### **Apple** <<Service>> <<System>>

Midtier serves the ++ApplePayCertificate++. Apple / DigiCert builds it; Midtier is not a type. POST `/apple/cert` `getCert`.

+ Apple(...)
------
----
+ read(): ApplePayCertificate
	// Provide Apple Pay Certificate
	// always POST /apple/cert getCert
	// always certificates.bm
	// Given CognitoUser vs live unauthenticated /apple

# Billing

Mavenir **billing account** on the party (`customer.account[0]`). Payment is on the cart (`# Payments` FAC token). After the card is approved, this module creates the account and hangs the token as `defaultPaymentMethod`. Cook later stamps that account onto the Mavenir shopping cart and `productOrderFromCart` — the order is billed to the account; the account does not know Cart.

Self-care My Paradise Billing reads the same account: state, default payment, invoices, AR transactions, current balance.

## Paradise

### **Billing** <<Aggregate Root>> <<Entity>>

Paradise view of the party's billing account. Onboarding keeps `{ id, defaultPayment }`. Self-care adds state, invoices, balance, transactions. Lives on `Customer.billing`. `CustomerRepository.load` signs out when `state` is `terminated`.

+ Billing(...)
------
+ id: string
+ state: string
	// active | suspended | terminated
+ balance: string
	// currentBalance on MavenirBillingAccount.accountBalance
+ << composition >> defaultPayment
	// id, status, brand, lastFourDigits
	// Payments token after FAC; account.defaultPaymentMethod
+ << composition >> invoices: Invoice[]
+ << composition >> transactions: Transaction[]
+ <<represents>> MavenirBillingAccount
----
+ create(customer: Customer): Billing | Error
	-> PortalGateway.createBilling
	// after Payment approved
	// POST /customer/billing
	// body transactionId ignored
	// 409 when customer.account already present
	// 201 empty body
+ applyCredit(): Billing
	-> PortalGateway.applyCredit
	// posts onto this account; uses Customer, Cart voucher, and VoucherRedemption already on the graph
	// cook after Vouchera.redeem, before productOrderFromCart
	// skip when VoucherRedemption.success false
	// then appears as Transaction / ArTransaction

### **BillingRepository** <<Repository>>

Owns `Collection<Billing>`. Associates to `PortalGateway` to create and read ++MavenirBillingAccount++ and to post credit.

+ BillingRepository(...)
------
+ << aggregation >> billings: Collection<Billing>
+ << association >> portalGateway: PortalGateway
----
+ find(customer: Customer): Billing | null
	-> PortalGateway.read
	// Customer.account[0]
	// assembles invoices, transactions, defaultPayment, balance
+ create(customer: Customer): Billing | Error
	-> PortalGateway.createBilling

### **Invoice** <<Entity>>

Self-care row from `v1/invoice/history` FINAL_BILL (~6 months).

+ Invoice(...)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string
+ <<represents>> MavenirInvoice

### **Transaction** <<Entity>>

Self-care Processed AR row.

+ Transaction(...)
------
+ id: string
+ paymentDate: string
+ totalAmount: string
+ <<represents>> ArTransaction

## Mavenir

### **MavenirBillingAccount** <<System>> <<Entity>>

`v1/billingAccount`. POSTPAID party account. Create payload: ratingType POSTPAID, billCycle `1st of every month`, billingTemplate Summary, communicationMedium Email, Consumer Dunning, Primary contact from ContactMedium, defaultPaymentMethod from the FAC token already on the party. The wrap does not know Cart or Billing.

+ MavenirBillingAccount(...)
------
+ id: string
+ name: string
+ href: string
+ state: string
	// active | suspended | terminated
+ ratingType: string
	// always POSTPAID
+ billCycle: string
	// always 1st of every month
+ defaultPaymentMethod
+ relatedParty
+ accountBalance
	// currentBalance is Paradise Billing.balance
+ << composition >> creditAdjustments: MavenirCreditAdjustment[]
	// posted onto this account
	// PortalGateway.applyCredit
	// then listed as ArTransaction

### **MavenirInvoice** <<System>> <<Entity>>

`v1/invoice/history` FINAL_BILL. PDF is `v1/invoice/invoicePDF`.

+ MavenirInvoice(...)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string

### **ArTransaction** <<System>> <<Entity>>

`paymentManagement/v4/refund/allARTransaction`. Self-care lists Processed rows. Credit adjustment posts here.

+ ArTransaction(...)
------
+ id: string
+ status: string
+ totalAmount: string
+ paymentDate: string

### **MavenirCreditAdjustment** <<System>> <<Entity>>

AR credit **on the billing account**. `creditPayload.account` is that account's id / href. `PortalGateway.applyCredit` POSTs `allARTransaction` (`transactionType` creditAdjustment). Cook (voucher / pay-upfront) and later Pay Now use this. After it posts, self-care lists it as a Processed *ArTransaction* on the same account. The wrap does not know Cart.

+ MavenirCreditAdjustment(...)
------
+ amount: number
+ unit: string
	// always BMD
+ glCode: string
	// always 100004
+ transactionType: string
	// always creditAdjustment
+ transactionSubType: string
	// always Credit
+ serviceProviderId: string
	// always 100000000
+ reason: string
	// always $ + Voucher.campaign

### **PortalGateway** <<Service>> <<System>>

Billing on the Mavenir party. Party create / read / profile live in `# Customer`.

+ PortalGateway(...)
------
----
+ createBilling(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error
	// POST v1/billingAccount?customerId=
	// 409 when account already present
	// 201 no body
+ read(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error
	// GET v1/billingAccount/{accountId}
+ readInvoices(mavenirCustomer: MavenirCustomer): MavenirInvoice[]
	// GET v1/invoice/history
+ readTransactions(mavenirCustomer: MavenirCustomer): ArTransaction[]
	// GET allARTransaction
+ readInvoicePdf(billingAccountId: string, invoiceId: string)
	// GET v1/invoice/invoicePDF
+ applyCredit(mavenirCustomer: MavenirCustomer, creditAdjustment: MavenirCreditAdjustment): MavenirCreditAdjustment
	// POST allARTransaction
	// cook after Vouchera.redeem, before productOrderFromCart
	// skip when VoucherRedemption.success false

# Subscription

The billed **phone line** after the cart is placed. Everything the cart selected lands here: *Bundle*, number, SIM / ICCID, and the *Portability* link when they brought a number. The party stays on `# Customer` (`Customer.subscriptions`). Payment stays on the cart; the billing account stays on `# Billing`. `Cart.createOrder` writes *MavenirProductOrder*; cook may redeem the cart voucher and `# Billing.applyCredit` onto that account.

## Paradise

### **Line** <<Entity>>

The phone line on a Cart or Subscription. Owns number, SIM type, ICCID, and portability.

+ Line(...)
------
+ msisdn: string | null
+ simType: SimType | null
	// SimType.Esim | SimType.Psim
	// null until selectSim or attachIccid
+ iccid: string | null
	// null until attachIccid
+ availableNumbers: string[]
+ << association >> portability: Portability | null
----
+ selectSim(simType: SimType): void | Error
	-> ShoppingCartGateway.patchCartWithSim
	// when the line already has that SIM type: no patch
	// Request a Paradise SIM card: SimType.Psim, no ICCID
	// when patch fails: Error
+ attachIccid(iccid: string): void | Error
	-> MsisdnRepository.read
	-> ShoppingCartGateway.patchCartWithSim
	// always SimType.Psim
	// when whitespace: Error; no inventory or patch
	// when read miss: Error
+ activateSim(iccid: string): void | Error
	-> Line.attachIccid
	-> PortalGateway.createPsimDeliveredOrder
	// waiting pSIM must already be Active
	// absent waiting pSIM: Error
	// waiting pSIM Cleared: Error

### **Subscription** <<Aggregate Root>> <<Entity>>

Paradise view of one line. Self-care: `{ id, bundle, number, simType, status, usage }`. Onboarding thinner: `{ type, number, status }` until agreement is live. `<<represents>>` ++MavenirAgreement++ (`agreementManagement/agreement`).

+ Subscription(...)
------
+ id: string
	// MavenirAgreement.id
+ status: string
	// active | suspended | terminated | pendingActive
+ << composition >> line: Line
	// number, simType, iccid, portability live on Line
+ << composition >> bundle: Bundle
	// from Cart
	// same snapshot pickPlan wrote
	// agreementItem.product / productOffering
+ << composition >> usage: Usage
+ << association >> portability: Portability | null
	// from Porting
	// from Cart.portability when they brought a number
+ << association >> productOrder: MavenirProductOrder | null
	// Cart.createOrder / PortalGateway.createProductOrder
+ << association >> voucherRedemption: VoucherRedemption | null
	// cook: Vouchera.redeem on Cart.voucher
+ <<represents>> MavenirAgreement
----
+ changePlan(plan: Plan): Subscription | Error
	-> PortalGateway.changePlan

### **Usage** <<Entity>>

Local / roaming data on the line. Loaded with the subscription (`getUsageRequest`).

+ Usage(...)
------
+ local.used: number
+ local.quota: number | null
+ roaming.used: number
+ roaming.quota: number | null
+ <<represents>> MsisdnDataUsage

### **SubscriptionRepository** <<Repository>>

Owns `Collection<Subscription>`. Associates to `PortalGateway` for agreements / product order. Associates to `CcsGateway` for usage.

+ SubscriptionRepository(...)
------
+ << aggregation >> subscriptions: Collection<Subscription>
+ << association >> portalGateway: PortalGateway
+ << association >> ccsGateway: CcsGateway
----
+ list(customer: Customer): Subscription[]
	-> PortalGateway.listAgreements
	-> CcsGateway.readUsage
	// sets Customer.subscriptions
	// active and suspended
	// bundle from latest agreementItem.product
	// number / simType from characteristics

## Mavenir

### **MavenirAgreement** <<System>> <<Entity>>

`agreementManagement/agreement?customerId=&productValues=true`. The wrap does not know Subscription.

+ MavenirAgreement(...)
------
+ id: string
+ status: string
+ agreementType: string
+ initialDate: string
+ characteristic
	// MSISDN, SIM_TYPE
+ << composition >> agreementItem: MavenirAgreementProduct[]

### **MavenirAgreementProduct** <<System>> <<Entity>>

Product on the agreement. Latest `orderDate` is Paradise *Bundle* (`productOffering.id` is Plan.id).

+ MavenirAgreementProduct(...)
------
+ id: string
+ name: string
+ description: string
+ orderDate
+ productOffering.id: string
+ productPrice

### **MavenirProductOrder** <<System>> <<Entity>>

Cook: PATCH shoppingCart with billingAccount then `POST v2/productOrderFromCart`. Created by `Cart.createOrder`. Lives with the line after cook. The wrap does not know Cart.

+ MavenirProductOrder(...)
------
+ id: string

### **MsisdnDataUsage** <<System>> <<Entity>>

CCS `subscriber/serviceUsage/.../subscribers/{msisdn}`.

+ MsisdnDataUsage(...)
------
+ subscriptions.activeSubscriptions

### **PortalGateway** <<Service>> <<System>>

Agreements and product order on the Mavenir party. Party create / read / profile live in `# Customer`. Billing commits live in `# Billing`. Cart shopping-cart slice lives in `# Cart`.

+ PortalGateway(...)
------
----
+ listAgreements(mavenirCustomerId: string): MavenirAgreement[]
	// GET agreementManagement/agreement
+ createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error
	-> GrowthBook.evaluate
	-> Vouchera.redeem
	-> Billing.applyCredit
	-> PortalGateway.createProductOrder
	-> PortalGateway.patchSubmitOrder
	-> patchDone
	-> patchWaitingPsim
	// Create Product Order
	// always POST /customer/order
	// no body
	// 409 when done is truthy
	// when verified or portability or Plan.bypassVerified: cook
	// when cook: Vouchera.redeem then Billing.applyCredit then productOrderFromCart
	// when unverified no bypass no portability: patchSubmitOrder
	// always patchDone
	// waitingPsim true when pSIM no iccid
	// 201 { payUpFront, verified }
+ changePlan(mavenirCustomerId: string, plan: Plan): MavenirAgreement | Error

### **CcsGateway** <<Service>> <<System>>

Usage on the MSISDN. Midtier maps; it is not a type.

+ CcsGateway(...)
------
----
+ readUsage(msisdn: string, planName: string): MsisdnDataUsage
	// GET ccsGateway/subscriber/serviceUsage/.../subscribers/{msisdn}

## System

### **VoucherRedemption** <<System>> <<Entity>>

Vouchera redeem at cook. Written on Subscription. Cart.voucher is the code.

+ VoucherRedemption(...)
------
+ success: boolean
	// flagged 5xx: false; cook continues
+ discountAmount: number
+ totalAmount: number

# Care

Cases, Zendesk tickets, Persona inquiry, and Persona documents. Confirm-ID catalog stays in `# KYC`. Requester is the Customer (name + email); a Case is not a property of Customer. `Cart.createOrder` hops `CaseRepository.open`. Messenger / Help Center stay unfilled.

## Paradise

### **Case** <<Aggregate Root>> <<Entity>>

Paradise *Case* `<<represents>>` a Zendesk ++Ticket++. One subject per open. Not stored on the Customer session.

+ Case(...)
------
+ subject: string
	// GWT seven: ID Verification Required | SIM Delivery Required | ID Verification Required and SIM Delivery Required | Promotional trial | Portability Required | Payment failed | Roaming plan - New Subscription
	// cardAdditionFailed config out of GWT
+ <<represents>> Ticket

### **CaseRepository** <<Repository>>

+ CaseRepository(...)
------
+ << aggregation >> cases: Collection<Case>
+ << association >> zendesk: Zendesk
----
+ open(customer: Customer, subject: string): Case
	-> Zendesk.create
	// Create Order Ticket
	// requesterName Identity.fullName
	// requesterEmail Identity.email

## System

### **Ticket** <<System>> <<Entity>>

Wrap target. Zendesk ++Ticket++. No Paradise types.

+ Ticket(...)
------
+ id: string
+ subject: string
+ requesterName: string
	// Identity.fullName
+ requesterEmail: string
	// Identity.email

### **Zendesk** <<Service>> <<System>>

Zendesk builds the ++Ticket++. Midtier maps; it is not a type. POST tickets.json.

+ Zendesk(...)
------
----
+ create(customer: Customer, subject: string): Ticket
	// always POST tickets.json
	// seven GWT subjects
	// trial may also create id / pSim / idAndPsim
	// cardAdditionFailed config out of GWT
	// requesterName Identity.fullName
	// requesterEmail Identity.email

### **PersonaInquiry** <<System>> <<Entity>>

Wrap target. Persona inquiry. Care owns the inquiry record. KYC `ProfileRequirements.mapInquiry` writes Identity / Address.

+ PersonaInquiry(...)
------
+ inquiryId: string
+ status: string
+ verified: boolean
+ email: string
+ nameFirst: string
+ nameLast: string
+ birthdate: string
+ selectedCountryCode: string
+ identificationNumber: string
+ identificationClass: string
+ expiryDate: string
+ addressStreet1: string
+ addressStreet2: string
+ addressCity: string
+ addressSubdivision: string
+ addressPostalCode: string
+ addressCountryCode: string
+ currentGovernmentId: string | null

### **PersonaDocument** <<System>> <<Entity>>

Wrap target. Persona government-id document. Care owns the document. KYC reads expiry onto Identity.

+ PersonaDocument(...)
------
+ documentId: string
+ expirationDate: string
+ email: string

### **PersonaService** <<Service>> <<System>>

Persona builds the ++PersonaInquiry++. Midtier maps; it is not a type.

+ PersonaService(...)
------
----
+ create(customer: Customer): PersonaInquiry
	// wraps a Persona inquiry with inquiryId + status + fields
	// email pre-filled from Customer.identity.email
	// create failed: status failed, verified false
	// Verify Later: create is not called
+ readDocument(documentId: string): PersonaDocument | Error
	// missing document: not found
	// email mismatch: unauthorized
